#!/usr/bin/env python3
"""
Merge CSV data from tourism_api with group_tours_frontend.json
Adds available spaces and pricing information to tour dates

CSV date format: DD-MM-YYYY (e.g., "07-10-2025")
JSON date format: D MMM - D MMM YYYY - Status (e.g., "6 Oct - 19 Oct 2025 - Book Now")
"""

import json
import csv
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path


def parse_csv_date(date_str):
    """Parse DD-MM-YYYY format to datetime"""
    try:
        return datetime.strptime(date_str, "%d-%m-%Y")
    except:
        return None


def parse_json_date(date_part):
    """Parse 'D MMM YYYY' format to datetime"""
    try:
        # Clean up the date string and parse
        return datetime.strptime(date_part.strip(), "%d %b %Y")
    except:
        # Try with full month name
        try:
            return datetime.strptime(date_part.strip(), "%d %B %Y")
        except:
            return None


def normalize_tour_name(name):
    """
    Normalize tour name for matching between JSON and CSV
    Handles: colons, ampersands, dashes, extra spaces
    """
    if not name:
        return ""

    # Remove/replace special characters
    normalized = name.replace(':', '')  # Remove colons
    normalized = normalized.replace('&', ' ')  # Replace & with space
    normalized = normalized.replace('-', ' ')  # Replace dashes with space

    # Normalize whitespace (multiple spaces to single space)
    normalized = ' '.join(normalized.split())

    return normalized.strip()


def extract_dates_from_json_string(date_string):
    """
    Extract start and end dates from JSON date string
    Format: "6 Oct - 19 Oct 2025 - Book Now"
    Returns: (start_date, end_date, status) or None
    """
    try:
        parts = date_string.split(' - ')
        if len(parts) < 3:
            return None

        start_part = parts[0].strip()  # "6 Oct"
        end_part = parts[1].strip()    # "19 Oct 2025"
        status = parts[2].strip()       # "Book Now"

        # Extract year from end date
        end_date_parts = end_part.split()
        if len(end_date_parts) != 3:
            return None

        year = end_date_parts[2]

        # Construct full date strings
        start_date_str = f"{start_part} {year}"
        end_date_str = end_part

        start_date = parse_json_date(start_date_str)
        end_date = parse_json_date(end_date_str)

        if start_date and end_date:
            return (start_date, end_date, status)

        return None
    except Exception as e:
        print(f"  ⚠️ Error parsing date string '{date_string}': {e}")
        return None


def load_global_prices(global_prices_dir):
    """
    Load global pricing data from CSV files
    Returns dict: {tour_name: {price_GBP: X, price_USD: Y, ...}}
    """
    global_prices = {}

    if not os.path.exists(global_prices_dir):
        print(f"⚠️ Global prices directory not found: {global_prices_dir}")
        return global_prices

    csv_files = list(Path(global_prices_dir).glob("*.csv"))
    print(f"💰 Found {len(csv_files)} global pricing CSV files")

    for csv_file in csv_files:
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    tour_name = row.get('Tour Name', '').strip()
                    if not tour_name:
                        continue

                    # Extract main prices (not deposit)
                    prices = {}
                    for currency in ['USD', 'NZD', 'GBP', 'EUR', 'CAD', 'AUD']:
                        price_val = row.get(f'Main Price {currency}', '')
                        try:
                            prices[f'price_{currency}'] = int(price_val) if price_val else None
                        except:
                            prices[f'price_{currency}'] = None

                    # Store with both original and normalized names
                    global_prices[tour_name] = prices
                    normalized_name = normalize_tour_name(tour_name)
                    if normalized_name != tour_name:
                        global_prices[normalized_name] = prices

            print(f"  ✅ Loaded prices from {csv_file.name}")
        except Exception as e:
            print(f"  ❌ Error loading {csv_file.name}: {e}")

    return global_prices


def load_csv_data(csv_dir):
    """
    Load all CSV files from tourism_api csv/tour_dates directory
    Returns dict: {tour_name: [{date_info}, ...]}
    """
    csv_data = {}

    if not os.path.exists(csv_dir):
        print(f"❌ CSV directory not found: {csv_dir}")
        return csv_data

    csv_files = list(Path(csv_dir).glob("*.csv"))
    print(f"📁 Found {len(csv_files)} tour dates CSV files")

    for csv_file in csv_files:
        # Extract tour name from filename
        # e.g., "Backpacking_Thailand_Expedition.csv" -> "Backpacking Thailand Expedition"
        tour_name = csv_file.stem.replace('_', ' ')

        dates_data = []

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    start_date = parse_csv_date(row.get('Starting Date (DD-MM-YYYY)', ''))
                    end_date = parse_csv_date(row.get('Ending Date (DD-MM-YYYY)', ''))

                    if not start_date or not end_date:
                        continue

                    # Extract available places
                    available_places = row.get('Available Places', '')
                    try:
                        available_places = int(available_places) if available_places else 0
                    except:
                        available_places = 0

                    # Extract prices
                    prices = {
                        'deposit': {
                            'USD': row.get('Deposit Price USD', ''),
                            'NZD': row.get('Deposit Price NZD', ''),
                            'GBP': row.get('Deposit Price GBP', ''),
                            'EUR': row.get('Deposit Price EUR', ''),
                            'CAD': row.get('Deposit Price CAD', ''),
                            'AUD': row.get('Deposit Price AUD', '')
                        },
                        'main': {
                            'USD': row.get('Main Price USD', ''),
                            'NZD': row.get('Main Price NZD', ''),
                            'GBP': row.get('Main Price GBP', ''),
                            'EUR': row.get('Main Price EUR', ''),
                            'CAD': row.get('Main Price CAD', ''),
                            'AUD': row.get('Main Price AUD', '')
                        }
                    }

                    # Convert price strings to integers, handle empty values
                    for price_type in ['deposit', 'main']:
                        for currency in prices[price_type]:
                            val = prices[price_type][currency]
                            try:
                                prices[price_type][currency] = int(val) if val else None
                            except:
                                prices[price_type][currency] = None

                    date_entry = {
                        'start_date': start_date,
                        'end_date': end_date,
                        'available_spaces': available_places,
                        'prices': prices
                    }
                    dates_data.append(date_entry)

            # Store with both original and normalized names for better matching
            csv_data[tour_name] = dates_data
            normalized_name = normalize_tour_name(tour_name)
            if normalized_name != tour_name:
                csv_data[normalized_name] = dates_data
            print(f"  ✅ Loaded {len(dates_data)} dates from {tour_name}")

        except Exception as e:
            print(f"  ❌ Error loading {csv_file.name}: {e}")

    return csv_data


def match_dates(json_date_str, csv_dates):
    """
    Match a JSON date string with CSV date data
    Returns: matched CSV date data or None
    """
    parsed = extract_dates_from_json_string(json_date_str)
    if not parsed:
        return None

    json_start, json_end, status = parsed

    # Find matching date in CSV data
    for csv_date in csv_dates:
        if csv_date['start_date'] == json_start and csv_date['end_date'] == json_end:
            return csv_date

    return None


def enhance_json_with_csv_data(json_file, csv_dir, global_prices_dir, output_file):
    """
    Enhance group_tours_frontend.json with CSV data (dates and global prices)
    """
    print(f"\n🚀 Starting data merge...")
    print(f"   JSON input: {json_file}")
    print(f"   Tour dates CSV directory: {csv_dir}")
    print(f"   Global prices CSV directory: {global_prices_dir}")
    print(f"   Output: {output_file}")

    # Load JSON data
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading JSON file: {e}")
        return False

    # Handle both list and dict formats
    if isinstance(json_data, list):
        tours = json_data
    else:
        tours = json_data.get('tours', [])
    print(f"📊 Loaded {len(tours)} tours from JSON")

    # Load global prices
    global_prices = load_global_prices(global_prices_dir)

    # Load CSV data for dates
    csv_data = load_csv_data(csv_dir)

    # Enhance tours with CSV data
    enhanced_count = 0
    matched_dates_count = 0
    global_prices_count = 0

    for tour in tours:
        tour_name = tour.get('tour_name', '')
        starting_dates = tour.get('starting_dates', [])

        if not tour_name:
            continue

        # Add global prices to tour level
        tour_prices = global_prices.get(tour_name)
        if not tour_prices:
            # Try normalized name
            normalized_name = normalize_tour_name(tour_name)
            tour_prices = global_prices.get(normalized_name)

        if tour_prices:
            tour['price'] = tour_prices
            global_prices_count += 1

        if not starting_dates:
            continue

        # Try to find matching CSV data for dates
        csv_tour_dates = csv_data.get(tour_name)

        # If no exact match, try normalized name
        if not csv_tour_dates:
            normalized_name = normalize_tour_name(tour_name)
            csv_tour_dates = csv_data.get(normalized_name)

        if not csv_tour_dates:
            continue

        # Convert starting_dates from strings to enhanced objects
        enhanced_dates = []

        for date_str in starting_dates:
            # Extract status from date string
            parsed = extract_dates_from_json_string(date_str)
            if not parsed:
                # Keep original format if can't parse
                enhanced_dates.append(date_str)
                continue

            _, _, status = parsed

            # Try to match with CSV data
            csv_match = match_dates(date_str, csv_tour_dates)

            if csv_match:
                enhanced_dates.append({
                    'date': date_str,
                    'status': status,
                    'available_spaces': csv_match['available_spaces'],
                    'prices': csv_match['prices']
                })
                matched_dates_count += 1
            else:
                # No match found, keep basic structure
                enhanced_dates.append({
                    'date': date_str,
                    'status': status,
                    'available_spaces': None,
                    'prices': None
                })

        tour['starting_dates'] = enhanced_dates
        enhanced_count += 1

    # Save enhanced JSON (preserve original format)
    try:
        if isinstance(json_data, list):
            output_data = tours
        else:
            output_data = json_data
            output_data['tours'] = tours

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2)
        print(f"\n✅ Successfully created enhanced JSON")
        print(f"   Added global prices to {global_prices_count} tours")
        print(f"   Enhanced {enhanced_count} tours with date-specific data")
        print(f"   Matched {matched_dates_count} dates with CSV data")
        print(f"   Output: {output_file}")
        return True
    except Exception as e:
        print(f"❌ Error writing output file: {e}")
        return False


def sync_tourism_api_repo():
    """
    Clone or update tourism_api repository from GitHub
    Returns: Tuple of (tour_dates_path, global_prices_path)
    Raises: Exception if sync fails
    """
    # Use authenticated URL for private repository access
    # Get token from environment variable
    github_token = os.environ.get('GITHUB_TOKEN', '')
    if github_token:
        repo_url = f"https://si0411:{github_token}@github.com/si0411/tourism_api.git"
    else:
        repo_url = "https://github.com/si0411/tourism_api.git"
    repo_path = Path("/tmp/tourism_api")
    tour_dates_path = repo_path / "csv" / "tour_dates"
    global_prices_path = repo_path / "csv" / "global_prices"

    try:
        if repo_path.exists():
            # Repository exists, pull latest changes
            print(f"📥 Updating tourism_api repository...")
            result = subprocess.run(
                ["git", "-C", str(repo_path), "pull"],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ Updated: {result.stdout.strip()}")
        else:
            # Clone repository
            print(f"📥 Cloning tourism_api repository from GitHub...")
            result = subprocess.run(
                ["git", "clone", repo_url, str(repo_path)],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ Cloned successfully")

        # Verify CSV directories exist
        if not tour_dates_path.exists():
            print(f"⚠️ Tour dates directory not found at {tour_dates_path}")
        if not global_prices_path.exists():
            print(f"⚠️ Global prices directory not found at {global_prices_path}")

        return tour_dates_path, global_prices_path

    except subprocess.CalledProcessError as e:
        raise Exception(f"Git operation failed: {e.stderr}")
    except Exception as e:
        raise Exception(f"Failed to sync tourism_api repository: {str(e)}")


def main():
    """Main function"""
    # Determine paths
    script_dir = Path(__file__).parent
    json_file = script_dir / "group_tours_frontend.json"
    output_file = script_dir / "group_tours_frontend_enhanced.json"

    # Sync tourism_api repository from GitHub
    try:
        tour_dates_dir, global_prices_dir = sync_tourism_api_repo()
    except Exception as e:
        print(f"❌ {e}")
        return 1

    # Run the merge
    success = enhance_json_with_csv_data(json_file, tour_dates_dir, global_prices_dir, output_file)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
