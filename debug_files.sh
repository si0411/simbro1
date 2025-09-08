#!/bin/zsh
set +x

SRC="/Volumes/LaCie/Personal/Music/BandCamp"

echo "Checking for one of the 'missing' files..."
echo ""

# Let's check if the files actually exist with different approaches
target="1980s - Mad One Dj.flac"

echo "1. Direct check:"
if [[ -f "$SRC/$target" ]]; then
    echo "✓ Found: $SRC/$target"
else
    echo "✗ Not found: $SRC/$target"
fi

echo ""
echo "2. Finding similar files:"
find "$SRC" -name "*1980s*" -type f

echo ""
echo "3. Finding Mad One files:"
find "$SRC" -name "*Mad One*" -type f

echo ""
echo "4. Sample of actual files in directory:"
find "$SRC" -name "*.flac" | head -5

echo ""
echo "5. Checking if files have unusual characters:"
find "$SRC" -name "*Mad One*" -type f | xxd
