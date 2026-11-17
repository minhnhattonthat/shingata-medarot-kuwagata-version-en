-- Text sweep: every dialogue start shows the next string of LIST instead of the game's own (tools/debug/sweep.py).
--   emu.py ROM --script tools/debug/warp.lua --var "EVENTS='..'" --script tools/lua/sweep.lua --var "LIST='C:/abs/list.txt'"
-- 0x08040F6C(r0 = string pointer) starts a dialogue box (stores r0 at runner 0x03000520+8; docs/re/text.md); each
-- call gets r0 replaced by the next CPU address of LIST (one hex address per line), so the game's own runner draws
-- the string in the real box. Logs "SWEEP <n> <addr> f<frame>"; "SWEEPEND" once the list is used up.
local list = {}
local f = io.open(LIST, "r")
for ln in f:lines() do
  local a = ln:match("^(%x+)")
  if a then list[#list + 1] = tonumber(a, 16) end
end
f:close()
-- Some screens restart the same string every frame (the intro): a repeated original pointer keeps the current
-- substitute; only a different original pointer advances the list.
local n, last = 0, nil
L.on_exec(0x08040F6C, 0x08040F6C, function()
  local orig = emu.getState()["cpu.r0"]
  if orig ~= last then
    last = orig
    n = n + 1
    if n == #list + 1 then L.log("SWEEPEND f" .. L.frame) end
    if n <= #list then L.log(string.format("SWEEP %d %X f%d", n, list[n], L.frame)) end
  end
  if n >= 1 and n <= #list then
    local t = {}
    t["cpu.r0"] = list[n]
    emu.setState(t)
  end
end)
