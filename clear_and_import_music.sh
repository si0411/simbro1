#!/bin/bash

# ESC cancel handler
cancel_on_esc() {
 stty -echo -icanon time 0 min 0
 while true; do
   key=$(dd bs=1 count=1 2>/dev/null)
   if [[ $key == $'\e' ]]; then
     echo "Cancelled with ESC"
     kill $$
   fi
   sleep 0.1
 done
}
cancel_on_esc &

# Open iMazing and bring to front
osascript -e 'tell application "iMazing" to activate'

# Reposition window immediately
osascript <<APPLESCRIPT
tell application "System Events"
   tell application process "iMazing"
   	set frontmost to true
   	try
   		set position of front window to {0, 0}
   		set size of front window to {1440, 900}
   	end try
   end tell
end tell
APPLESCRIPT

# Wait for iPhone + UI to be ready
sleep 18

# Dismiss warning if present
osascript <<APPLESCRIPT
tell application "System Events"
   tell application process "iMazing"
   	repeat 20 times
   		if exists (sheet 1 of window 1) then
   			try
   				click button 1 of sheet 1 of window 1
   				exit repeat
   			end try
   		end if
   		delay 1
   	end repeat
   end tell
end tell
APPLESCRIPT

sleep 9  # Before clicking Music

# Click "Music" section
cliclick c:350,155
sleep 11

# Click a track
sleep 9
cliclick c:674,360
sleep 1

# Select all
cliclick kd:cmd t:a ku:cmd
sleep 1

# Click Trash
cliclick c:1405,865
sleep 5

# Click "Apply to All"
cliclick c:520,486
sleep 1

# Click Enter button on screen
cliclick c:633,522
sleep 1

# Press physical Enter
cliclick kp:return
sleep 25

# Click "Import"
cliclick c:1130,867
sleep 2

# Select all & press Enter
cliclick kd:cmd t:a ku:cmd
sleep 1
cliclick kp:return
sleep 2

# Final confirmation button click
cliclick c:986,666
sleep 2
