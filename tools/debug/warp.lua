-- Debug warp for Shingata Medarot Kuwagata (GBA). RAM map and evidence: docs/re/debug.md.
--   emu.py ROM --out DIR --script tools/debug/warp.lua --var "SCENE='town'" --frames 900 --sheet
-- Globals (--var):
--   SCENE='name'     an entry of tools/debug/scenes.txt (SCENES='abs path' overrides the file)
--   MAP=n [X= Y= DIR=]                       ad-hoc field warp (tile coords)
--   RAWMODE=n [RAWSUB= RAWSTEP= RAWEXTRA={[addr]=byte}]   ad-hoc main-mode switch
--   EVENT=n [EVPC=pc]  start story event n (0..687, work/re/events.txt) on the start map, A mashed; HOLD= frames
--   HOLD=n           frames to keep running after arrival before logging ARRIVED (default 120)
--   NOENC=1          no random robattles; AFTER_MASH=n press A every n frames after arrival
--   STOP=1 [SAVE='abs.mss']   end the run at ARRIVED (after saving a state): tools/debug/prove.py
-- Scene key events={{ev, pc}, ...} runs those field events first (WARP.event), e.g. the story's first medal
-- and first Medabot; then the rest of the scene applies. Key run={ev, pc} starts one event as the scene's own
-- trigger (no wait for its end: pair it with wait=). Key wait={mode=,sub=,step=} delays arrival (and the
-- hold count) until main mode/sub/step reach those values (step: at least), for screens deep inside a robattle.
-- Without --state-in the script boots cold: new game, mash A through the intro until the field is idle,
-- then applies the scene. With --state-in it waits for the field to be idle (or applies at once for NOW=1).
-- The log gets "FIELD f<n>" when the field is reached and "ARRIVED <scene> f<n>" when the scene is up.
local mem = emu.memType.gbaMemory
local function rd(a) return emu.read(a, mem) end
local function wr(a, v) emu.write(a, v, mem) end
local function rd32(a) return emu.read32(a, mem) end
local function wr32(a, v) emu.write32(a, v, mem) end
local function setreg(r, v) local t = {}; t["cpu.r" .. r] = v; emu.setState(t) end
local function reg(r) return emu.getState()["cpu.r" .. r] end

local MODE, SUBM, STEP = 0x0300177C, 0x03001D6C, 0x03001364
local FSUB = 0x030043E1 -- field substate: 2 = idle, 4 = run door warp

WARP = { pending = false }

-- 0x03004268 = 1 while the field input routine 0x08056C38 runs (player has control; 0 during events)
function WARP.field_idle() return rd32(MODE) == 1 and rd(FSUB) == 2 and rd(0x03004268) == 1 end

-- Field warp: substate 4 runs the door-warp routine 0x08057E14 on the player's tile; force its first entry
-- to match and swap in the destination at the loads, so the game's own map loader runs.
function WARP.go(map, x, y, dir)
  WARP.dest = { map = map, x = x or 5, y = y or 5, dir = dir or 0 }
  WARP.pending = true
  wr(FSUB, 4)
end
L.on_exec(0x08057E50, 0x08057E50, function() if WARP.pending then setreg(3, reg(0)) end end)
L.on_exec(0x08057E5A, 0x08057E5A, function() if WARP.pending then setreg(3, reg(1)) end end)
L.on_exec(0x08057E64, 0x08057E64, function() if WARP.pending then setreg(1, WARP.dest.map) end end)
L.on_exec(0x08057E6E, 0x08057E6E, function() if WARP.pending then setreg(1, WARP.dest.dir) end end)
L.on_exec(0x08057E78, 0x08057E78, function() if WARP.pending then setreg(0, WARP.dest.x) end end)
L.on_exec(0x08057E8A, 0x08057E8A, function()
  if WARP.pending then
    setreg(0, WARP.dest.y); WARP.pending = false
    L.log(string.format("warp f%d -> map %d (%d,%d)", L.frame, WARP.dest.map, WARP.dest.x, WARP.dest.y))
  end
end)

-- Run field event `ev` from byte offset `pc` through the game's own interpreter: the same stores the tile
-- trigger 0x080573A4 makes; mode 1 sub 1 (0x0804C088) dispatches while +0x9A0 (0x03005250) is set.
function WARP.event(ev, pc)
  wr(0x03005250, 1); emu.write16(0x03005256, ev, mem); emu.write16(0x03005258, ev, mem)
  wr(0x03005251, 0); emu.write16(0x03005252, pc or 0, mem); wr(0x0300527C, 0); wr(0x030029C5, 1)
  L.log(string.format("event f%d 0x%X pc %d", L.frame, ev, pc or 0))
end
function WARP.event_running() return rd(0x03005250) ~= 0 end

-- Main-mode switch: the same stores a case of the scene switch 0x0804908C makes.
function WARP.switch(mode, sub, step, extra)
  for a, v in pairs(extra or {}) do wr(a, v) end
  wr32(MODE, mode); wr32(SUBM, sub or 0); wr32(STEP, step or 0)
  L.log(string.format("switch f%d mode=%d sub=%d step=%d", L.frame, mode, sub or 0, step or 0))
end

-- Scene list: "name<TAB>{lua table}<TAB>description"; '#' comments.
local function load_scenes(path)
  local t = {}
  local f = io.open(path, "r")
  if not f then return t end
  for line in f:lines() do
    local name, spec = line:match("^([%w_]+)\t+(%b{})")
    if name then t[name] = assert(load("return " .. spec))() end
  end
  f:close()
  return t
end

local spec
if SCENE then
  local scenes = load_scenes(SCENES or "../debug/scenes.txt")
  spec = assert(scenes[SCENE], "unknown SCENE " .. tostring(SCENE))
elseif MAP then
  spec = { map = MAP, x = X, y = Y, dir = DIR }
elseif EVENT then -- any story event, its text mashed through (the map stays the start map: actors may be missing)
  spec = { run = { EVENT, EVPC or 0 }, mash = 30 }
elseif RAWMODE then
  spec = { mode = RAWMODE, sub = RAWSUB, step = RAWSTEP, extra = RAWEXTRA }
end

-- Writes applied every frame from arrival on (god mode style pins): spec.pin = {[addr]=byte}
local function apply(s)
  for a, v in pairs(s.poke or {}) do -- poke={[addr]=byte or "hex bytes"}
    if type(v) == "string" then
      local i = 0
      for h in v:gmatch("%x%x") do wr(a + i, tonumber(h, 16)); i = i + 1 end
    else wr(a, v) end
  end
  MASH = s.mash or AFTER_MASH or 0 -- keep pressing A every N frames after arrival (cutscenes)
  if s.map then WARP.go(s.map, s.x, s.y, s.dir)
  elseif s.mode then WARP.switch(s.mode, s.sub, s.step, s.extra)
  elseif s.run then WARP.event(s.run[1], s.run[2]) end -- run={ev,pc}: start an event, arrive via wait=
  if s.press then for step in s.press:gmatch("[^;]+") do
    local n, b = step:match("^%s*(%d+)%s+(%S+)%s*$"); L.press(b, tonumber(n)) end end
end

local cold = not STATE_IN
local idle, phase, at, evi = 0, "boot", 0, 0
if cold then
  -- new game from the title (tools/routes/newgame.txt), then A through name entry and the intro
  for _, s in ipairs({ { "-", 600 }, { "start", 4 }, { "-", 200 }, { "start", 4 }, { "-", 300 }, { "up", 6 },
    { "-", 40 }, { "a", 6 }, { "-", 300 } }) do L.press(s[1], s[2]) end
end
L.on_frame(function(f)
  if phase == "boot" then
    if cold and L.route_done() then MASH = 40 end
    if WARP.field_idle() then idle = idle + 1 else idle = 0 end
    if idle >= 30 or (NOW and not cold) then
      MASH = 0
      L.log(string.format("FIELD f%d", f))
      if not spec then phase = "done"; return end
      phase, at = "wait", f + 10
      if spec.events then phase, evi, idle = "events", 0, 0 end
    end
  elseif phase == "events" then
    -- spec.events = {{ev, pc}, ...}: run each story event to its end (A mashed through its text), one by one
    if WARP.event_running() then MASH, idle = 30, 0
    else
      MASH = 0
      if WARP.field_idle() then idle = idle + 1 else idle = 0 end
      if idle >= 20 then
        evi, idle = evi + 1, 0
        local e = spec.events[evi]
        if e then WARP.event(e[1], e[2]) else phase, at = "wait", f + 10 end
      end
    end
  elseif phase == "wait" and f >= at and L.route_done() then
    apply(spec); phase, at = "arrive", f
  elseif phase == "arrive" and spec.wait and not WARP.waited then
    -- spec.wait = {mode=, sub=, step=}: arrival counts from the first frame those hold (step = at least)
    local w = spec.wait
    if (not w.mode or rd32(MODE) == w.mode) and (not w.sub or rd32(SUBM) == w.sub)
      and (not w.step or rd32(STEP) >= w.step) then WARP.waited = true; at = f end
  elseif phase == "arrive" and not WARP.pending and L.route_done() and f - at >= (spec.hold or HOLD or 120) then
    -- spec.expect = {[addr]=byte, ...} (and expect_mode/expect_sub): the RAM that proves the scene; a mismatch
    -- logs NOTARRIVED instead, so prove.py fails rather than saving a state of the wrong screen.
    local bad = {}
    for a, v in pairs(spec.expect or {}) do if rd(a) ~= v then bad[#bad + 1] = string.format("%08X=%02X", a, rd(a)) end end
    if spec.expect_mode and rd32(MODE) ~= spec.expect_mode then bad[#bad + 1] = "mode=" .. rd32(MODE) end
    if spec.expect_sub and rd32(SUBM) ~= spec.expect_sub then bad[#bad + 1] = "sub=" .. rd32(SUBM) end
    L.log(string.format("%s %s f%d mode=%d sub=%d map=%d %s", #bad == 0 and "ARRIVED" or "NOTARRIVED", SCENE or "adhoc",
      f, rd32(MODE), rd32(SUBM), rd(0x03004DC6), table.concat(bad, " ")))
    phase = "done"
    L.shot("arrived.png")
    -- STOP=1: end the run here (prove.py); SAVE='abs path.mss' saves a state first
    if SAVE then L.save_state(SAVE, function() if STOP then L.finish(0) end end)
    elseif STOP then L.finish(0) end
  end
  if phase ~= "boot" and spec and spec.pin then for a, v in pairs(spec.pin) do wr(a, v) end end
  if NOENC then wr(0x030051F1, 0) end -- field +0x941: random robattles off (docs/re/debug.md)
end)
