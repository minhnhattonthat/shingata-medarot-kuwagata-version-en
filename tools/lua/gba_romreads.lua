-- gba_romreads.lua: per PC, the lowest/highest ROM address it reads (data reads) in frames FROM..TO.
-- --var FROM=1800 --var TO=2400 ; optional --var LO=0x08000000 --var HI=0x08800000
-- Log line: "PC <pc> lo <addr> hi <addr> n <count>" (ROM offsets = addr - 0x08000000).
local from, to = FROM or 0, TO or 1e9
local lo, hi = LO or 0x08000000, HI or 0x08800000
local stat = {}
L.on_read(lo, hi, function(addr)
  if L.frame < from or L.frame > to then return end
  local pc = L.pc()
  local s = stat[pc]
  if not s then stat[pc] = { addr, addr, 1 } else
    if addr < s[1] then s[1] = addr end
    if addr > s[2] then s[2] = addr end
    s[3] = s[3] + 1
  end
end)
L.on_frame(function(n)
  if n == to then
    for pc, s in pairs(stat) do
      L.log(string.format("PC %08X lo %08X hi %08X n %d", pc, s[1], s[2], s[3]))
    end
  end
end)
