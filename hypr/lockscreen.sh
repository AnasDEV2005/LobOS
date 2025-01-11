
#!/bin/bash

# Disable keybindings
hyprctl keybinds reset

# Optional: Disable specific keybindings if you want to be more selective
hyprctl keybinds unbind SUPER+Q
hyprctl keybinds unbind SUPER+SPACE
# (Add more unbind commands if needed)

# Start the lock screen (assuming you're running a Python script or another command)
source ~/.config/hypr/fabric-venv/bin/activate && python ~/.config/hypr/fab-lock/fablock.py


# After lock screen is closed, restore the keybindings
hyprctl keybinds reload
