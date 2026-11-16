-- Log every write to one VRAM address (default 0x06001800) with frame, pc and r0-r14, to find the decompressor call
-- (and its source pointer) that fills a tile range:
--   emu.py ROM --script tools/debug/warp.lua --var "SCENE='x'" --script tools/lua/vramwho.lua --var ADDR=0x06001800
local addr = ADDR or 0x06001800
local last = -1
L.on_write(addr, addr + 1, function(a, v)
  if L.frame == last then return end
  last = L.frame
  local s = emu.getState()
  local r = {}
  for i = 0, 14 do r[#r + 1] = string.format("r%d=%08X", i, s["cpu.r" .. i]) end
  L.log(string.format("vw f%d pc=%08X v=%X %s", L.frame, L.pc(), v, table.concat(r, " ")))
end)
