tell application "iMazing"
    activate
end tell

delay 5

tell application "System Events"
    tell process "iMazing"
        -- Wait for iMazing to be ready
        repeat 10 times
            try
                if (count of windows) > 0 then exit repeat
            end try
            delay 1
        end repeat
        
        delay 2
        
        -- Try to find and click iPhone device
        try
            -- Look for device in sidebar (common patterns)
            try
                click static text "Simon's iPhone" of window 1
            on error
                try
                    click button "Simon's iPhone" of window 1
                on error
                    -- Click first device button if name doesn't match
                    click button 1 of group 1 of window 1
                end try
            end try
        end try
        
        delay 3
        
        -- Click Music section
        try
            click static text "Music" of window 1
        on error
            try
                click button "Music" of window 1
            end try
        end try
        
        delay 3
        
        -- Clear existing music
        try
            -- Select all with Cmd+A
            keystroke "a" using command down
            delay 1
            
            -- Delete with Delete key
            key code 51
            delay 2
        end try
        
        -- Import new files using drag and drop simulation
        try
            -- Open Finder to the music folder
            tell application "Finder"
                activate
                open folder "iPhoneSync" of folder "Music" of home folder
            end tell
            
            delay 2
            
            -- Select all files in Finder
            tell application "System Events"
                tell process "Finder"
                    keystroke "a" using command down
                end tell
            end tell
            
            delay 1
            
            -- Switch back to iMazing
            tell application "iMazing" to activate
            delay 1
            
            -- Simulate drag and drop (this is a workaround)
            tell application "System Events"
                tell process "Finder"
                    keystroke "c" using command down -- Copy files
                end tell
                delay 1
                tell process "iMazing"
                    keystroke "v" using command down -- Paste in iMazing
                end tell
            end tell
            
        end try
        
    end tell
end tell

-- Close Finder window
tell application "Finder"
    close windows
end tell
