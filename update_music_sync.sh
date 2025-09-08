#!/bin/zsh

SRC="/Volumes/LaCie/Personal/Music/BandCamp"
DEST="$HOME/Music/iPhoneSync"

mkdir -p "$DEST"
find "$DEST" -type f -delete 2>/dev/null

# Check if ffmpeg is available
if ! command -v ffmpeg &> /dev/null; then
    echo "Error: ffmpeg not found. Please install ffmpeg first."
    exit 1
fi

echo "Selecting and processing music files..."

# Get all files into array
all_files=()
while IFS= read -r -d $'\0' file; do
    [[ -n "$file" ]] && all_files+=("$file")
done < <(find "$SRC" \( -name '*.flac' -o -name '*.mp3' -o -name '*.ogg' -o -name '*.oga' -o -name '*.m4a' -o -name '*.aac' -o -name '*.wav' -o -name '*.aiff' -o -name '*.wma' -o -name '*.opus' -o -name '*.webm' -o -name '*.3gp' -o -name '*.amr' \) -type f -print0)

# Sort by modification time to get 30 most recent
recent_files=()
temp_array=()

for file in "${all_files[@]}"; do
    if [[ ! -f "$file" || -z "$file" ]]; then
        continue
    fi
    
    mtime=$(stat -f "%m" "$file" 2>/dev/null)
    if [[ -n "$mtime" && -n "$file" ]]; then
        temp_array+=("$mtime:$file")
    fi
done

# Sort and get exactly 30 recent - filter out empty entries
if [[ ${#temp_array[@]} -gt 0 ]]; then
    IFS=$'\n' sorted=($(sort -rn <<<"${temp_array[*]}"))
    
    for entry in "${sorted[@]}"; do
        # Skip empty entries
        [[ -z "$entry" || "$entry" == ":" ]] && continue
        
        # Parse entry
        if [[ "$entry" == *:* ]]; then
            filepath="${entry#*:}"
            if [[ -n "$filepath" && -f "$filepath" ]]; then
                recent_files+=("$filepath")
                # Stop when we have 30
                [[ ${#recent_files[@]} -eq 30 ]] && break
            fi
        fi
    done
fi

# Get remaining files for random selection
remaining_files=()
for file in "${all_files[@]}"; do
    [[ -z "$file" ]] && continue
    found=false
    for recent in "${recent_files[@]}"; do
        [[ "$file" == "$recent" ]] && found=true && break
    done
    [[ "$found" == false ]] && remaining_files+=("$file")
done

# Select random files - get extra to backfill if needed
target_total=40
needed_random=$((target_total - ${#recent_files[@]}))
random_files=()
temp_remaining=("${remaining_files[@]}")

while [[ ${#random_files[@]} -lt $needed_random && ${#temp_remaining[@]} -gt 0 ]]; do
    random_index=$((RANDOM % ${#temp_remaining[@]}))
    candidate="${temp_remaining[$random_index]}"
    
    temp_remaining=("${temp_remaining[@]:0:$random_index}" "${temp_remaining[@]:$((random_index+1))}")
    
    if [[ -f "$candidate" ]]; then
        random_files+=("$candidate")
    fi
done

# Print selected files
echo ""
echo "=== SELECTED FILES ==="
echo ""
echo "RECENT FILES (${#recent_files[@]} files):"
for file in "${recent_files[@]}"; do
    echo "  $(basename "$file")"
done

echo ""
echo "RANDOM FILES (${#random_files[@]} files):"
for file in "${random_files[@]}"; do
    echo "  $(basename "$file")"
done
echo ""

# Combine chosen files
chosen_files=("${recent_files[@]}" "${random_files[@]}")

# Process files (copy or convert)
success=0
used_names=()

process_file() {
    local source_file="$1"
    local base_name="$(basename "$source_file")"
    local extension="${source_file##*.}"
    
    # Handle long filenames
    if [[ ${#base_name} -gt 250 ]]; then
        local name_part="${base_name%.*}"
        base_name="${name_part:0:200}.${extension}"
    fi
    
    # Clean special characters
    base_name="${base_name//[^a-zA-Z0-9._-]/_}"
    
    # Determine output filename
    local output_name=""
    if [[ "$extension" == "flac" || "$extension" == "ogg" || "$extension" == "oga" || "$extension" == "wav" || "$extension" == "aiff" || "$extension" == "wma" || "$extension" == "opus" || "$extension" == "webm" || "$extension" == "3gp" || "$extension" == "amr" ]]; then
        # Convert to M4A
        local name_part="${base_name%.*}"
        output_name="${name_part}.m4a"
    else
        # Keep original format (MP3, M4A)
        output_name="$base_name"
    fi
    
    # Handle duplicates
    local final_name="$output_name"
    local counter=1
    while [[ " ${used_names[*]} " =~ " ${final_name} " ]]; do
        local ext="${output_name##*.}"
        local name_part="${output_name%.*}"
        final_name="${name_part}_${counter}.${ext}"
        ((counter++))
    done
    
    used_names+=("$final_name")
    
    # Process the file
    if [[ "$extension" == "flac" || "$extension" == "ogg" || "$extension" == "oga" || "$extension" == "wav" || "$extension" == "aiff" || "$extension" == "wma" || "$extension" == "opus" || "$extension" == "webm" || "$extension" == "3gp" || "$extension" == "amr" ]]; then
        # Convert using ffmpeg
        if ffmpeg -y -i "$source_file" -map 0:a -c:a aac -b:a 192k "$DEST/$final_name" >/dev/null 2>&1; then
            return 0
        else
            return 1
        fi
    else
        # Just copy MP3, M4A, AAC files
        if cp "$source_file" "$DEST/$final_name" 2>/dev/null; then
            return 0
        else
            return 1
        fi
    fi
}

echo "Processing files (converting FLAC/OGG/OGA/WAV/AIFF/WMA/OPUS/WEBM/3GP/AMR to M4A)..."

for file in "${chosen_files[@]}"; do
    [[ -z "$file" || ! -f "$file" ]] && continue
    
    if process_file "$file"; then
        ((success++))
    else
        echo "Failed: $(basename "$file")"
    fi
done

echo ""
echo "=== MUSIC PROCESSING COMPLETE ==="
echo "Processed: $success files in $DEST"
echo ""
echo "Files are ready for import to iMazing."
echo "Location: $DEST"
