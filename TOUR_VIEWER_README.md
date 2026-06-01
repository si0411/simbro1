# Backpacking Tours Data Viewer

## What it does
Checks www.backpackingtours.com for group tour URLs, scrapes the data, and displays it in a web viewer at https://simbro.app/bt_tour_viewer

## Simple Process
1. **Collect URLs**: `BT_scraping/get_grouptour_urls.py` → saves to `BT_scraping/bt_matching_urls.txt`
2. **Scrape Tour Data**: `BT_scraping/categorized_extractor.py` or `BT_scraping/process_all_tours.py` → creates timestamped JSON
3. **Merge CSV Data**: `BT_scraping/merge_csv_data.py` → creates `group_tours_frontend_enhanced.json`
4. **Auto Cleanup**: `BT_scraping/post_scrape_cleanup.py` → copies latest to `group_tours_frontend.json`
5. **View Data**: Visit https://simbro.app/bt_tour_viewer - loads `BT_scraping/group_tours_frontend.json`

## How to Update Data
1. Go to https://simbro.app/bt_tour_viewer
2. Click "Update Tours" button
3. Wait for scraping to complete (progress bar shows status)
4. Refresh page to see updated data

## Critical Files & Data Flow

### JSON Files (in order of creation):
1. **`group_tours_frontend_YYYYMMDD_HHMMSS.json`** - Timestamped scrape output
2. **`group_tours_frontend_enhanced.json`** - Enhanced with CSV data (starting dates, prices)
3. **`group_tours_frontend.json`** - **LIVE FILE** used by tour viewer

### Python Scripts:
- `get_grouptour_urls.py` - Discovers tour URLs from website
- `scrape_grouptours.py` - Scrapes tour data and creates timestamped JSON
- `merge_csv_data.py` - Merges CSV data to create enhanced JSON
- **`cleanup_old_versions.py`** - Removes old versions, keeps latest
- **`post_scrape_cleanup.py`** - Post-scrape cleanup (runs automatically)
- `scrape_full_process.py` - Orchestrates full scraping workflow

### HTML Files:
- `bt_tour_viewer.html` - Main viewer interface with 3 tabs (Group/Private/Volunteer)
- `starting_dates.html` - Date-based tour search
- `image_viewer.html` - Tour image viewer

## Troubleshooting

### "Tour viewer shows old data"

**Symptoms:** Website shows "Last Updated: [old date]" even after scraping

**Root Causes:**
1. Scrape created timestamped file but cleanup didn't run
2. Enhanced JSON created from old source data
3. Old timestamped files blocking latest version
4. Permission issues preventing file updates

**Solution:**
```bash
# SSH into server
ssh root@simbro.app

# Navigate to scraping directory
cd /var/www/html/BT_scraping

# Run post-scrape cleanup manually
python3 post_scrape_cleanup.py

# This will:
# - Find all JSON versions (including _enhanced)
# - Keep the newest one
# - Copy it to group_tours_frontend.json
# - Remove old timestamped versions
# - Set proper permissions (664)
```

**Verify Fix:**
```bash
# Check file dates and sizes
ls -lh group_tours_frontend*.json

# Check last_updated field in JSON
python3 -c "import json; print(json.load(open('group_tours_frontend.json'))['last_updated'])"

# Refresh tour viewer and check "Last Updated" date
```

### "Permission denied" errors

**Solution:**
```bash
cd /var/www/html/BT_scraping
chmod 664 group_tours_frontend*.json
chown www-data:www-data group_tours_frontend*.json
```

### "Enhanced file exists but not loading"

The enhanced file (`group_tours_frontend_enhanced.json`) is NOT used by the tour viewer directly. It must be copied to `group_tours_frontend.json` by the cleanup script.

**Manual Fix:**
```bash
cd /var/www/html/BT_scraping
cp group_tours_frontend_enhanced.json group_tours_frontend.json
chmod 664 group_tours_frontend.json
```

## Maintenance

### Weekly Cleanup (Automated)
The `post_scrape_cleanup.py` script now runs automatically after each scrape via `scrape_full_process.py`. No manual intervention needed.

### Manual Cleanup (if needed)
```bash
ssh root@simbro.app
cd /var/www/html/BT_scraping
python3 post_scrape_cleanup.py
```

### Check Data Freshness
```bash
# View last updated date
curl -s https://simbro.app/BT_scraping/group_tours_frontend.json | python3 -c "import sys,json; print(json.load(sys.stdin)['last_updated'])"

# List all JSON files with dates
ssh root@simbro.app "cd /var/www/html/BT_scraping && ls -lh group_tours_frontend*.json"
```

## Deployment

To deploy changes to the server:

```bash
# From local machine in /Users/simon/Documents/simbro/
python3 deploy_bt_scraping.py

# This deploys:
# - All BT_scraping/*.py scripts (including cleanup scripts)
# - Tour viewer HTML files
# - PHP backend files
```

**After deployment, verify:**
1. Visit https://simbro.app/bt_tour_viewer
2. Check "Last Updated" date
3. Click "Update Tours" to trigger fresh scrape
4. Verify cleanup runs and removes old files

## Files Structure
```
/var/www/html/
├── bt_tour_viewer.html          # Main tour viewer
├── starting_dates.html           # Date search page
├── image_viewer.html             # Image viewer
└── BT_scraping/
    ├── group_tours_frontend.json              # LIVE FILE (tour viewer loads this)
    ├── group_tours_frontend_enhanced.json     # Enhanced with CSV data
    ├── cleanup_old_versions.py                # Cleanup logic
    ├── post_scrape_cleanup.py                 # Post-scrape automation
    ├── scrape_full_process.py                 # Main scraping orchestrator
    ├── merge_csv_data.py                      # CSV data merger
    └── [other scraping scripts]
```
