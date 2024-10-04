-- pobranie akcji przekazanej przez Pythona
local action = ...

-- egzekucja akcji
if action == "up" then
    joypad.set({["Up"] = true})
elseif action == "down" then
    joypad.set({["Down"] = true})
elseif action == "left" then
    joypad.set({["Left"] = true})
elseif action == "right" then
    joypad.set({["Right"] = true})
elseif action == "A" then
    joypad.set({["A"] = true})
elseif action = "B" then
    joypad.set({["B"] = true})
end

-- przejdź do następnej klastki
emu.frameadvance()