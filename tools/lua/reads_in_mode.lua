-- Log every distinct (pc, address) read of IWRAM+EWRAM while main mode/sub equal RMODE/RSUB (docs/re/debug.md).
--   emu.py ROM --state-in S --script tools/debug/warp.lua --var "SCENE='medal_list'" --script tools/lua/reads_in_mode.lua
--          --var RMODE=0 --var RSUB=4 [--var RLO=0x03000000 --var RHI=0x03007FFF] [--var RPCLO=0x08010000 RPCHI=..]
-- (stack reads at 0x03007000+ are skipped; RPCLO/RPCHI keep only reads made by code in that range)
-- Lines: "R pc addr value". Use it to find which RAM a screen reads (inventory, counts).
local mem = emu.memType.gbaMemory
local seen, n = {}, 0
local function hit(addr, value)
  if emu.read32(0x0300177C, mem) ~= RMODE or (RSUB and emu.read32(0x03001D6C, mem) ~= RSUB)
    or (RSTEP and emu.read32(0x03001364, mem) < RSTEP) then return end -- RSTEP: only from that step on
  local pc = L.pc()
  if pc < (RPCLO or 0) or pc > (RPCHI or 0xFFFFFFFF) or addr >= 0x03007000 then return end
  if RXLO and addr >= RXLO and addr <= RXHI then return end -- RXLO/RXHI: an address range to skip
  local key = pc * 0x100000 + (addr & 0xFFFFF)
  if seen[key] or n > (RMAX or 20000) then return end
  seen[key] = true; n = n + 1
  L.log(string.format("R %08X %08X %02X", pc, addr, value or 0))
end
L.on_read(RLO or 0x03000000, RHI or 0x03007FFF, hit)
if not RLO then L.on_read(0x02000000, 0x0203FFFF, hit) end
