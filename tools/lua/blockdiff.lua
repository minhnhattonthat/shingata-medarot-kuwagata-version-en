-- Log every byte of the saved field block (0x030048B0-0x03005287) and EWRAM/IWRAM ranges that changes,
-- between a snapshot at frame DIFF_FROM (default 5) and every DIFF_EVERY frames after (default 300).
--   emu.py ROM --state-in S --script tools/lua/blockdiff.lua [--var DIFF_LO=0x030048B0 --var DIFF_HI=0x03005287]
-- Lines: "D f<frame> mode=m sub=s addr old->new" (one line per changed byte per checkpoint, vs the last checkpoint).
local mem = emu.memType.gbaMemory
local LO, HI = DIFF_LO or 0x030048B0, DIFF_HI or 0x03005287
local snap
local function take()
  local t = {}
  for a = LO, HI do t[a] = emu.read(a, mem) end
  return t
end
L.on_frame(function(f)
  if f == (DIFF_FROM or 5) then snap = take()
  elseif snap and (f - (DIFF_FROM or 5)) % (DIFF_EVERY or 300) == 0 then
    local now = take()
    local mode, sub = emu.read32(0x0300177C, mem), emu.read32(0x03001D6C, mem)
    for a = LO, HI do
      if now[a] ~= snap[a] then
        L.log(string.format("D f%d mode=%d sub=%d %08X %02X->%02X", f, mode, sub, a, snap[a], now[a]))
      end
    end
    snap = now
  end
end)
