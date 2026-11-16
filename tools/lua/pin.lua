-- Write bytes every frame (from frame PIN_FROM, default 1): --var "PIN={[0x030051F1]=1}"
local mem = emu.memType.gbaMemory
L.on_frame(function(f)
  if f >= (PIN_FROM or 1) then for a, v in pairs(PIN) do emu.write(a, v, mem) end end
end)
