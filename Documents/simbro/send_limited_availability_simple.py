#!/usr/bin/env python3
"""
Simple version: Generate HTML email and provide manual sending instructions
"""

import json
import os
import sys
import webbrowser
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Configuration
TOUR_DATA_FILE = 'BT_scraping/group_tours_frontend_enhanced.json'
LIMITED_SPACES_THRESHOLD = 5


def parse_tour_date(date_string: str) -> Optional[Dict]:
    """Parse tour date string"""
    try:
        parts = date_string.split(' - ')
        if len(parts) < 3:
            return None

        start_part = parts[0].strip()
        end_part = parts[1].strip()

        end_date_parts = end_part.split()
        if len(end_date_parts) != 3:
            return None

        year = end_date_parts[2]
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
        return None


def get_limited_availability_tours() -> List[Dict]:
    """Get all tours with limited availability (upcoming tours only)"""
    with open(TOUR_DATA_FILE, 'r') as f:
        data = json.load(f)

    tours = data.get('tours', [])
    today = datetime.now()

    print(f"📅 Searching for all upcoming tours with limited availability...")

    limited_tours = []

    for tour in tours:
        tour_name = tour.get('tour_name', 'Unknown Tour')
        tour_url = tour.get('url', '')
        tour_color = tour.get('tour_colour', '#6c49ff')
        starting_dates = tour.get('starting_dates', [])

        limited_dates = []

        for date_info in starting_dates:
            if isinstance(date_info, dict):
                date_string = date_info.get('date', '')
                available_spaces = date_info.get('available_spaces')

                # Only include tours with 1-5 spaces (exclude null/0)
                if available_spaces is None or available_spaces == 0 or available_spaces > LIMITED_SPACES_THRESHOLD:
                    continue

                parsed = parse_tour_date(date_string)
                if not parsed:
                    continue

                # Only include future tours (no date range restriction)
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
                'dates': limited_dates
            })

    print(f"✅ Found {len(limited_tours)} tours with limited availability\n")
    return limited_tours


def generate_email_html(tours: List[Dict]) -> str:
    """Generate beautiful HTML email following email best practices"""
    next_month = (datetime.now().replace(day=1) + timedelta(days=32)).strftime('%B %Y')

    html = f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Limited Availability - {next_month}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f8f9fa; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;">
    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f8f9fa;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table border="0" cellpadding="0" cellspacing="0" width="800" style="background-color: #ffffff; border-radius: 10px; max-width: 800px;">
                    <!-- Header -->
                    <tr>
                        <td align="center" style="padding: 40px 30px 30px 30px;">
                            <h1 style="margin: 0; color: #1a1a1a; font-size: 32px; font-weight: 600; line-height: 1.3;">🔥 Don't Miss Out – Last Seats Available</h1>
                            <p style="margin: 15px 0 0 0; color: #666; font-size: 16px; line-height: 1.6;">Don't miss your chance to explore with us! Our next tours are filling up fast, and there are only a few spaces remaining. Check out the list below to see which trips still have availability and secure your spot before they're gone.</p>
                        </td>
                    </tr>

                    <!-- Tours -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px;">
"""

    for tour in tours:
        tour_color = tour['tour_color']
        tour_name = tour['tour_name']
        tour_url = tour['tour_url']

        html += f"""
                            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f7f8fa; border-left: 4px solid {tour_color}; border-radius: 8px; margin-bottom: 20px;">
                                <tr>
                                    <td style="padding: 20px;">
                                        <!-- Tour Title -->
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                            <tr>
                                                <td style="padding-bottom: 15px;">
                                                    <table border="0" cellpadding="0" cellspacing="0">
                                                        <tr>
                                                            <td style="padding-right: 15px; vertical-align: middle;">
                                                                <div style="width: 16px; height: 16px; border-radius: 50%; background-color: {tour_color};"></div>
                                                            </td>
                                                            <td style="vertical-align: middle;">
                                                                <h2 style="margin: 0; font-size: 22px; font-weight: 600; color: #1a1a1a; line-height: 1.4;">{tour_name}</h2>
                                                            </td>
                                                        </tr>
                                                    </table>
                                                </td>
                                            </tr>
                                        </table>
"""

        # Add dates
        for date in tour['dates']:
            spaces = date['available_spaces']
            badge_color = '#ffa500' if spaces > 2 else '#ff6b6b'
            spaces_text = f"{spaces} space left" if spaces == 1 else f"{spaces} spaces left"

            html += f"""
                                        <!-- Date Item -->
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #ffffff; border-radius: 6px; margin-bottom: 10px;">
                                            <tr>
                                                <td style="padding: 12px 15px;">
                                                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                                        <tr>
                                                            <td style="color: #333; font-size: 15px; font-weight: 500;">
                                                                {date['start_str']} - {date['end_str']}
                                                            </td>
                                                            <td align="right" style="white-space: nowrap;">
                                                                <span style="background-color: {badge_color}; color: #ffffff; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; display: inline-block;">{spaces_text}</span>
                                                            </td>
                                                        </tr>
                                                    </table>
                                                </td>
                                            </tr>
                                        </table>
"""

        # Book Now button
        html += f"""
                                        <!-- Book Now Button -->
                                        <table border="0" cellpadding="0" cellspacing="0" style="margin-top: 15px;">
                                            <tr>
                                                <td align="center" style="border-radius: 6px; background-color: #6c49ff;">
                                                    <a href="{tour_url}" target="_blank" style="display: inline-block; padding: 12px 30px; font-size: 16px; color: #ffffff; text-decoration: none; font-weight: 600; border-radius: 6px;">Book Now →</a>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
"""

    html += """
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td align="center" style="padding: 20px 30px 30px 30px; border-top: 1px solid #e0e0e0;">
                            <p style="margin: 0 0 10px 0; color: #1a1a1a; font-size: 16px; font-weight: 600;">Backpacking Tours</p>
                            <p style="margin: 0 0 15px 0; color: #666; font-size: 14px;">Creating unforgettable adventures around the world</p>
                            <p style="margin: 15px 0 5px 0; color: #999; font-size: 12px; line-height: 1.6;">{{SenderInfo}}</p>
                            <p style="margin: 10px 0 0 0; font-size: 12px;">
                                <a href="{{UnsubscribeURL}}" style="color: #999; text-decoration: underline;">Unsubscribe</a>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
    return html


def main():
    print("=" * 60)
    print("🎯 Limited Availability Email Generator")
    print("=" * 60)
    print()

    tours = get_limited_availability_tours()

    if not tours:
        print("⚠️  No tours with limited availability for next month")
        tours = [{
            'tour_name': 'Sample - Backpacking Thailand',
            'tour_url': 'https://www.backpackingtours.com',
            'tour_color': '#6c49ff',
            'dates': [{'start_str': '15 Nov', 'end_str': '28 Nov 2025', 'available_spaces': 2}]
        }]

    html_content = generate_email_html(tours)

    filename = f'limited_availability_email_{datetime.now().strftime("%Y%m%d")}.html'
    with open(filename, 'w') as f:
        f.write(html_content)

    print(f"✅ Email saved to: {filename}")
    print(f"📂 Full path: {os.path.abspath(filename)}\n")

    print("📧 Next Steps:")
    print("─" * 60)
    print("1. Open the HTML file in your browser to preview")
    print("2. Go to https://emailoctopus.com/dashboard")
    print("3. Click 'Campaigns' → 'Create Campaign'")
    print("4. Choose 'Regular Campaign'")
    print("5. Design: Copy/paste the HTML from the file")
    print("6. Select your email list")
    print("7. Send or schedule the campaign")
    print("─" * 60)

    webbrowser.open(f'file://{os.path.abspath(filename)}')
    print("\n✅ Opening preview in your browser...")


if __name__ == '__main__':
    main()
