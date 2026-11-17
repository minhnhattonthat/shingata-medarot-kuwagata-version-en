-- Log writes to a RAM range (default the yes/no window template 0x02030024..+0xC0) with frame, pc, value and r0-r14:
--   emu.py ROM --script tools/debug/warp.lua --var "SCENE='save'" --script tools/lua/ramwho.lua --var LO=0x02030024 --var HI=0x020300E4
-- One line per (pc, frame): "rw f<frame> pc=<pc> a=<addr> v=<value> r0=.. r14=..". Finds who builds a table in RAM.
local lo, hi = LO or 0x02030024, HI or 0x020300E4
local seen = {}
L.on_write(lo, hi, function(a, v)
  local pc = L.pc()
  local key = pc .. ":" .. L.frame
  if seen[key] then return end
  seen[key] = true
  local s = emu.getState()
  local r = {}
  for i = 0, 14 do r[#r + 1] = string.format("r%d=%08X", i, s["cpu.r" .. i]) end
  L.log(string.format("rw f%d pc=%08X a=%08X v=%X %s", L.frame, pc, a, v, table.concat(r, " ")))
end)
