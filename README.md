# simbro.app

Multi-app hosting platform and development workspace for simbro.app domain.

## Infrastructure

### VPS Server
- **OS**: Ubuntu 24.04 LTS
- **Purpose**: Host multiple applications

### Network Information
#### IPv4
- **Address**: 72.60.107.156
- **Reverse DNS**: srv986664.hstgr.cloud

#### IPv6
- **Address**: 2a02:4780:5e:cc67::1
- **Reverse DNS**: srv986664.hstgr.cloud

### SSH Access
- **Key name**: simbro_key
- **Key type**: ssh-ed25519
- **Key fingerprint**: AAAAC3NzaC1lZDI1NTE5AAAAIL/bMdHLMDBTTTYAu5+eMRpKlfwtw2LRTzD9vXAcoiX5
- **Associated email**: simon@backpackingtours.com


### Deployment Instructions

#### Upload Files to Live Website
To update the live website files:

1. **Access your web server** (via FTP, cPanel File Manager, or SSH)
2. **Upload fixed files**:
   - `bt_tour_viewer.html` → root directory of simbro.app
   - `update_tours.php` → root directory of simbro.app
   - Ensure `BT_scraping/` directory exists with Python scripts
3. **Test the fix**: Visit https://simbro.app/bt_tour_viewer
4. **Verify itinerary expansion**: Click on tours with itineraries and test day expansion

#### Files Structure on Server
```
/var/www/html/
├── bt_tour_viewer.html              # Main tour viewer page (3-table toggle)
├── start_update.php                 # Start scraping process
├── check_update_status.php          # Monitor scraping progress
└── BT_scraping/                     # Scraping scripts directory (CRITICAL PATH)
    ├── categorized_extractor.py        # Main extraction logic with CSS color detection
    │
    ├── get_grouptour_urls.py           # Group tours URL discovery
    ├── scrape_grouptours.py            # Group tours scraper
    ├── group_tours_frontend.json       # Group tours data (generated)
    │
    ├── get_privatetour_urls.py         # Private tours URL discovery
    ├── scrape_privatetours.py          # Private tours scraper
    ├── private_tours_frontend.json     # Private tours data (generated)
    │
    ├── get_volunteer_urls.py           # Volunteer programs URL discovery
    ├── scrape_volunteers.py            # Volunteer programs scraper
    └── volunteer_frontend.json         # Volunteer programs data (generated)
```

**IMPORTANT**: The BT_scraping directory must be at `/var/www/html/BT_scraping/` - this is where the PHP scripts expect to find the Python scraping files.

### Scraping Different Tour Types

The system supports three types of tours, each with its own scraping workflow:

#### 1. Group Tours
```bash
cd BT_scraping
python3 get_grouptour_urls.py      # Discover URLs
python3 scrape_grouptours.py       # Scrape data
```
Output: `group_tours_frontend.json`

#### 2. Private Tours
```bash
cd BT_scraping
python3 get_privatetour_urls.py    # Discover URLs
python3 scrape_privatetours.py     # Scrape data
```
Output: `private_tours_frontend.json`

#### 3. Volunteer Programs
```bash
cd BT_scraping
python3 get_volunteer_urls.py      # Discover URLs
python3 scrape_volunteers.py       # Scrape data
```
Output: `volunteer_frontend.json`

### Tour Viewer Interface

The `bt_tour_viewer.html` page features a **3-table toggle system**:
- **Group Tours** button - displays group tour data
- **Private Tours** button - displays private tour data
- **Volunteer** button - displays volunteer program data

Each table:
- Loads its own JSON data file
- Has independent search/filter/sort functionality
- Shares the same UI layout and features
- Updates the tour count dynamically

### Color Extraction System

The scraper uses an advanced CSS color class detection system to extract accurate tour colors:

#### How It Works
- **Method 1**: Searches for priority CSS selectors like `circle-fb-rate--magenta`, `l-submenu--blurple`
- **Method 2**: Counts occurrences of color themes to find the dominant one
- **No Fallbacks**: Returns "N/A" if no CSS color classes are found (no hardcoded defaults)

#### Supported Colors
The system maps CSS class names to hex colors from the main stylesheet:
- `magenta` → `#a03a68`
- `blurple` → `#f94171`
- `orangeblood` → `#ff603b`
- `burgundy` → `#ae2e69`
- `purple` → `#6c49ff`
- `orange` → `#ffc132`
- And 10+ other predefined tour colors

#### Verified Results
- **Bali**: #f94171 (blurple) ✅
- **Mexico**: #ff603b (orangeblood) ✅
- **Japan**: #ae2e69 (burgundy) ✅


## Infrastructure Status

### VPS Setup Complete ✅
- **OS**: Ubuntu 24.04 LTS (fully updated)
- **Web Server**: Nginx 1.24.0 (running)
- **Runtime**: Node.js v18.19.1, Python 3.12.3
- **Security**: UFW firewall enabled (SSH, HTTP, HTTPS)
- **Access**: HTTP accessible at http://72.60.107.156
- **SSH**: Password authentication enabled

### Installed Tools
- **Development**: git, build-essential, npm, pip, python3-venv
- **Web Server**: nginx (active and enabled)
- **Security**: ufw firewall
- **SSL**: Ready for Let's Encrypt configuration

### Connection Details
- **SSH Command**: `ssh root@72.60.107.156`
- **Root Password**: Located in `.env` file (ROOT_PASSWORD variable)
- **Web Access**: http://72.60.107.156 (nginx default page)
- **Status**: Ready for application deployment

## Automated Tasks

### Automated Tour Scraping (Every 2 Days) 🤖

**Location**: Server cron on simbro.app

- **Schedule**: Every 2 days at 9:15 AM Thailand time (2:15 AM UTC)
- **Script**: `/var/www/html/BT_scraping/automated_scraping.sh`
- **Log File**: `/var/log/tour_scraping.log`
- **Cron Entry**: `15 2 */2 * * /var/www/html/BT_scraping/automated_scraping.sh >> /var/log/tour_scraping.log 2>&1`
- **Duration**: Approximately 10-20 minutes

**What it does:**
1. Discovers all group tour URLs from backpackingtours.com
2. Scrapes all tour data (itineraries, dates, descriptions, images)
3. Cleans up old backup JSON files (keeps only current versions)
4. Merges CSV pricing data with scraped dates
5. Sets proper file permissions (644, www-data ownership)
6. Sends notifications to dashboard API on start/completion

**Output Files:**
- `group_tours_frontend.json` (base tour data, ~455K)
- `group_tours_frontend_enhanced.json` (with pricing, ~1.1M)

**Notifications:**
- Start: "🚀 Tour scraping started" (info)
- Success: "✅ Tour scraping completed successfully" (info)
- Failure: "❌ Tour scraping failed: [error]" (error)
- Dashboard: https://backpackingtours.simbro.app/api/notifications/external

**Recent Test Results:**
- Duration: 9 minutes
- Tours scraped: 33 tours
- Dates processed: 1,084 dates
- File cleanup: Working (old backups removed)
- Permissions: Correct (644, www-data)

**Check scraping log:**
```bash
ssh root@72.60.107.156
tail -100 /var/log/tour_scraping.log
```

**Manually trigger scraping:**
```bash
ssh root@72.60.107.156
/var/www/html/BT_scraping/automated_scraping.sh
```

**Important Notes:**
- ✅ Image scraping is MANUAL ONLY (triggered via button on webpage)
- ✅ Atomic file writes prevent data corruption during scraping
- ✅ Old timestamped backup files are automatically removed
- ✅ CSV pricing data is merged automatically after scraping
- ✅ Notifications sent to dashboard for monitoring

### Daily CSV Data Merge (Every Day) 🤖

**Location**: Server cron on simbro.app

- **Schedule**: Daily at 10:00 AM Thailand time (3:00 AM UTC)
- **Script**: `/var/www/html/BT_scraping/daily_update.sh`
- **Log File**: `/var/log/tour_data_update.log`
- **Cron Entry**: `0 3 * * * /var/www/html/BT_scraping/daily_update.sh >> /var/log/tour_data_update.log 2>&1`

**What it does:**
1. Pulls latest CSV data from `tourism_api` GitHub repository (private repo with available spaces & prices)
2. Reads existing `group_tours_frontend.json` from server
3. Merges CSV data (available spaces, prices) with existing tour dates
4. Creates/updates `group_tours_frontend_enhanced.json` with merged data
5. Sets proper file permissions (644, www-data ownership)

**Important Notes:**
- ✅ Does NOT scrape new tours (updates pricing only)
- ✅ Does NOT add new dates from CSV (only matches existing dates)
- ✅ Only updates available spaces and pricing info for existing tour dates
- ✅ Runs entirely on server - no GitHub Actions dependency
- ✅ Runs in addition to the every-2-days full scraping

**Check the merge log:**
```bash
ssh root@72.60.107.156
tail -100 /var/log/tour_data_update.log
```

**Manually trigger the merge:**
```bash
ssh root@72.60.107.156
/var/www/html/BT_scraping/daily_update.sh
```

**View all cron tasks:**
```bash
ssh root@72.60.107.156
crontab -l
```

### File Usage by Pages

**Which pages use which JSON files:**

1. **bt_tour_viewer.html** (Tour Viewer)
   - Uses: `group_tours_frontend.json` (base data)
   - Displays: Tour listings, itineraries, descriptions

2. **starting_dates.html** (Date Search)
   - Uses: `group_tours_frontend_enhanced.json` (with pricing)
   - Displays: Available dates with pricing and availability

3. **deals.html** (Deals Page)
   - Uses: `group_tours_frontend_enhanced.json` (with pricing)
   - Displays: Tour deals with current pricing

4. **Image Scraping**
   - Trigger: Manual button click only
   - NOT automated via cron

### Manual Tour Updates (If Needed)

The automated scraping runs every 2 days, but you can trigger it manually:

**Option 1: Run full automation script**
```bash
ssh root@72.60.107.156
/var/www/html/BT_scraping/automated_scraping.sh
```

**Option 2: Run individual steps**
```bash
ssh root@72.60.107.156
cd /var/www/html/BT_scraping
python3 get_grouptour_urls.py       # Step 1: Discover URLs
python3 scrape_grouptours.py        # Step 2: Scrape tours
python3 post_scrape_cleanup.py      # Step 3: Clean old files
python3 merge_csv_data.py           # Step 4: Merge pricing
chmod 644 group_tours_frontend*.json
chown www-data:www-data group_tours_frontend*.json
```

**Option 3: Run locally and deploy**
```bash
cd BT_scraping
python3 get_grouptour_urls.py
python3 scrape_grouptours.py
scp group_tours_frontend.json root@72.60.107.156:/var/www/html/BT_scraping/
```

### Troubleshooting

**If automated scraping fails:**
1. Check the scraping log: `ssh root@72.60.107.156 'tail -100 /var/log/tour_scraping.log'`
2. Verify backpackingtours.com is accessible
3. Check Python dependencies: `ssh root@72.60.107.156 'pip3 list | grep -E "requests|beautifulsoup4"'`
4. Check notification API is working: View dashboard at https://backpackingtours.simbro.app
5. Manually run script to see detailed output: `/var/www/html/BT_scraping/automated_scraping.sh`

**If automated merge fails:**
1. Check the merge log: `ssh root@72.60.107.156 'tail -100 /var/log/tour_data_update.log'`
2. Verify `tourism_api` repository is accessible from server
3. Check Python dependencies are installed
4. Ensure base JSON file exists: `ls -la /var/www/html/BT_scraping/group_tours_frontend.json`
5. Manually run the script: `/var/www/html/BT_scraping/daily_update.sh`

**Common issues:**
- **Git credentials expired**: Update GitHub token in merge_csv_data.py
- **Missing files**: Run scraping first to generate base JSON
- **Permission errors**: Check file ownership (should be www-data:www-data)
- **Dict parsing errors**: If merge script fails with "'dict' object has no attribute 'split'", the enhanced JSON may be corrupted - re-run full scraping
- **Python errors**: Check Python version (3.12+) and dependencies

**Monitor automation:**
- View notifications: https://backpackingtours.simbro.app
- Check cron status: `ssh root@72.60.107.156 'systemctl status cron'`
- View all logs: `ssh root@72.60.107.156 'tail -f /var/log/tour_*.log'`