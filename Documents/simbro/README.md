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

### Daily CSV Data Merge (GitHub Actions) 🤖

**Location**: `.github/workflows/daily-scraping.yml` in BT_scraping repo (`si0411/simbro1`)

- **Schedule**: Daily at 10:00 AM Thailand time (3:00 AM UTC)
- **Repository**: https://github.com/si0411/simbro1
- **Purpose**: Merge CSV data (available spaces & prices) with existing tour data and deploy to server
- **Cron Expression**: `0 3 * * *`

**What it does:**
1. Pulls latest CSV data from `tourism_api` repository (private repo)
2. Reads existing `group_tours_frontend.json` from repository
3. Merges CSV data (available spaces, prices) with existing tour dates
4. Creates `group_tours_frontend_enhanced.json` with merged data
5. Commits enhanced JSON to repository (git history)
6. Deploys BOTH files to simbro.app server

**Important Notes:**
- ✅ Does NOT scrape new tours (manual control maintained)
- ✅ Does NOT add new dates from CSV (only matches existing dates)
- ✅ Only updates available spaces and pricing info
- ✅ Deploys both base and enhanced JSON files

**Configuration:**
- Requires `TOURISM_API_TOKEN` secret (GitHub PAT with repo access)
- Requires `SERVER_PASSWORD` secret (for SCP deployment)

**View workflow runs:**
```bash
# Via GitHub web interface
https://github.com/si0411/simbro1/actions

# Via GitHub API
curl -s "https://api.github.com/repos/si0411/simbro1/actions/runs?per_page=5"
```

**Manual trigger:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.github.com/repos/si0411/simbro1/actions/workflows/daily-scraping.yml/dispatches \
  -d '{"ref":"master"}'
```

### Manual Tour Updates

When you need to scrape fresh tour data (new tours, updated itineraries, etc.):

1. **Run scraping locally or via server:**
   ```bash
   cd BT_scraping
   python get_grouptour_urls.py
   python scrape_grouptours.py
   ```

2. **Deploy to server:**
   ```bash
   scp group_tours_frontend.json root@72.60.107.156:/var/www/html/BT_scraping/
   ```

3. **Commit to repository:**
   ```bash
   git add group_tours_frontend.json
   git commit -m "Update tour data"
   git push
   ```

The daily automated merge will then update available spaces and prices.

### Troubleshooting

**If GitHub Actions workflow fails:**
1. Check workflow runs at https://github.com/si0411/simbro1/actions
2. Verify `TOURISM_API_TOKEN` secret has repo access to `tourism_api` repository
3. Check if `tourism_api` repository is accessible
4. Verify base file `group_tours_frontend.json` exists in repository