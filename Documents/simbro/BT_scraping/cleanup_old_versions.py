#!/usr/bin/env python3
"""
Cleanup old versions of tour data and keep only the most recent version
"""

import os
import json
import glob
from datetime import datetime

def cleanup_old_versions():
    """Remove old versions and ensure only the newest data remains"""
    print("🧹 Cleaning up old tour data versions...")

    # Find all tour data files
    all_files = []

    # Main file
    if os.path.exists('group_tours_frontend.json'):
        all_files.append(('group_tours_frontend.json', os.path.getmtime('group_tours_frontend.json')))

    # Enhanced file (created by merge_csv_data.py) - CRITICAL!
    if os.path.exists('group_tours_frontend_enhanced.json'):
        all_files.append(('group_tours_frontend_enhanced.json', os.path.getmtime('group_tours_frontend_enhanced.json')))
        print("✅ Found enhanced JSON file (latest scraped version)")

    # Timestamped files
    for file_path in glob.glob('group_tours_frontend_*.json'):
        # Skip enhanced version as we already added it
        if file_path != 'group_tours_frontend_enhanced.json' and os.path.exists(file_path):
            all_files.append((file_path, os.path.getmtime(file_path)))

    if not all_files:
        print("❌ No tour data files found")
        return False

    # Sort by modification time (most recent first)
    all_files.sort(key=lambda x: x[1], reverse=True)

    print(f"📁 Found {len(all_files)} tour data files:")
    for file_path, mtime in all_files:
        mod_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        print(f"   {file_path} (modified: {mod_time})")

    if len(all_files) <= 1:
        print("✅ Only one file exists, no cleanup needed")
        return True

    # Keep the most recent file
    newest_file, newest_time = all_files[0]
    print(f"\n🎯 Keeping newest file: {newest_file}")

    # Remove all other files
    removed_count = 0
    for file_path, mtime in all_files[1:]:
        try:
            os.remove(file_path)
            print(f"🗑️ Removed: {file_path}")
            removed_count += 1
        except Exception as e:
            print(f"⚠️ Could not remove {file_path}: {e}")

    # Ensure the newest file is named correctly
    if newest_file != 'group_tours_frontend.json':
        try:
            # If the newest file is the enhanced version, copy it (don't rename it)
            # This preserves the enhanced version for other tools that may need it
            if newest_file == 'group_tours_frontend_enhanced.json':
                import shutil
                shutil.copy2(newest_file, 'group_tours_frontend.json')
                print(f"📝 Copied {newest_file} to group_tours_frontend.json")
                print("   (Keeping enhanced version for CSV merge tools)")
            else:
                # For other files, rename them
                if os.path.exists('group_tours_frontend.json'):
                    os.remove('group_tours_frontend.json')
                os.rename(newest_file, 'group_tours_frontend.json')
                print(f"📝 Renamed {newest_file} to group_tours_frontend.json")

            # Set proper permissions for www-data to read
            try:
                os.chmod('group_tours_frontend.json', 0o664)
                print("✅ Set proper permissions (664) on group_tours_frontend.json")
            except Exception as perm_error:
                print(f"⚠️ Could not set permissions: {perm_error}")

        except Exception as e:
            print(f"⚠️ Could not update file: {e}")

    # Verify the data format and clean up if needed
    cleanup_data_format()

    print(f"\n✅ Cleanup complete! Removed {removed_count} old files")
    return True

def cleanup_data_format():
    """Ensure the data format is consistent with single timestamp"""
    try:
        with open('group_tours_frontend.json', 'r') as f:
            data = json.load(f)

        # Check if data is in old format (array of tours with individual timestamps)
        if isinstance(data, list):
            print("🔄 Converting old format to new format...")

            # Create new format with single timestamp
            today = datetime.now().strftime('%Y-%m-%d')

            # Clean individual tour data
            cleaned_tours = []
            for tour in data:
                if isinstance(tour, dict) and 'error' not in tour:
                    # Remove individual last_updated fields to avoid conflicts
                    clean_tour = {k: v for k, v in tour.items() if k != 'last_updated'}
                    cleaned_tours.append(clean_tour)
                else:
                    cleaned_tours.append(tour)

            new_data = {
                'last_updated': today,
                'tours': cleaned_tours
            }

            # Save the cleaned data
            with open('group_tours_frontend.json', 'w') as f:
                json.dump(new_data, f, indent=2)

            print(f"✅ Converted to new format with timestamp: {today}")

        elif isinstance(data, dict) and 'tours' in data and 'last_updated' in data:
            print("✅ Data is already in correct new format")

            # Still clean individual tour timestamps if they exist
            tours = data['tours']
            cleaned_tours = []
            changes_made = False

            for tour in tours:
                if isinstance(tour, dict) and 'last_updated' in tour:
                    clean_tour = {k: v for k, v in tour.items() if k != 'last_updated'}
                    cleaned_tours.append(clean_tour)
                    changes_made = True
                else:
                    cleaned_tours.append(tour)

            if changes_made:
                data['tours'] = cleaned_tours
                with open('group_tours_frontend.json', 'w') as f:
                    json.dump(data, f, indent=2)
                print("🧹 Cleaned individual tour timestamps")
        else:
            print("⚠️ Unknown data format, leaving as-is")

    except Exception as e:
        print(f"⚠️ Error cleaning data format: {e}")

if __name__ == "__main__":
    cleanup_old_versions()