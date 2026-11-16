-- Story helper: from a state, run the route (--route-str), then press A every MASH_N frames (default 20) until the
-- field is idle (player control) for 40 frames; then shot "idle.png", save SAVE='abs.mss' and finish.
--   emu.py ROM --state-in S --script tools/lua/mash_idle.lua --var "STEPS='60 left'" --var "SAVE='C:/.../x.mss'"
-- Field idle test as in tools/debug/warp.lua (docs/re/debug.md). Logs "IDLE f<n> map=<id> x y" and mode changes.
local mem = emu.memType.gbaMemory
local function rd(a) return emu.read(a, mem) end
local idle, lastmode, done = 0, -1, false
-- STEPS='48 down;80 right': presses first (same syntax as emu.py --route-str; ROUTE is taken by emu.py)
for step in (STEPS or ""):gmatch("[^;]+") do
  local n, b = step:match("^%s*(%d+)%s+(%S+)%s*$"); if n then L.press(b, tonumber(n)) end
end
local lastptr = 0
L.on_frame(function(f)
  -- dialogue runner 0x03000520: +8 string base, +0xC read offset (docs/re/text.md); log each new string start
  local base = emu.read32(0x03000528, mem)
  if base ~= lastptr and base >= 0x08000000 and base < 0x0A000000 then
    L.log(string.format("TXT f%d %08X", f, base)); lastptr = base
  end
  if done or not L.route_done() or f < (MASH_FROM or 10) then return end
  local mode = emu.read32(0x0300177C, mem)
  local sub = emu.read32(0x03001D6C, mem)
  if mode * 256 + sub ~= lastmode then
    L.log(string.format("mode f%d %d/%d map=%d", f, mode, sub, rd(0x03004DC6))); lastmode = mode * 256 + sub
  end
  if mode == 1 and rd(0x030043E1) == 2 and rd(0x03004268) == 1 then idle = idle + 1 else idle = 0 end
  if idle >= 40 then
    done = true
    L.log(string.format("IDLE f%d map=%d x=%d y=%d", f, rd(0x03004DC6), rd(0x0300521E), rd(0x0300521F)))
    L.shot("idle.png")
    if SAVE then L.save_state(SAVE, function() L.finish(0) end) else L.finish(0) end
  elseif idle == 0 and f % (MASH_N or 20) == 0 then -- never press while in control (A would talk again)
    L.press(MASH_BTN or "a", 4)
  end
end)
