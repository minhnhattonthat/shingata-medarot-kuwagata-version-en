-- Log writes to WLO..WHI (default one byte at WLO) with pc and r0-r3: follow a value back to its source.
--   emu.py ROM --state-in S --script tools/debug/warp.lua --var NOW=1 --var RAWMODE=0 --var RAWSUB=4
--          --script tools/lua/writes.lua --var WLO=0x030005C6 [--var WHI=0x030005CC] [--var WMAX=200]
-- Lines: "W frame pc addr value r0-r4 lr".
local n = 0
L.on_write(WLO, WHI or WLO, function(addr, value)
  if n >= (WMAX or 200) then return end
  n = n + 1
  local s = emu.getState()
  L.log(string.format("W f%d %08X %08X %X r0=%08X r1=%08X r2=%08X r3=%08X r4=%08X lr=%08X", L.frame, L.pc(), addr,
    value or 0, s["cpu.r0"], s["cpu.r1"], s["cpu.r2"], s["cpu.r3"], s["cpu.r4"], s["cpu.r14"]))
end)
