#!/usr/bin/env python3
"""
Generate HTML email for tours with limited availability
"""

import json
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Configuration
TOUR_DATA_FILE = 'BT_scraping/group_tours_frontend_enhanced.json'
TOUR_IMAGES_FILE = 'BT_scraping/listing_images/grouptour_main_images.json'
LIMITED_SPACES_THRESHOLD = 5  # Tours with 5 or fewer spaces are considered "limited"


def clean_tour_name_for_utm(tour_name: str) -> str:
    """
    Clean tour name for UTM parameter - replace spaces and special characters with underscores
    """
    # Convert to lowercase
    cleaned = tour_name.lower()
    # Replace spaces and special characters with underscores
    cleaned = re.sub(r'[^a-z0-9]+', '_', cleaned)
    # Remove leading/trailing underscores
    cleaned = cleaned.strip('_')
    # Remove consecutive underscores
    cleaned = re.sub(r'_+', '_', cleaned)
    return cleaned


def parse_tour_date(date_string: str) -> Optional[Dict]:
    """
    Parse date string like "20 Oct - 2 Nov 2025 - Book Now"
    Returns dict with start_date, end_date as datetime objects
    """
    try:
        parts = date_string.split(' - ')
        if len(parts) < 3:
            return None

        start_part = parts[0].strip()  # "20 Oct"
        end_part = parts[1].strip()    # "2 Nov 2025"

        # Extract year from end date
        end_date_parts = end_part.split()
        if len(end_date_parts) != 3:
            return None

        year = end_date_parts[2]

        # Parse start date
        start_date_str = f"{start_part} {year}"
        start_date = datetime.strptime(start_date_str, "%d %b %Y")
        end_date = datetime.strptime(end_part, "%d %b %Y")

        return {
            'start_date': start_date,
            'end_date': end_date,
            'start_str': start_date.strftime("%d %b"),
            'end_str': end_date.strftime("%d %b %Y")
        }
    except Exception as e:
        print(f"Error parsing date '{date_string}': {e}")
        return None


def get_limited_availability_tours() -> List[Dict]:
    """
    Get all tours with limited availability (upcoming tours only)
    """
    # Load tour data
    with open(TOUR_DATA_FILE, 'r') as f:
        data = json.load(f)

    # Load tour images
    tour_images = {}
    try:
        with open(TOUR_IMAGES_FILE, 'r') as f:
            images_data = json.load(f)
            for item in images_data:
                tour_images[item['tour_name']] = item['image_url']
    except FileNotFoundError:
        print("Warning: Tour images file not found")

    tours = data.get('tours', [])
    today = datetime.now()

    print(f"Searching for all upcoming tours with limited availability...")

    limited_tours = []

    for tour in tours:
        tour_name = tour.get('tour_name', 'Unknown Tour')
        tour_url = tour.get('url', '')
        tour_color = tour.get('tour_colour', '#6c49ff')

        # Get tour image from images JSON, with imgix optimization for email (600x337 for 20:11.23 ratio)
        tour_image = tour_images.get(tour_name, '')
        if tour_image:
            tour_image = f"{tour_image}?w=600&h=337&fit=crop&auto=format"

        starting_dates = tour.get('starting_dates', [])

        limited_dates = []

        for date_info in starting_dates:
            if isinstance(date_info, dict):
                date_string = date_info.get('date', '')
                available_spaces = date_info.get('available_spaces')

                # Skip if spaces is None, 0, negative, or > threshold
                if available_spaces is None or available_spaces <= 0 or available_spaces > LIMITED_SPACES_THRESHOLD:
                    continue

                # Parse date
                parsed = parse_tour_date(date_string)
                if not parsed:
                    continue

                # Only include future tours
                if parsed['start_date'] >= today:
                    limited_dates.append({
                        'start_str': parsed['start_str'],
                        'end_str': parsed['end_str'],
                        'available_spaces': available_spaces,
                        'date_string': date_string
                    })

        if limited_dates:
            limited_tours.append({
                'tour_name': tour_name,
                'tour_url': tour_url,
                'tour_color': tour_color,
                'tour_image': tour_image,
                'dates': limited_dates
            })

    print(f"Found {len(limited_tours)} tours with limited availability")
    return limited_tours


def generate_email_html(tours: List[Dict]) -> str:
    """
    Generate HTML email template with mobile-friendly design
    """
    if not tours:
        return "<p>No tours with limited availability found.</p>"

    # Determine server URL for assets (will work both locally and on server)
    base_url = "https://simbro.app"

    # Email-safe HTML with inline styles and table-based layout
    html = f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Don't Miss Out – Last Seats Available!</title>
    <style type="text/css">
        @media only screen and (max-width: 600px) {{
            .tour-image {{ width: 100% !important; height: auto !important; }}
            .tour-content {{ padding: 15px !important; }}
            .header-title {{ font-size: 22px !important; }}
            .tour-name {{ font-size: 18px !important; }}
            .logo {{ max-width: 150px !important; }}
        }}
    </style>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;">
    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f4f4f4;">
        <tr>
            <td align="center" style="padding: 20px 10px;">
                <!-- Main Container -->
                <table border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff; max-width: 600px;">

                    <!-- Header with Logo -->
                    <tr>
                        <td align="center" style="padding: 30px 30px 20px 30px; background-color: #6c49ff;">
                            <a href="https://www.backpackingtours.com/?utm_medium=email&utm_campaign=lastfewspaces&utm_content=logo" style="display: block; text-decoration: none;">
                                <img src="{base_url}/assets/BT_Logo_White.png" alt="Backpacking Tours" class="logo" width="180" style="display: block; max-width: 180px; height: auto; margin: 0 auto;" />
                            </a>
                        </td>
                    </tr>

                    <!-- Header Text -->
                    <tr>
                        <td align="center" style="padding: 20px 30px 30px 30px; background-color: #6c49ff;">
                            <h1 class="header-title" style="color: #ffffff; font-size: 26px; margin: 0 0 12px 0; font-weight: 700; line-height: 1.2;">
                                🔥 Don't Miss Out – Last Seats Available
                            </h1>
                            <p style="color: #ffffff; font-size: 15px; margin: 0 0 12px 0; line-height: 1.6;">
                                Don't miss your chance to explore with us! Our next tours are filling up fast, and there are only a few spaces remaining. Check out the list below to see which trips still have availability and secure your spot before they're gone.
                            </p>
                            <p style="color: #ffffff; font-size: 15px; margin: 0; line-height: 1.6;">
                                Check out all our tours over at <a href="https://www.backpackingtours.com/?utm_medium=email&utm_campaign=lastfewspaces&utm_content=header_text" style="color: #ffffff; text-decoration: underline;">Backpacking Tours</a> and our latest <a href="https://www.backpackingtours.com/tour-deals?utm_medium=email&utm_campaign=lastfewspaces&utm_content=special_offers" style="color: #ffffff; text-decoration: underline;">special offers</a>.
                            </p>
                        </td>
                    </tr>

                    <!-- Tours Section -->
                    <tr>
                        <td style="padding-top: 30px; padding-bottom: 0; padding-left: 0; padding-right: 0;">
"""

    # Generate tour cards
    for tour in tours:
        tour_name = tour['tour_name']
        tour_url = tour['tour_url']
        tour_color = tour['tour_color']
        tour_image = tour.get('tour_image', '')
        dates = tour['dates']

        # Add UTM parameters to tour URL (clean tour name for utm_content)
        utm_content = clean_tour_name_for_utm(tour_name)
        separator = '&' if '?' in tour_url else '?'
        tour_url_with_utm = f"{tour_url}{separator}utm_medium=email&utm_campaign=lastfewspaces&utm_content={utm_content}"

        # Use a placeholder image if no tour image available
        image_url = tour_image if tour_image else 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=600&h=337&fit=crop'

        html += f"""
                            <!-- Tour Card -->
                            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 25px;">
                                <!-- Tour Image -->
                                <tr>
                                    <td style="padding: 0; line-height: 0;">
                                        <a href="{tour_url_with_utm}" style="text-decoration: none;">
                                            <img class="tour-image" src="{image_url}" alt="{tour_name}" width="600" height="337" style="display: block; height: auto; border: none;" />
                                        </a>
                                    </td>
                                </tr>

                                <!-- Color Bar -->
                                <tr>
                                    <td style="padding: 0; line-height: 0;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="600" style="border-collapse: collapse;">
                                            <tr>
                                                <td height="4" style="background-color: {tour_color}; font-size: 0; line-height: 0;">&nbsp;</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>

                                <!-- Tour Content -->
                                <tr>
                                    <td class="tour-content" style="padding: 20px; background-color: #ffffff;">
                                        <!-- Tour Name with Color Dot -->
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                            <tr>
                                                <td style="padding-bottom: 15px;">
                                                    <h2 class="tour-name" style="margin: 0; font-size: 20px; color: #1a1a1a; font-weight: 700; line-height: 1.3;">
                                                        <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background-color: {tour_color}; margin-right: 8px; vertical-align: middle;"></span>
                                                        {tour_name}
                                                    </h2>
                                                </td>
                                            </tr>
                                        </table>

                                        <!-- Available Dates -->
"""

        for date in dates:
            spaces = date['available_spaces']
            badge_color = '#ff4444' if spaces <= 2 else '#ff8800'
            spaces_text = f"{spaces} space left" if spaces == 1 else f"{spaces} spaces left"

            html += f"""
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 8px;">
                                            <tr>
                                                <td style="padding: 12px; background-color: #f8f9fa;">
                                                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                                        <tr>
                                                            <td style="font-size: 15px; color: #333333; font-weight: 500;">
                                                                {date['start_str']} - {date['end_str']}
                                                            </td>
                                                            <td align="right" style="padding-left: 10px;">
                                                                <span style="background-color: {badge_color}; color: #ffffff; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 700; white-space: nowrap; display: inline-block;">
                                                                    {spaces_text}
                                                                </span>
                                                            </td>
                                                        </tr>
                                                    </table>
                                                </td>
                                            </tr>
                                        </table>
"""

        html += f"""
                                        <!-- Book Now Button -->
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-top: 15px;">
                                            <tr>
                                                <td align="center">
                                                    <a href="{tour_url_with_utm}" style="display: inline-block; background-color: {tour_color}; color: #ffffff; text-decoration: none; padding: 14px 35px; font-weight: 700; font-size: 16px;">
                                                        Book Now →
                                                    </a>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
"""

    # Footer with social media icons
    html += f"""
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px 20px; background-color: #f8f9fa; text-align: center; border-top: 1px solid #e0e0e0;">
                            <p style="margin: 0 0 20px 0; font-size: 16px; color: #1a1a1a; font-weight: 700;">
                                <a href="https://www.backpackingtours.com/?utm_medium=email&utm_campaign=lastfewspaces&utm_content=footer" style="color: #1a1a1a; text-decoration: none;">Backpacking Tours</a>
                            </p>

                            <!-- Social Media Icons -->
                            <table border="0" cellpadding="0" cellspacing="0" align="center" style="margin: 0 auto 20px auto;">
                                <tr>
                                    <td style="padding: 0 10px;">
                                        <a href="https://www.facebook.com/backpackingtours" target="_blank">
                                            <img src="{base_url}/assets/fb_icon.png" alt="Facebook" width="32" height="32" style="display: block; border: none;" />
                                        </a>
                                    </td>
                                    <td style="padding: 0 10px;">
                                        <a href="https://www.instagram.com/backpackingtours" target="_blank">
                                            <img src="{base_url}/assets/ig_icon.png" alt="Instagram" width="32" height="32" style="display: block; border: none;" />
                                        </a>
                                    </td>
                                    <td style="padding: 0 10px;">
                                        <a href="https://www.tiktok.com/@backpackingtours?lang=en" target="_blank">
                                            <img src="{base_url}/assets/tiktok_icon.png" alt="TikTok" width="32" height="32" style="display: block; border: none;" />
                                        </a>
                                    </td>
                                </tr>
                            </table>

                            <!-- Unsubscribe and Sender Info -->
                            <p style="margin: 0 0 10px 0; font-size: 12px; color: #999999;">
                                <a href="{{{{UnsubscribeURL}}}}" style="color: #999999; text-decoration: underline;">Unsubscribe</a>
                            </p>
                            <p style="margin: 0; font-size: 12px; color: #999999;">
                                {{{{SenderInfo}}}}
                            </p>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

    return html


def save_html_file(html_content: str, filename: str = None):
    """
    Save HTML file with timestamped filename
    """
    if filename is None:
        # Generate timestamped filename
        timestamp = datetime.now().strftime('%Y%m%d')
        filename = f'limited_availability_email_{timestamp}.html'

    with open(filename, 'w') as f:
        f.write(html_content)

    abs_path = os.path.abspath(filename)
    print(f"✅ Email HTML saved to: {filename}")
    print(f"   Full path: {abs_path}")
    print(f"   Open in browser: file://{abs_path}")
    print()
    print("📋 Copy the HTML from this file and paste it into Email Octopus")


def main():
    print("=" * 60)
    print("Limited Availability Email Generator")
    print("=" * 60)
    print()

    # Get tours with limited availability
    tours = get_limited_availability_tours()

    if not tours:
        print("⚠️  No tours with limited availability found.")
        print("   Make sure the tour data file exists and has tours with ≤5 spaces")
        return

    # Generate email HTML
    html_content = generate_email_html(tours)

    # Save HTML file
    save_html_file(html_content)

    print()
    print("✅ Done! You can now:")
    print("   1. Open the HTML file in your browser to preview")
    print("   2. Copy the HTML code and paste it into Email Octopus")


if __name__ == '__main__':
    main()
