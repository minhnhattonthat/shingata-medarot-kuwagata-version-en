-- Debug warp for Shingata Medarot Kuwagata (GBA). RAM map and evidence: docs/re/debug.md.
--   emu.py ROM --out DIR --script tools/debug/warp.lua --var "SCENE='town'" --frames 900 --sheet
-- Globals (--var):
--   SCENE='name'     an entry of tools/debug/scenes.txt (SCENES='abs path' overrides the file)
--   MAP=n [X= Y= DIR=]                       ad-hoc field warp (tile coords)
--   RAWMODE=n [RAWSUB= RAWSTEP= RAWEXTRA={[addr]=byte}]   ad-hoc main-mode switch
--   HOLD=n           frames to keep running after arrival before logging ARRIVED (default 120)
--   NOENC=1          no random robattles; AFTER_MASH=n press A every n frames after arrival
--   STOP=1 [SAVE='abs.mss']   end the run at ARRIVED (after saving a state): tools/debug/prove.py
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
elseif RAWMODE then
  spec = { mode = RAWMODE, sub = RAWSUB, step = RAWSTEP, extra = RAWEXTRA }
end

-- Writes applied every frame from arrival on (god mode style pins): spec.pin = {[addr]=byte}
local function apply(s)
  for a, v in pairs(s.poke or {}) do wr(a, v) end
  MASH = s.mash or AFTER_MASH or 0 -- keep pressing A every N frames after arrival (cutscenes)
  if s.map then WARP.go(s.map, s.x, s.y, s.dir)
  elseif s.mode then WARP.switch(s.mode, s.sub, s.step, s.extra) end
  if s.press then for step in s.press:gmatch("[^;]+") do
    local n, b = step:match("^%s*(%d+)%s+(%S+)%s*$"); L.press(b, tonumber(n)) end end
end

local cold = not STATE_IN
local idle, phase, at = 0, "boot", 0
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
    end
  elseif phase == "wait" and f >= at and L.route_done() then
    apply(spec); phase, at = "arrive", f
  elseif phase == "arrive" and not WARP.pending and L.route_done() and f - at >= (spec.hold or HOLD or 120) then
    L.log(string.format("ARRIVED %s f%d mode=%d sub=%d map=%d", SCENE or "adhoc", f, rd32(MODE), rd32(SUBM), rd(0x03004DC6)))
    phase = "done"
    L.shot("arrived.png")
    -- STOP=1: end the run here (prove.py); SAVE='abs path.mss' saves a state first
    if SAVE then L.save_state(SAVE, function() if STOP then L.finish(0) end end)
    elseif STOP then L.finish(0) end
  end
  if phase ~= "boot" and spec and spec.pin then for a, v in pairs(spec.pin) do wr(a, v) end end
  if NOENC then wr(0x030051F1, 0) end -- field +0x941: random robattles off (docs/re/debug.md)
end)
