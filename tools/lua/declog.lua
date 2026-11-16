-- Log every decompressor call (Le entry 0x080009DC, BIOS LZ77 SWI entries) with source and destination:
--   emu.py ROM --script tools/debug/warp.lua --var "SCENE='x'" --script tools/lua/declog.lua [--var DST_LO=0x06000000]
-- One line per (src, dst) pair: "dec f<frame> le src=08xxxxxx dst=06xxxxxx". Find which block feeds a VRAM range.
local lo = DST_LO or 0
local hi = DST_HI or 0xFFFFFFFF
local seen = {}
local function reg(n)
  return emu.getState()["cpu.r" .. n]
end
local function hit(kind)
  return function()
    local src, dst = reg(0), reg(1)
    if dst < lo or dst > hi then return end
    local key = string.format("%s %08X %08X", kind, src, dst)
    if seen[key] then return end
    seen[key] = true
    L.log(string.format("dec f%d %s src=%08X dst=%08X lr=%08X", L.frame, kind, src, dst, reg(14)))
  end
end
L.on_exec(0x080009DC, 0x080009DC, hit("le"))
