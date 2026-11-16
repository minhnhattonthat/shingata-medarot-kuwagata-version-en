-- Trace the field event interpreter (docs/re/debug.md §Events): one line per command dispatched.
--   emu.py ROM --state-in S --script tools/lua/evtrace.lua [--route-str ...]
-- Byte fetch 0x080505E8: bank = *(0x03004660), event index u16 +0x9A6 (0x03005256), pc u16 +0x9A2 (0x03005252).
-- Dispatch: command byte at +0x9AA (0x0300525A) through table 0x0847B160 (bl 0x0808B984 at 0x080502A6/0x08050308/
-- 0x0804D63C). Lines: "EV f<n> bank=<ptr> ev=<idx> pc=<off> cmd=<xx> map=<id>".
local mem = emu.memType.gbaMemory
local function ev(tag)
  return function()
    L.log(string.format("EV f%d %s bank=%08X ev=%04X pc=%04X cmd=%02X map=%d", L.frame, tag,
      emu.read32(0x03004660, mem), emu.read16(0x03005256, mem), emu.read16(0x03005252, mem),
      emu.read(0x0300525A, mem), emu.read(0x03004DC6, mem)))
  end
end
-- EVTRACE_BYTES=1: also log the address of every script byte fetched (ldrb at 0x08050650, r5)
if EVTRACE_BYTES then
  L.on_exec(0x08050650, 0x08050650, function()
    local a = emu.getState()["cpu.r5"]
    L.log(string.format("SB f%d %08X %02X", L.frame, a, emu.read(a, mem)))
  end)
end
L.on_exec(0x080502A6, 0x080502A6, ev("a"))
L.on_exec(0x08050308, 0x08050308, ev("b"))
L.on_exec(0x0804D63C, 0x0804D63C, ev("c"))
