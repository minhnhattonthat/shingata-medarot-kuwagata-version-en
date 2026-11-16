-- Log main mode / sub / step whenever they change (docs/re/debug.md): "M f<frame> mode sub step".
local mem = emu.memType.gbaMemory
local last = ""
L.on_frame(function(f)
  local s = string.format("%d %d %d", emu.read32(0x0300177C, mem), emu.read32(0x03001D6C, mem), emu.read32(0x03001364, mem))
  if s ~= last then L.log(string.format("M f%d %s", f, s)); last = s end
  if PCEVERY and f % PCEVERY == 0 then -- PCEVERY=n: also log pc/lr every n frames (find a hang)
    local st = emu.getState()
    L.log(string.format("P f%d pc=%08X lr=%08X", f, L.pc(), st["cpu.r14"] or 0))
  end
end)
