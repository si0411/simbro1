#!/usr/bin/env python3
"""
Full tour scraping process
1. Discover all group tour URLs
2. Scrape all tours
3. Update progress status throughout
"""

import json
import os
import sys
import time
import subprocess
from datetime import datetime

def log_message(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    sys.stdout.flush()

def set_status(status, progress=0, message='', total_urls=0, completed_urls=0):
    """Update scraping status file"""
    status_file = os.path.join(os.path.dirname(__file__), 'scraping_status.json')
    data = {
        'status': status,
        'progress': progress,
        'message': message,
        'total_urls': total_urls,
        'completed_urls': completed_urls,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    with open(status_file, 'w') as f:
        json.dump(data, f)

def run_command(command, description):
    """Run a command and return success status"""
    log_message(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        log_message(f"Error: {e.stderr}")
        return False, e.stderr

def main():
    try:
        log_message("=== Starting Full Tour Scraping Process ===")

        # Step 1: Discover URLs
        set_status('running', 5, 'Discovering group tour URLs...')
        log_message("Step 1: Discovering group tour URLs...")

        success, output = run_command('python3 get_grouptour_urls.py', 'URL discovery')
        if not success:
            set_status('error', 0, f'Failed to discover URLs: {output}')
            return

        # Read discovered URLs
        urls_file = 'group_tour_urls.json'
        if not os.path.exists(urls_file):
            set_status('error', 0, 'No URLs file found after discovery')
            return

        with open(urls_file, 'r') as f:
            urls_data = json.load(f)

        total_urls = len(urls_data)
        log_message(f"Found {total_urls} tour URLs to scrape")

        # Step 2: Run main scraping process
        set_status('running', 10, f'Starting to scrape {total_urls} tours...', total_urls, 0)
        log_message("Step 2: Running main scraping process...")

        # Run the existing scraping process (scrape_grouptours.py if it exists)
        # Otherwise we'll create a simple loop to scrape all tours

        # Check if scrape_grouptours.py exists
        if os.path.exists('scrape_grouptours.py'):
            log_message("Using existing scrape_grouptours.py")
            success, output = run_command('python3 scrape_grouptours.py', 'Main scraping process')
        else:
            # Fallback: scrape tours one by one
            log_message("Scraping tours individually...")
            success = scrape_tours_individually(urls_data, total_urls)

        if not success:
            set_status('error', 0, 'Scraping process failed')
            return

        # Step 3: Run post-scraping cleanup
        set_status('running', 95, 'Running post-scraping cleanup...', total_urls, total_urls)
        log_message("Step 3: Running post-scraping cleanup...")

        success, output = run_command('python3 post_scrape_cleanup.py', 'Post-scraping cleanup')
        if not success:
            log_message(f"⚠️  Warning: Cleanup had issues: {output}")
            # Don't fail the entire process if cleanup fails
        else:
            log_message("✅ Post-scraping cleanup completed")

        # Step 4: Complete
        set_status('completed', 100, f'Successfully scraped {total_urls} tours', total_urls, total_urls)
        log_message("=== Scraping Process Completed Successfully ===")

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        log_message(f"ERROR: {error_msg}")
        set_status('error', 0, error_msg)

def scrape_tours_individually(urls_data, total_urls):
    """Scrape tours one by one if no main scraping script exists"""
    completed = 0
    results = []

    for i, tour_data in enumerate(urls_data):
        url = tour_data.get('bt_url')
        if not url:
            continue

        # Update progress
        progress = 10 + (i / total_urls) * 85  # 10% for discovery, 85% for scraping
        set_status('running', int(progress), f'Scraping tour {i+1}/{total_urls}: {url}', total_urls, completed)

        log_message(f"Scraping [{i+1}/{total_urls}]: {url}")

        # Run scraping for this URL
        try:
            result = subprocess.run(['python3', 'scrape_all_images.py', url],
                                  capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                # Parse the JSON result
                tour_result = json.loads(result.stdout)
                if tour_result.get('success'):
                    results.append(tour_result)
                    completed += 1
                    log_message(f"✓ Successfully scraped: {tour_result.get('tour_name', 'Unknown')}")
                else:
                    log_message(f"✗ Failed to scrape: {url}")
            else:
                log_message(f"✗ Process failed for: {url}")
        except Exception as e:
            log_message(f"✗ Error scraping {url}: {e}")

        # Small delay to avoid overwhelming the server
        time.sleep(2)

    # Save results
    results_file = 'tour_images_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    log_message(f"Completed scraping {completed}/{total_urls} tours")
    return True

if __name__ == "__main__":
    main()