#!/bin/bash
#
# Server Verification Script for BT Scraping System
# This script checks and fixes file permissions to ensure the web server can write to necessary directories
#
# Usage: sudo bash verify_permissions.sh
#

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "  BT Scraping Permission Verification"
echo "========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}ERROR: This script must be run as root (sudo)${NC}"
    echo "Usage: sudo bash verify_permissions.sh"
    exit 1
fi

# Define the scraping directory
SCRAPING_DIR="/var/www/html/BT_scraping"

# Check if directory exists
if [ ! -d "$SCRAPING_DIR" ]; then
    echo -e "${RED}ERROR: Scraping directory not found: $SCRAPING_DIR${NC}"
    echo "Please ensure the BT_scraping directory is deployed to the server."
    exit 1
fi

echo -e "${GREEN}✓${NC} Found scraping directory: $SCRAPING_DIR"
echo ""

# Check current ownership and permissions
echo "📋 Current directory status:"
ls -la "$SCRAPING_DIR" | head -10
echo ""

# Fix ownership to www-data (web server user)
echo "🔧 Fixing ownership to www-data:www-data..."
chown -R www-data:www-data "$SCRAPING_DIR"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Ownership updated successfully"
else
    echo -e "${RED}✗${NC} Failed to update ownership"
    exit 1
fi

# Fix directory permissions (755 - rwxr-xr-x)
echo ""
echo "🔧 Fixing directory permissions..."
find "$SCRAPING_DIR" -type d -exec chmod 755 {} \;

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Directory permissions updated (755)"
else
    echo -e "${RED}✗${NC} Failed to update directory permissions"
fi

# Fix file permissions (644 - rw-r--r--)
echo ""
echo "🔧 Fixing file permissions..."
find "$SCRAPING_DIR" -type f -exec chmod 644 {} \;

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} File permissions updated (644)"
else
    echo -e "${RED}✗${NC} Failed to update file permissions"
fi

# Make Python scripts executable
echo ""
echo "🔧 Making Python scripts executable..."
find "$SCRAPING_DIR" -name "*.py" -exec chmod 755 {} \;

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Python scripts made executable"
else
    echo -e "${RED}✗${NC} Failed to make Python scripts executable"
fi

# Check for JSON files and their permissions
echo ""
echo "📄 Checking JSON data files:"
for file in "$SCRAPING_DIR"/*.json; do
    if [ -f "$file" ]; then
        basename "$file"
        ls -lh "$file" | awk '{print "  Owner: " $3 "  Permissions: " $1 "  Size: " $5 "  Modified: " $6 " " $7 " " $8}'
    fi
done

# Check if error log exists and is writable
echo ""
echo "📝 Checking error log:"
ERROR_LOG="$SCRAPING_DIR/scraping_errors.log"
if [ -f "$ERROR_LOG" ]; then
    echo -e "${GREEN}✓${NC} Error log exists: $ERROR_LOG"
    ls -lh "$ERROR_LOG" | awk '{print "  Permissions: " $1 "  Size: " $5}'
else
    echo -e "${YELLOW}!${NC} Error log does not exist (will be created on first error)"
fi

# Test write permissions by creating a test file
echo ""
echo "🧪 Testing write permissions..."
TEST_FILE="$SCRAPING_DIR/.permission_test_$$"
sudo -u www-data touch "$TEST_FILE" 2>/dev/null

if [ -f "$TEST_FILE" ]; then
    echo -e "${GREEN}✓${NC} Write test successful - www-data can create files"
    rm -f "$TEST_FILE"
else
    echo -e "${RED}✗${NC} Write test failed - www-data CANNOT create files"
    echo "  This will cause scraping to fail!"
    exit 1
fi

# Check Python dependencies
echo ""
echo "🐍 Checking Python dependencies..."
cd "$SCRAPING_DIR" || exit 1

python3 -c "import requests, bs4, json" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Python dependencies installed (requests, bs4)"
else
    echo -e "${RED}✗${NC} Missing Python dependencies"
    echo "  Install with: pip3 install requests beautifulsoup4"
fi

# Summary
echo ""
echo "========================================="
echo "  Verification Complete"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. The scraping system should now have proper permissions"
echo "2. Test by running: python3 $SCRAPING_DIR/scrape_grouptours.py"
echo "3. Check error log if issues occur: $ERROR_LOG"
echo ""

# Show final directory status
echo "Final directory permissions:"
ls -la "$SCRAPING_DIR" | grep -E "\.json|\.py|scraping_errors" | head -10
