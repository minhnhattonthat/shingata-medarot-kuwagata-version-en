-- Dump a RAM range as hex lines at frame DUMP_AT (default 2), then finish: diff two states' dumps with diff/python.
--   emu.py ROM --state-in S --script tools/lua/dumpblock.lua [--var DUMP_LO=0x030048B0 --var DUMP_HI=0x03005287]
-- Lines: "H addr 32 hex bytes". Default range = the saved field block (docs/re/debug.md §Save block).
local mem = emu.memType.gbaMemory
L.on_frame(function(f)
  if f ~= (DUMP_AT or 2) then return end
  local lo, hi = DUMP_LO or 0x030048B0, DUMP_HI or 0x03005287
  for a = lo, hi, 32 do
    local t = {}
    for i = 0, 31 do if a + i <= hi then t[#t + 1] = string.format("%02X", emu.read(a + i, mem)) end end
    L.log(string.format("H %08X %s", a, table.concat(t)))
  end
  L.finish(0)
end)
