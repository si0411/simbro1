#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
import re
import time
import sys

def extract_tour_name(soup):
    """Extract tour name from the page"""
    # Try h1.headline-2 first
    title_elem = soup.find('h1', class_='headline-2')
    if title_elem:
        return title_elem.get_text(strip=True)

    # Fallback to any h1
    h1_elem = soup.find('h1')
    if h1_elem:
        return h1_elem.get_text(strip=True)

    return "Unknown Tour"

def clean_image_url(url):
    """Clean and normalize image URL"""
    if not url:
        return ""

    # Remove query parameters
    clean_url = url.split('?')[0].split('#')[0]

    # Filter out non-image files like SVGs, icons, etc.
    if any(pattern in clean_url.lower() for pattern in ['/arrow-', '/icon-', '.svg']):
        return ""

    # Ensure it starts with /
    if clean_url.startswith('https://') or clean_url.startswith('http://'):
        # Extract path from full URL
        try:
            from urllib.parse import urlparse
            parsed = urlparse(clean_url)
            clean_url = parsed.path
        except:
            pass

    if not clean_url.startswith('/'):
        clean_url = '/' + clean_url

    return clean_url

def get_image_src(img):
    """Get image source from various attributes"""
    return (img.get('src') or
            img.get('data-src') or
            img.get('data-lazy-src') or
            img.get('data-original') or
            img.get('data-lazy') or
            extract_from_style_background(img))

def extract_from_style_background(element):
    """Extract image from CSS background-image"""
    style = element.get('style', '')
    bg_match = re.search(r'background-image:\s*url\([\'"]?([^\'")]+)[\'"]?\)', style)
    return bg_match.group(1) if bg_match else None

def scrape_itinerary_images(soup):
    """
    Scrape itinerary images using DOM structure - prioritize individual day containers
    """
    itinerary_images = {}

    print("Looking for itinerary day structures...", file=sys.stderr)

    # First, let's see what images are actually on the page
    all_imgs = soup.find_all('img')
    imgix_imgs = [img for img in all_imgs if img.get('src') and 'imgix.net' in img.get('src')]
    print(f"DEBUG: Found {len(all_imgs)} total images, {len(imgix_imgs)} imgix images", file=sys.stderr)

    # Check for the specific images mentioned by user in various attributes
    def find_img_in_attrs(filename):
        for img in all_imgs:
            for attr in ['src', 'data-src', 'data-lazy-src', 'data-original', 'data-lazy']:
                value = img.get(attr) or ''
                if filename in value:
                    return True, attr
        return False, None

    day1_img1, attr1 = find_img_in_attrs('srilanka-adobestock50_mpypq.png')
    day1_img2, attr2 = find_img_in_attrs('beaconbeachnegombo1_obvfw.jpg')
    day2_img1, attr3 = find_img_in_attrs('pidurangala2_qfxkk.jpg')
    print(f"DEBUG: Specific images found - Day1 img1: {day1_img1} ({attr1}), Day1 img2: {day1_img2} ({attr2}), Day2 img1: {day2_img1} ({attr3})", file=sys.stderr)

    # Also check what imgix images we do have
    sample_imgix = [img.get('src')[:100] + '...' for img in imgix_imgs[:3]]
    print(f"DEBUG: Sample imgix URLs: {sample_imgix}", file=sys.stderr)

    # Method 1: Look for individual day containers/sections
    # Find all day spans to understand the structure
    day_spans = soup.find_all('span', class_=re.compile(r'card__content-day\s+bg-'))
    print(f"Found {len(day_spans)} day indicator spans", file=sys.stderr)

    for day_span in day_spans:
        day_text = day_span.get_text(strip=True)  # "DAY 1"
        day_match = re.search(r'DAY\s+(\d+)', day_text, re.IGNORECASE)
        if day_match:
            day_number = int(day_match.group(1))
            day_key = f"Day {day_number}"

            print(f"Processing {day_key}...", file=sys.stderr)

            # Strategy 1: Find the nearest image-containing container
            day_images = []

            # Look for the closest parent container that has images
            current_element = day_span
            for level in range(5):  # Go up 5 levels max
                parent = current_element.find_parent()
                if not parent:
                    break

                # Check if this parent has images
                parent_images = parent.find_all('img')
                if parent_images:
                    print(f"  Found {len(parent_images)} images at level {level} for {day_key}", file=sys.stderr)

                    # Debug: Check what images we're finding
                    img_with_data_src = [img for img in parent_images if img.get('data-src')]
                    print(f"  Images with data-src: {len(img_with_data_src)}", file=sys.stderr)

                    if day_key == "Day 1" and level <= 2:  # Debug Day 1 specifically
                        for i, img in enumerate(parent_images[:3]):
                            src = get_image_src(img)
                            print(f"    Img {i}: src='{src[:50] if src else None}...', data-src='{img.get('data-src', '')[:50]}...'", file=sys.stderr)

                    # Take images from the first level where we find a reasonable number
                    # Avoid levels with too many images (like level 3+ with 57 images)
                    if level <= 2 and len(parent_images) <= 10:  # Reasonable number of images
                        for img in parent_images:
                            src = get_image_src(img)
                            if src:
                                clean_src = clean_image_url(src)
                                if clean_src:
                                    alt_text = img.get('alt', '')
                                    if not any(item['url'] == clean_src for item in day_images):
                                        day_images.append({
                                            'url': clean_src,
                                            'alt': alt_text
                                        })

                        # If we found images at this level, stop going further up
                        if day_images:
                            print(f"  {day_key}: Captured {len(day_images)} images from level {level}", file=sys.stderr)
                            break

                current_element = parent

            # Strategy 2: If no images found yet, look for next siblings that contain images
            if not day_images:
                day_container = day_span.find_parent(['div', 'section', 'article'])
                if day_container:
                    # Look in following siblings for images
                    for sibling in day_container.find_next_siblings(['div', 'section']):
                        # Stop if we hit another day indicator
                        if sibling.find('span', class_='card__content-day'):
                            break

                        sibling_images = sibling.find_all('img')
                        for img in sibling_images:
                            src = get_image_src(img)
                            if src:
                                clean_src = clean_image_url(src)
                                if clean_src:
                                    alt_text = img.get('alt', '')
                                    if not any(item['url'] == clean_src for item in day_images):
                                        day_images.append({
                                            'url': clean_src,
                                            'alt': alt_text
                                        })

                        # Limit images per day to avoid taking too many
                        if len(day_images) >= 5:
                            break

            if day_images:
                itinerary_images[day_key] = day_images
                print(f"  {day_key}: {len(day_images)} images captured", file=sys.stderr)
            else:
                print(f"  {day_key}: No images found", file=sys.stderr)

    # Method 2: If we didn't get good results, try swiper container approach
    if len(itinerary_images) < len(day_spans) * 0.5:  # If we got less than half the expected days
        print("Low capture rate, trying swiper container approach...", file=sys.stderr)

        # Look for swiper wrapper and slides
        swiper_wrapper = soup.find('div', class_=re.compile(r'swiper-wrapper'))
        if swiper_wrapper:
            swiper_slides = swiper_wrapper.find_all('div', class_=re.compile(r'swiper-slide'))
            print(f"Found {len(swiper_slides)} swiper slides", file=sys.stderr)

            # Try to map slides to days based on position and content
            for i, slide in enumerate(swiper_slides):
                # Try to find day information within the slide
                day_spans_in_slide = slide.find_all('span', class_=re.compile(r'card__content-day\s+bg-'))

                if day_spans_in_slide:
                    for day_span in day_spans_in_slide:
                        day_text = day_span.get_text(strip=True)
                        day_match = re.search(r'DAY\s+(\d+)', day_text, re.IGNORECASE)
                        if day_match:
                            day_number = int(day_match.group(1))
                            day_key = f"Day {day_number}"

                            # Get all images in this slide
                            slide_images = []
                            for img in slide.find_all('img'):
                                src = get_image_src(img)
                                if src:
                                    clean_src = clean_image_url(src)
                                    if clean_src:
                                        alt_text = img.get('alt', '')
                                        slide_images.append({
                                            'url': clean_src,
                                            'alt': alt_text
                                        })

                            if slide_images:
                                itinerary_images[day_key] = slide_images
                                print(f"  Swiper {day_key}: {len(slide_images)} images", file=sys.stderr)

    print(f"Found itinerary images for {len(itinerary_images)} days", file=sys.stderr)
    for day, images in itinerary_images.items():
        print(f"  {day}: {len(images)} images", file=sys.stderr)

    return itinerary_images

def parse_day_button_info(button):
    """Parse day and type from button onclick attribute"""
    onclick = button.get('onclick', '')
    # Extract: App.changeDay(this, 1, 'activities') -> day=1, type='activities'
    day_match = re.search(r'App\.changeDay\(this,\s*(\d+),\s*[\'"](\w+)[\'"]', onclick)
    if day_match:
        return {
            'day_number': int(day_match.group(1)),
            'image_type': day_match.group(2),  # 'activities' or 'accommodation'
            'key': f"Day {day_match.group(1)}"
        }
    return None

def find_gallery_images_by_dom_structure(soup):
    """Find gallery images by parsing js-thumb-button elements with data attributes"""
    gallery_images = {}

    # Find all thumbnail buttons that contain image data
    thumb_buttons = soup.find_all('button', class_='js-thumb-button')
    print(f"Found {len(thumb_buttons)} thumbnail buttons", file=sys.stderr)

    for button in thumb_buttons:
        onclick = button.get('onclick', '')
        img_url = button.get('data-popup-img-url', '')
        description = button.get('data-description', '')

        if not onclick or not img_url:
            continue

        # Parse: App.updatePreview(this, 'activities', 2)
        # The third parameter is the day number
        # The second parameter is the type (activities or accommodation)
        match = re.search(r"App\.updatePreview\(this,\s*['\"](\w+)['\"]\s*,\s*(\d+)\)", onclick)

        if match:
            image_type = match.group(1)  # 'activities' or 'accommodation'
            day_number = int(match.group(2))
            day_key = f"Day {day_number}"

            if day_key not in gallery_images:
                gallery_images[day_key] = []

            # Check if this URL is already in the list for this day
            if not any(item['url'] == img_url for item in gallery_images[day_key]):
                gallery_images[day_key].append({
                    'url': img_url,
                    'description': description,
                    'type': image_type
                })
                print(f"  {day_key} ({image_type}): {description[:50]}...", file=sys.stderr)

    return gallery_images

def scrape_gallery_images(tour_url, headers):
    """
    Scrape gallery images using DOM structure - look for js-day-button elements
    """
    # Construct gallery URL from tour URL
    gallery_url = tour_url.rstrip('/') + '/gallery'

    print(f"Fetching gallery page: {gallery_url}", file=sys.stderr)

    try:
        response = requests.get(gallery_url, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"Gallery page not found (404), skipping gallery", file=sys.stderr)
            return {}

        soup = BeautifulSoup(response.content, 'html.parser')

        # Use new DOM structure-based approach
        gallery_images = find_gallery_images_by_dom_structure(soup)

        print(f"Found gallery images for {len(gallery_images)} days", file=sys.stderr)
        for day, images in gallery_images.items():
            print(f"  {day}: {len(images)} images", file=sys.stderr)

        return gallery_images

    except requests.RequestException as e:
        print(f"Error fetching gallery page: {e}", file=sys.stderr)
        return {}

def clean_and_format_images(images_dict):
    """Format images for output"""
    formatted = {}

    for day, images in images_dict.items():
        if not images:
            continue

        unique_urls = []
        full_urls = []
        descriptions = []
        image_types = []

        for img in images:
            url = img['url'] if isinstance(img, dict) else img
            description = img.get('description', img.get('alt', '')) if isinstance(img, dict) else ''
            img_type = img.get('type', '') if isinstance(img, dict) else ''

            if url and url not in unique_urls:
                unique_urls.append(url)
                # Handle both relative and absolute URLs
                if url.startswith('http'):
                    full_urls.append(url)
                else:
                    full_urls.append('https://www.backpackingtours.com' + url)
                descriptions.append(description)
                image_types.append(img_type)

        if unique_urls:
            formatted[day] = {
                'relative': unique_urls,
                'full_URL': full_urls,
                'description': descriptions,
                'type': image_types
            }

    return formatted

def scrape_tour_data(url):
    """
    Main function to scrape tour data
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        print(f"Fetching tour page: {url}", file=sys.stderr)
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract tour name
        tour_name = extract_tour_name(soup)
        print(f"Tour name: {tour_name}", file=sys.stderr)

        # Scrape itinerary images from main page
        itinerary_images = scrape_itinerary_images(soup)

        # Scrape gallery images from gallery page
        gallery_images = scrape_gallery_images(url, headers)

        return {
            'tour_name': tour_name,
            'url': url,
            'itinerary': clean_and_format_images(itinerary_images),
            'gallery': clean_and_format_images(gallery_images)
        }

    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"Error processing {url}: {e}", file=sys.stderr)
        return {}

def scrape_single_tour_images(url):
    """
    Scrape images from a single tour URL
    Returns JSON data suitable for web API
    """
    try:
        tour_data = scrape_tour_data(url)

        if tour_data and (tour_data.get('itinerary') or tour_data.get('gallery')):
            return {
                'success': True,
                'tour_name': tour_data.get('tour_name', 'Unknown Tour'),
                'url': tour_data['url'],
                'itinerary': tour_data.get('itinerary', {}),
                'gallery': tour_data.get('gallery', {})
            }
        else:
            return {
                'success': False,
                'error': 'No images found for this tour'
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Single tour mode - scrape one tour
        url = sys.argv[1]
        result = scrape_single_tour_images(url)
        # Only output JSON to stdout, no debug info
        print(json.dumps(result))
    else:
        print("Usage: python3 scrape_all_images.py <tour_url>", file=sys.stderr)
        sys.exit(1)