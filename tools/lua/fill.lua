-- Fill a RAM range with a byte on frame FILL_AT (default 2): probing what a screen reads.
--   emu.py ROM --state-in S --script tools/lua/fill.lua --var FILL_LO=0x03004AB0 --var FILL_HI=0x03004DBF --var FILL_V=1
--          [--script tools/debug/warp.lua --var "SCENE='parts_list'"]
local mem = emu.memType.gbaMemory
L.on_frame(function(f)
  if f == (FILL_AT or 2) then
    for a = FILL_LO, FILL_HI do emu.write(a, FILL_V or 1, mem) end
    L.log(string.format("fill %08X-%08X = %02X", FILL_LO, FILL_HI, FILL_V or 1))
  end
end)
