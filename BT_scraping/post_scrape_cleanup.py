#!/usr/bin/env python3
"""
Post-scraping cleanup script
Run this after scraping completes to:
1. Copy latest enhanced JSON to frontend JSON
2. Remove old timestamped versions
3. Set proper permissions
4. Verify data integrity

CRITICAL: This ensures bt_tour_viewer always loads the latest data!
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

def log_message(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    sys.stdout.flush()

def main():
    """Main cleanup process"""
    log_message("=" * 60)
    log_message("POST-SCRAPING CLEANUP")
    log_message("=" * 60)

    # Change to BT_scraping directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    log_message(f"Working directory: {os.getcwd()}")

    # Step 1: Run cleanup script
    log_message("\n📋 Step 1: Running cleanup_old_versions.py...")
    try:
        result = subprocess.run(
            ['python3', 'cleanup_old_versions.py'],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        if result.stderr:
            print(f"Warnings: {result.stderr}")
        log_message("✅ Cleanup completed successfully")
    except subprocess.CalledProcessError as e:
        log_message(f"❌ Cleanup failed: {e.stderr}")
        return False
    except FileNotFoundError:
        log_message("❌ cleanup_old_versions.py not found!")
        return False

    # Step 2: Verify the frontend JSON exists and is recent
    log_message("\n📋 Step 2: Verifying group_tours_frontend.json...")
    frontend_json = Path('group_tours_frontend.json')

    if not frontend_json.exists():
        log_message("❌ group_tours_frontend.json not found after cleanup!")
        return False

    # Check file age
    mtime = frontend_json.stat().st_mtime
    file_age_seconds = datetime.now().timestamp() - mtime
    file_age_minutes = file_age_seconds / 60

    log_message(f"✅ File exists")
    log_message(f"   Size: {frontend_json.stat().st_size / 1024:.2f} KB")
    log_message(f"   Modified: {datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')}")
    log_message(f"   Age: {file_age_minutes:.1f} minutes ago")

    if file_age_minutes > 60:
        log_message("⚠️  WARNING: File is more than 1 hour old - may not be latest scrape")

    # Step 3: Set proper permissions
    log_message("\n📋 Step 3: Setting proper permissions...")
    try:
        # Set 664 (rw-rw-r--) for JSON files
        for json_file in ['group_tours_frontend.json', 'group_tours_frontend_enhanced.json']:
            if Path(json_file).exists():
                os.chmod(json_file, 0o664)
                log_message(f"✅ Set 664 permissions on {json_file}")
    except Exception as e:
        log_message(f"⚠️  Could not set permissions: {e}")

    # Step 4: Count and list remaining files
    log_message("\n📋 Step 4: Checking remaining JSON files...")
    json_files = list(Path('.').glob('group_tours_frontend*.json'))
    log_message(f"Found {len(json_files)} JSON files:")
    for f in sorted(json_files, key=lambda x: x.stat().st_mtime, reverse=True):
        mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        size = f.stat().st_size / 1024
        log_message(f"   {f.name:50} {size:8.2f} KB  {mtime}")

    log_message("\n" + "=" * 60)
    log_message("✅ POST-SCRAPING CLEANUP COMPLETE")
    log_message("=" * 60)
    log_message("\n🌐 Tour viewer will now load the latest data:")
    log_message("   https://simbro.app/bt_tour_viewer")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
