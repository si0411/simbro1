tell application "iMazing"
	activate
end tell

delay 10

tell application "System Events"
	tell process "iMazing"
		set frontmost to true

		-- Dismiss alert if it appears
		repeat 30 times
			try
				if exists sheet 1 of window 1 then
					click button 1 of sheet 1 of window 1
					exit repeat
				end if
			end try
			delay 1
		end repeat

		-- Select Simon’s iPhone from the sidebar
		repeat 30 times
			try
				if exists text "Simon’s iPhone" of outline 1 of scroll area 1 of splitter group 1 of window 1 then
					click text "Simon’s iPhone" of outline 1 of scroll area 1 of splitter group 1 of window 1
					exit repeat
				end if
			end try
			delay 1
		end repeat
	end tell
end tell

-- Now click the Music app icon
delay 2
do shell script "/usr/local/bin/cliclick c:962,350"
