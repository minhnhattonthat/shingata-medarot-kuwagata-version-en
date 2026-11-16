-- Log DMA3 transfers to the EEPROM (dest 0x0Dxxxxxx): PC, source, and the caller chain (lr).
--   emu.py ROM --state-in work/states/save.mss --route-str "30 -;6 up;30 -;6 a;400 -" --script tools/lua/dma_eeprom.lua
local mem = emu.memType.gbaMemory
local seen = {}
L.on_write(0x040000D4, 0x040000DF, function(addr, value)
  local dad = emu.read32(0x040000D8, mem)
  if (dad >> 24) ~= 0x0D then return end
  local st = emu.getState()
  local key = string.format("%08X %08X", L.pc(), st["cpu.r14"] or 0)
  if seen[key] then return end
  seen[key] = true
  L.log(string.format("f%d pc=%08X lr=%08X sad=%08X dad=%08X r0=%08X r1=%08X r4=%08X r5=%08X sp=%08X", L.frame, L.pc(),
    st["cpu.r14"] or 0, emu.read32(0x040000D4, mem), dad, st["cpu.r0"] or 0, st["cpu.r1"] or 0, st["cpu.r4"] or 0,
    st["cpu.r5"] or 0, st["cpu.r13"] or 0))
end)
