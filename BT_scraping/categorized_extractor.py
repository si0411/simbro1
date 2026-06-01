#!/usr/bin/env python3
"""
Comprehensive tour data extraction organized into categories:
- Tour Information
- Itinerary  
- Starting Dates
- Price

Enhanced with data validation, type conversion, and quality improvements.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime
import hashlib

class CategorizedTourExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def extract_tour_data(self, url):
        """Extract comprehensive tour data organized by categories"""
        try:
            print(f"Processing: {url}")
            
            # Initialize enhanced categorized data structure
            tour_data = {
                'tour_name': '',
                'tour_id': '',  # Will be generated from URL
                'url': url,
                'country': '',  # Will be extracted from articles section
                'last_updated': datetime.now().strftime('%Y-%m-%d'),
                'status': 'active',
                'tour_colour': '',  # Single hex color for the tour
                'seo_data': {
                    'meta_title': '',
                    'meta_description': '',
                    'meta_keywords': '',
                    'open_graph': {}
                },
                'tour_information': {
                    'description': '',
                    'duration': {
                        'days': 0,
                        'display': ''
                    },
                    'age_range': {
                        'min': 0,
                        'max': 0,
                        'display': ''
                    },
                    'num_activities': 0,
                    'num_meals': 0,
                    'avg_group_size': '',
                    'operator': '',
                    'starting_point': '',
                    'ending_point': '',
                    'num_reviews': 0,
                    'included_items': [],
                    'excluded_items': [],
                    'activities_incl': []
                },
                'itinerary': {},
                'starting_dates': [],
                'price': {
                    'price_GBP': 0,
                    'price_USD': 0,
                    'price_EUR': 0,
                    'price_CAD': 0,
                    'price_AUD': 0,
                    'price_NZD': 0
                }
            }
            
            # Get the page with default currency
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Generate tour ID from URL
            tour_data['tour_id'] = self._generate_tour_id(url)
            
            # Extract all data
            self._extract_tour_information(soup, tour_data)
            self._extract_seo_data(soup, tour_data)
            self._extract_tour_colour(soup, tour_data)
            self._extract_detailed_itinerary(soup, tour_data)
            self._extract_tour_dates(url, tour_data)
            self._extract_all_currency_prices(url, tour_data)
            
            # Validate and clean data
            self._validate_and_clean_data(tour_data)
            
            return tour_data
            
        except Exception as e:
            print(f"Error processing {url}: {e}")
            return {'url': url, 'error': str(e)}
    
    def _extract_tour_information(self, soup, tour_data):
        """Extract all tour information data"""
        
        tour_info = tour_data['tour_information']
        
        # Extract tour name with improved logic
        self._extract_tour_name(soup, tour_data)
        
        # Extract structured tour info from HTML elements
        tour_info_items = soup.find_all('div', class_='list-tour-info__item-desc')
        for item in tour_info_items:
            bold = item.find('b')
            span = item.find('span')
            
            if bold and span:
                key_text = bold.get_text().strip()
                value = span.get_text().strip()
                self._assign_tour_info_value(key_text, value, tour_info)
        
        # Extract description
        self._extract_description(soup, tour_info)
        
        # Extract reviews count
        self._extract_reviews(soup, tour_info)
        
        # Extract included/excluded items
        self._extract_included_excluded(soup, tour_info)
        
        # Extract activities included list
        self._extract_activities_included(soup, tour_info)
        
        # Extract country from articles section
        self._extract_country_from_articles(soup, tour_data)
    
    def _assign_tour_info_value(self, key, value, tour_info):
        """Assign tour information values with type conversion"""
        key_lower = key.lower().strip()
        
        if 'activities' in key_lower and 'no' in key_lower:
            tour_info['num_activities'] = self._extract_number(value)
        elif 'meals' in key_lower and 'no' in key_lower:
            tour_info['num_meals'] = self._extract_number(value)
        elif 'operator' in key_lower:
            tour_info['operator'] = value
        elif 'starting point' in key_lower:
            tour_info['starting_point'] = value
        elif 'ending point' in key_lower:
            tour_info['ending_point'] = value
        elif 'length' in key_lower:
            self._parse_duration(value, tour_info)
        elif 'age' in key_lower and 'avg' in key_lower:
            self._parse_age_range(value, tour_info)
        elif 'group size' in key_lower and 'avg' in key_lower:
            tour_info['avg_group_size'] = value
    
    def _extract_description(self, soup, tour_info):
        """Extract tour description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            desc = meta_desc.get('content', '').strip()
            if len(desc) > 50:
                tour_info['description'] = desc
                return
        
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text().strip()
            if (len(text) > 100 and len(text) < 1000 and 
                not any(skip in text.lower() for skip in ['cookie', 'privacy', 'license', 'terms', 'copyright'])):
                tour_info['description'] = text
                break
    
    def _extract_reviews(self, soup, tour_info):
        """Extract number of reviews"""
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and 'aggregateRating' in data:
                    review_count = data['aggregateRating'].get('reviewCount')
                    if review_count:
                        tour_info['num_reviews'] = int(review_count)
                        return
            except:
                continue
    
    def _extract_included_excluded(self, soup, tour_info):
        """Extract included/excluded items"""
        tick_list = soup.find('ul', class_='list-icon--tick')
        if tick_list:
            items = tick_list.find_all('li')
            for item in items:
                text = item.get_text().strip()
                if text:
                    tour_info['included_items'].append(text)
        
        cross_list = soup.find('ul', class_='list-icon--cross')
        if cross_list:
            items = cross_list.find_all('li')
            for item in items:
                text = item.get_text().strip()
                if text:
                    tour_info['excluded_items'].append(text)
    
    def _extract_activities_included(self, soup, tour_info):
        """Extract the complete activities included list"""

        print("  Extracting activities included list...")

        # Look for the specific ul class pattern mentioned by user
        activities_list = soup.find('ul', class_=re.compile(r'list-icon\s+list-icon--tick\s+list-3-cols\s+list-mobile-limit.*js-limit-list'))

        if not activities_list:
            # Fallback: Look for list with the specific classes
            activities_list = soup.find('ul', class_='list-icon list-icon--tick list-3-cols list-mobile-limit')

        if not activities_list:
            # Another fallback: look for list-3-cols with tick icons
            activities_list = soup.find('ul', class_='list-3-cols')
            if activities_list and not activities_list.find(class_='list-icon--tick'):
                activities_list = None

        if not activities_list:
            # Final fallback: look for any tick list that might contain activities
            all_tick_lists = soup.find_all('ul', class_='list-icon--tick')
            for tick_list in all_tick_lists:
                # Check if this list has 3-column styling or contains typical activities
                if ('list-3-cols' in tick_list.get('class', []) or
                    'js-limit-list' in ' '.join(tick_list.get('class', []))):
                    activities_list = tick_list
                    break

        if activities_list:
            items = activities_list.find_all('li')
            activities = []

            for item in items:
                text = item.get_text().strip()
                if text and text not in activities:  # Avoid duplicates
                    activities.append(text)

            if activities:
                tour_info['activities_incl'] = activities
                print(f"    Found {len(activities)} activities: {activities[0] if activities else 'None'}")
            else:
                print("    Activities list found but no valid items extracted")
        else:
            print("    No activities list found with the specified class pattern")
    
    def _extract_tour_name(self, soup, tour_data):
        """Extract tour name with improved validation - no URL fallback"""

        print("  Extracting tour name...")

        # Method 1: Try specific h1 selectors for Backpacking Tours site
        h1_selectors = [
            '.hero__content h1',  # Main hero section
            '.tour-header h1',
            'h1.tour-title',
            '.page-header h1',
            'h1[class*="title"]',
            'h1[class*="heading"]',
            'h1'
        ]

        for selector in h1_selectors:
            try:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title_text = title_elem.get_text().strip()
                    # Strict validation to prevent generic names
                    if (title_text and
                        len(title_text) > 3 and
                        title_text.lower() not in ['tours', 'tour', 'backpacking tours', 'group tours', 'backpacking', 'adventure'] and
                        not title_text.lower().startswith('book') and
                        not title_text.lower().endswith('tours')):
                        tour_data['tour_name'] = title_text
                        print(f"    Found tour name from {selector}: {title_text}")
                        return
            except Exception as e:
                continue

        # Method 2: Try title tag with better cleaning
        try:
            title_elem = soup.find('title')
            if title_elem:
                title_text = title_elem.get_text().strip()
                # Clean up title (remove site suffix)
                title_text = re.sub(r'\s*[-|]\s*Backpacking Tours.*$', '', title_text, flags=re.IGNORECASE)
                title_text = re.sub(r'\s*[-|]\s*BT.*$', '', title_text, flags=re.IGNORECASE)

                # Strict validation
                if (title_text and
                    len(title_text) > 3 and
                    title_text.lower() not in ['tours', 'tour', 'backpacking tours', 'group tours', 'backpacking', 'adventure', 'home', 'book'] and
                    not title_text.lower().startswith('book') and
                    'cookie' not in title_text.lower()):
                    tour_data['tour_name'] = title_text
                    print(f"    Found tour name from title tag: {title_text}")
                    return
        except Exception as e:
            pass

        # No fallback - leave empty if no valid name found
        print("    No valid tour name found - leaving empty")
        tour_data['tour_name'] = ''
    
    
    def _extract_country_from_articles(self, soup, tour_data):
        """Extract country from articles section 'See All Articles' link or URL"""

        print("  Extracting country from articles section...")

        try:
            # Method 1: Extract country from tour URL by matching against known countries
            url = tour_data.get('url', '')

            # Define known countries (sorted by length descending to match longer names first)
            known_countries = [
                'new-zealand', 'south-korea', 'costa-rica', 'south-africa', 'sri-lanka',  # Multi-word countries first
                'thailand', 'philippines', 'vietnam', 'cambodia', 'indonesia',
                'malaysia', 'singapore', 'australia', 'colombia', 'morocco',
                'india', 'japan', 'bali', 'laos', 'myanmar', 'brunei',
                'croatia', 'mexico', 'peru', 'nepal'
            ]

            # Extract the URL slug (last part of URL)
            url_slug = url.rstrip('/').split('/')[-1].lower()

            # Try to find a known country in the URL slug
            for country in known_countries:
                if country in url_slug:
                    tour_data['country'] = country
                    print(f"    Found country from URL: {country}")
                    return
            
            # Method 2: Look for country-specific blog links
            print("    No country found in URL patterns, trying blog links...")
            
            # Define known countries to look for specifically
            known_countries = [
                'thailand', 'bali', 'vietnam', 'cambodia', 'philippines',
                'sri-lanka', 'india', 'laos', 'myanmar', 'indonesia',
                'malaysia', 'singapore', 'brunei', 'south-korea',
                'new-zealand', 'costa-rica', 'south-africa'
            ]
            
            # Look for blog links containing known countries
            for country in known_countries:
                # Look for direct country blog link
                country_blog_link = soup.find('a', href=re.compile(f'/blog/{country}', re.IGNORECASE))
                if country_blog_link:
                    tour_data['country'] = country
                    print(f"    Found country from specific blog link: {country}")
                    return
            
            # Method 3: Look for any blog links and filter out non-countries
            blog_links = soup.find_all('a', href=re.compile(r'/blog/\w+', re.IGNORECASE))
            
            # Terms that are NOT countries (to skip)
            non_countries = {
                'recognised', 'top', 'gap', 'year', 'provider', 'overseas', 'hotel',
                'hostel', 'weather', 'best', 'time', 'visit', 'national', 'park',
                'floating', 'bungalows', 'train', 'night', 'home', 'index', 'main',
                'blog', 'about', 'contact', 'terms', 'privacy', 'booking'
            }
            
            for link in blog_links:
                href = link.get('href', '')
                if '/blog/' in href.lower():
                    country_match = re.search(r'/blog/([^-/]+)', href, re.IGNORECASE)
                    if country_match:
                        potential_country = country_match.group(1).lower()
                        
                        # Skip if it's a known non-country term
                        if potential_country not in non_countries and len(potential_country) > 2:
                            # Additional check: if it's a city name, try to map to country
                            city_to_country = {
                                'bangkok': 'thailand',
                                'hanoi': 'vietnam',
                                'saigon': 'vietnam',
                                'ho': 'vietnam',  # ho-chi-minh
                                'siem': 'cambodia',  # siem-reap
                                'phnom': 'cambodia',  # phnom-penh
                                'manila': 'philippines',
                                'jakarta': 'indonesia',
                                'kuala': 'malaysia',  # kuala-lumpur
                                'colombo': 'sri-lanka',
                                'kanchanaburi': 'thailand',
                                'krabi': 'thailand',
                                'phuket': 'thailand',
                                'erawan': 'thailand',
                                'khao': 'thailand',  # khao-sok
                                'koh': 'thailand',   # koh-phi-phi etc
                                'amaphawa': 'thailand'
                            }
                            
                            country = city_to_country.get(potential_country, potential_country)
                            tour_data['country'] = country
                            print(f"    Found country from blog link: {country} (from {potential_country})")
                            return
            
            print("    No valid country found in blog links either")
            tour_data['country'] = ''
            
        except Exception as e:
            print(f"    Error extracting country: {e}")
            tour_data['country'] = ''

    def _extract_seo_data(self, soup, tour_data):
        """Extract SEO metadata (title, description, keywords, Open Graph)"""

        print("  Extracting SEO data...")
        seo_data = tour_data['seo_data']

        try:
            # Extract meta title
            title_tag = soup.find('title')
            if title_tag:
                seo_data['meta_title'] = title_tag.get_text().strip()
                print(f"    Meta title: {seo_data['meta_title'][:50]}...")

            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                seo_data['meta_description'] = meta_desc.get('content', '').strip()
                print(f"    Meta description: {seo_data['meta_description'][:50]}...")

            # Extract meta keywords
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords:
                seo_data['meta_keywords'] = meta_keywords.get('content', '').strip()
                print(f"    Meta keywords: {seo_data['meta_keywords'][:50]}...")

            # Extract Open Graph tags
            og_tags = soup.find_all('meta', attrs={'property': lambda x: x and x.startswith('og:')})
            for tag in og_tags:
                property_name = tag.get('property', '').replace('og:', '')
                content = tag.get('content', '').strip()
                if property_name and content:
                    seo_data['open_graph'][property_name] = content

            if seo_data['open_graph']:
                print(f"    Open Graph tags: {len(seo_data['open_graph'])} found")

        except Exception as e:
            print(f"    Error extracting SEO data: {e}")

    def _extract_tour_colour(self, soup, tour_data):
        """Extract single tour colour from page styling by finding CSS color classes"""

        print("  Extracting tour colour...")

        try:
            # CSS color mappings from the main stylesheet
            css_color_mappings = {
                'magenta': 'a03a68',
                'lightpink': 'f978d5',
                'burgundy': 'ae2e69',
                'purple': '6c49ff',
                'orange': 'ffc132',
                'blue': '36e0dc',
                'blue2': '3d90f4',
                'green': '0fba68',
                'green2': '269d73',
                'green3': '36e0a4',
                'red': 'f50000',
                'red2': 'ea1f3d',
                'yellow': 'ffaf3b',
                'navyblue': '402df7',
                'orangeblood': 'ff603b',
                'blurple': 'f94171'
            }

            # Look for structural elements with specific color class patterns
            priority_selectors = [
                'circle-fb-rate--',  # Rating circles
                'l-submenu--',       # Submenu elements
                'bg-',               # Background colors
                'color-'             # Text colors
            ]

            for selector_prefix in priority_selectors:
                for color_name, hex_color in css_color_mappings.items():
                    class_pattern = f'{selector_prefix}{color_name}'
                    elements = soup.find_all(attrs={'class': lambda x: x and any(class_pattern in cls.lower() for cls in x)})
                    if elements:
                        tour_data['tour_colour'] = f"#{hex_color}"
                        print(f"    Found tour colour from priority class '{class_pattern}': {tour_data['tour_colour']}")
                        return

            # Count occurrences of each color theme to find the dominant one
            # Prioritize longer/more specific color names (e.g., "orangeblood" over "orange")
            sorted_colors = sorted(css_color_mappings.keys(), key=len, reverse=True)
            color_counts = {}
            all_elements = soup.find_all(attrs={'class': True})

            for element in all_elements:
                classes = element.get('class', [])
                for class_name in classes:
                    class_lower = class_name.lower()
                    # Check colors in order of specificity (longest first)
                    for color_name in sorted_colors:
                        # Look for color name in class (with common separators)
                        if (f'-{color_name}' in class_lower or
                            f'--{color_name}' in class_lower or
                            class_lower.endswith(color_name)):
                            color_counts[color_name] = color_counts.get(color_name, 0) + 1
                            break  # Stop at first match to prioritize longer names

            if color_counts:
                # Find the most frequently used color theme
                dominant_color = max(color_counts, key=color_counts.get)
                hex_color = css_color_mappings[dominant_color]
                tour_data['tour_colour'] = f"#{hex_color}"
                print(f"    Found dominant tour colour '{dominant_color}' (appears {color_counts[dominant_color]} times): {tour_data['tour_colour']}")
                return

            # No color found - set to N/A
            tour_data['tour_colour'] = 'N/A'
            print("    No tour colour found - setting to N/A")

        except Exception as e:
            print(f"    Error extracting tour colour: {e}")
            tour_data['tour_colour'] = 'N/A'

    def _extract_tour_id_from_page(self, url):
        """Extract the numeric tour ID from the tour page HTML"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            html = response.text

            # Look for /tour/{id}/ pattern in the HTML
            tour_id_match = re.search(r'/tour/(\d+)/', html)
            if tour_id_match:
                tour_id = tour_id_match.group(1)
                print(f"    Extracted tour ID: {tour_id}")
                return tour_id

            return None
        except Exception as e:
            print(f"    Error extracting tour ID: {e}")
            return None

    def _extract_detailed_itinerary(self, soup, tour_data):
        """Extract detailed day-by-day itinerary"""

        print("  Extracting detailed itinerary...")

        # Find all itinerary day cards
        day_cards = soup.find_all('article', class_='card')
        
        for card in day_cards:
            # Look for day number
            day_span = card.find('span', class_='card__content-day')
            if not day_span:
                continue
                
            day_text = day_span.get_text().strip()
            day_match = re.search(r'Day (\d+)', day_text, re.IGNORECASE)
            if not day_match:
                continue
                
            day_num = day_match.group(1)
            
            # Extract title
            title_elem = card.find('h3', class_='headline-3')
            day_title = title_elem.get_text().strip() if title_elem else ''
            
            # Extract description
            desc_paragraph = card.find('div', class_='content').find('p') if card.find('div', class_='content') else None
            day_desc = desc_paragraph.get_text().strip() if desc_paragraph else ''
            
            # Extract meals, activities, room type from the tour info items
            day_meals = []
            day_activities = []
            day_roomtype = ''
            
            tour_info_items = card.find_all('div', class_='list-tour-info__item-desc')
            for item in tour_info_items:
                bold = item.find('b')
                span = item.find('span')
                
                if bold and span:
                    key = bold.get_text().strip()
                    value = span.get_text().strip()
                    
                    if 'meals included' in key.lower():
                        # Split meals by comma and clean
                        meals = [meal.strip() for meal in value.split(',')]
                        day_meals.extend(meals)
                    elif 'activities included' in key.lower():
                        # Split activities by comma and clean
                        activities = [activity.strip() for activity in value.split(',')]
                        day_activities.extend(activities)
                    elif 'room type' in key.lower():
                        day_roomtype = value
            
            # Add to itinerary in the requested order: title, description, meals, room type, activities
            tour_data['itinerary'][f'day{day_num}'] = {
                'title': day_title,
                'desc': day_desc,
                'meals_incl': day_meals,
                'roomtype': day_roomtype,
                'activities_incl': day_activities
            }
        
        print(f"    Processed {len(tour_data['itinerary'])} days")
    
    def _extract_tour_dates(self, base_url, tour_data):
        """Extract tour dates with availability"""

        print("  Extracting tour dates...")

        try:
            # Extract tour ID from the page HTML
            tour_id = self._extract_tour_id_from_page(base_url)
            if not tour_id:
                print("    Error: Could not extract tour ID from page")
                tour_data['starting_dates'] = []
                return

            # Build the API URL dynamically using the extracted tour ID
            api_url = f"https://www.backpackingtours.com/tour/{tour_id}/tour-dates"
            print(f"    Using API URL: {api_url}")
            
            # Add proper headers for the API request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/html, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': base_url,
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            response = self.session.get(api_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse JSON response
            json_data = response.json()
            if 'html' in json_data:
                html_content = json_data['html']
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Method 1: Extract from table rows (most reliable)
                date_entries = []
                table_rows = soup.find_all('tr')
                
                for row in table_rows:
                    # Get the first cell which usually contains the date range
                    first_cell = row.find('td')
                    if first_cell:
                        date_text = first_cell.get_text().strip()
                        # Look for date pattern
                        if re.match(r'\d+ \w+ - \d+ \w+ \d+', date_text):
                            # Check for availability indicators in the row
                            row_text = row.get_text().lower()
                            
                            if 'book now' in row_text or 'available' in row_text:
                                availability = 'Book Now'
                            elif 'no availability' in row_text or 'full' in row_text or 'sold out' in row_text:
                                availability = 'No Availability'
                            elif 'limited' in row_text:
                                availability = 'Limited'
                            else:
                                availability = 'Available'  # Default
                            
                            date_entries.append(f"{date_text} - {availability}")
                
                # Method 2: Fallback - extract all date patterns from text
                if not date_entries:
                    page_text = soup.get_text()
                    date_patterns = re.findall(r'\d+ \w+ - \d+ \w+ \d+', page_text)
                    
                    # For each date, try to determine availability
                    for date_pattern in date_patterns:
                        # This is a simplified approach - in reality you'd need to parse the table structure
                        date_entries.append(f"{date_pattern} - Available")
                
                if date_entries:
                    # Remove duplicates while preserving order
                    unique_dates = []
                    seen = set()
                    for date in date_entries:
                        if date not in seen:
                            unique_dates.append(date)
                            seen.add(date)
                    
                    tour_data['starting_dates'] = unique_dates
                    print(f"    Found {len(unique_dates)} tour dates")
                else:
                    print("    No tour dates found in structured format")
                    tour_data['starting_dates'] = []
            else:
                print("    No HTML content in JSON response")
                tour_data['starting_dates'] = []
                    
        except Exception as e:
            print(f"    Error extracting tour dates: {e}")
            tour_data['starting_dates'] = []
    
    def _extract_all_currency_prices(self, url, tour_data):
        """Extract prices in all currencies"""
        
        currency_mapping = {
            'USD': '1', 'NZD': '2', 'GBP': '3', 
            'EUR': '4', 'CAD': '5', 'AUD': '6'
        }
        
        print("  Extracting currency prices...")
        
        for currency, form_value in currency_mapping.items():
            try:
                form_data = {'currency': form_value}
                change_response = self.session.post(
                    "https://www.backpackingtours.com/change-currency", 
                    data=form_data, 
                    allow_redirects=True
                )
                
                tour_response = self.session.get(url, timeout=8)
                tour_soup = BeautifulSoup(tour_response.content, 'html.parser')
                
                price = self._extract_price_for_currency(tour_soup, currency)
                if price:
                    tour_data['price'][f'price_{currency}'] = price
                
                time.sleep(0.3)
                
            except Exception as e:
                print(f"    Error getting {currency} price: {e}")
        
        prices_found = sum(1 for p in tour_data['price'].values() if p)
        print(f"    Found prices in {prices_found} currencies")
    
    def _extract_price_for_currency(self, soup, currency):
        """Extract price for specific currency"""
        
        price_elements = soup.find_all(['div', 'span'], class_=re.compile(r'price'))
        candidates = []
        
        for elem in price_elements:
            text = elem.get_text().strip()
            
            if currency in ['USD', 'CAD', 'AUD', 'NZD']:
                price_matches = re.findall(r'\$(\d+[,\d]*)', text)
                for price in price_matches:
                    price_num = int(price.replace(',', ''))
                    if price_num > 300:
                        candidates.append(price_num)
            elif currency == 'EUR':
                price_matches = re.findall(r'€(\d+[,\d]*)', text)
                for price in price_matches:
                    price_num = int(price.replace(',', ''))
                    if price_num > 300:
                        candidates.append(price_num)
            elif currency == 'GBP':
                price_matches = re.findall(r'£(\d+[,\d]*)', text)
                for price in price_matches:
                    price_num = int(price.replace(',', ''))
                    if price_num > 300:
                        candidates.append(price_num)
        
        return max(candidates) if candidates else 0
    
    def _generate_tour_id(self, url):
        """Generate a unique tour ID from URL"""
        # Extract the tour name part from URL
        tour_slug = url.split('/')[-1]
        # Create a short hash for uniqueness
        hash_obj = hashlib.md5(url.encode())
        short_hash = hash_obj.hexdigest()[:8]
        return f"{tour_slug}_{short_hash}"
    
    def _extract_number(self, text):
        """Extract numeric value from text and return as integer"""
        if isinstance(text, (int, float)):
            return int(text)
        
        # Find all numbers in the text
        numbers = re.findall(r'\d+', str(text))
        if numbers:
            return int(numbers[0])
        return 0
    
    def _parse_duration(self, duration_text, tour_info):
        """Parse duration text and populate both raw and display values"""
        tour_info['duration']['display'] = duration_text
        
        # Extract number of days
        days_match = re.search(r'(\d+)\s*days?', duration_text.lower())
        if days_match:
            tour_info['duration']['days'] = int(days_match.group(1))
        else:
            tour_info['duration']['days'] = 0
    
    def _parse_age_range(self, age_text, tour_info):
        """Parse age range text and populate both raw and display values"""
        tour_info['age_range']['display'] = age_text
        
        # Extract min and max ages
        age_matches = re.findall(r'(\d+)', age_text)
        if len(age_matches) >= 2:
            tour_info['age_range']['min'] = int(age_matches[0])
            tour_info['age_range']['max'] = int(age_matches[1])
        elif len(age_matches) == 1:
            # If only one age, assume it's the starting age
            tour_info['age_range']['min'] = int(age_matches[0])
            tour_info['age_range']['max'] = 0
        else:
            tour_info['age_range']['min'] = 0
            tour_info['age_range']['max'] = 0
    
    def _validate_and_clean_data(self, tour_data):
        """Validate and clean the extracted data"""
        # Fix common typos in meals
        if 'itinerary' in tour_data:
            for day_key, day_data in tour_data['itinerary'].items():
                if 'meals_incl' in day_data and isinstance(day_data['meals_incl'], list):
                    # Fix breakfast typo
                    day_data['meals_incl'] = [
                        'Breakfast' if meal == 'Brekfast' else meal 
                        for meal in day_data['meals_incl']
                    ]
        
        # Ensure tour_name is not empty
        if not tour_data.get('tour_name'):
            # Try to extract from URL
            url_parts = tour_data['url'].split('/')
            if url_parts:
                tour_data['tour_name'] = url_parts[-1].replace('-', ' ').title()
        
        # Validate starting dates format
        if not tour_data.get('starting_dates'):
            tour_data['starting_dates'] = []
        
        # Ensure all price fields are integers
        for currency in ['GBP', 'USD', 'EUR', 'CAD', 'AUD', 'NZD']:
            price_key = f'price_{currency}'
            if price_key in tour_data['price']:
                if tour_data['price'][price_key] is None:
                    tour_data['price'][price_key] = 0

def test_categorized_extraction():
    """Test categorized extraction"""
    extractor = CategorizedTourExtractor()
    test_url = "https://www.backpackingtours.com/book-a-backpacking-tour/backpacking-india"
    
    print(f"Testing categorized extraction for: {test_url}")
    print("="*70)
    
    tour_data = extractor.extract_tour_data(test_url)
    
    print("\\n" + "="*70)
    print("EXTRACTED DATA BY CATEGORY")
    print("="*70)
    
    # Show tour name at the top
    tour_name = tour_data.get('tour_name', '[NOT FOUND]')
    print(f"\\n🏷️  TOUR NAME: {tour_name}")
    
    # Tour Information
    print("\\n📋 TOUR INFORMATION:")
    print("-" * 30)
    tour_info = tour_data.get('tour_information', {})
    key_fields = ['description', 'length', 'avg_age', 'num_activities', 
                  'num_meals', 'avg_group_size', 'operator', 'starting_point', 
                  'ending_point', 'num_reviews']
    
    for field in key_fields:
        value = tour_info.get(field, '[NOT FOUND]')
        if field == 'description' and len(str(value)) > 100:
            value = str(value)[:100] + "..."
        print(f"  {field}: {value}")
    
    # Show activities and lists
    activities = tour_info.get('activities_incl', [])
    print(f"  activities_incl: {len(activities)} items - {activities[0] if activities else 'None'}")
    
    included = tour_info.get('included_items', [])
    excluded = tour_info.get('excluded_items', [])
    print(f"  included_items: {len(included)} items")
    print(f"  excluded_items: {len(excluded)} items")
    
    # Itinerary
    print("\\n📅 ITINERARY:")
    print("-" * 30)
    itinerary = tour_data.get('itinerary', {})
    print(f"  Total days: {len(itinerary)}")
    
    if 'day1' in itinerary:
        day1 = itinerary['day1']
        print(f"  Day 1 sample:")
        print(f"    title: {day1.get('title', 'N/A')}")
        print(f"    meals_incl: {', '.join(day1.get('meals_incl', []))}")
        print(f"    roomtype: {day1.get('roomtype', 'N/A')}")
        print(f"    activities_incl: {', '.join(day1.get('activities_incl', []))}")
    
    # Starting Dates
    print("\\n📆 STARTING DATES:")
    print("-" * 30)
    dates = tour_data.get('starting_dates', [])
    print(f"  Total dates: {len(dates)}")
    for i, date in enumerate(dates[:3], 1):
        print(f"  {i}. {date}")
    if len(dates) > 3:
        print(f"  ... and {len(dates)-3} more")
    
    # Price
    print("\\n💰 PRICE:")
    print("-" * 30)
    price_info = tour_data.get('price', {})
    for currency in ['GBP', 'USD', 'EUR', 'CAD', 'AUD', 'NZD']:
        price = price_info.get(f'price_{currency}', '[NOT FOUND]')
        print(f"  {currency}: {price}")
    
    # Save results
    with open('group_tours_frontend.json', 'w') as f:
        json.dump(tour_data, f, indent=2)
    
    print(f"\\nResults saved to group_tours_frontend.json")
    
    return tour_data

if __name__ == "__main__":
    test_categorized_extraction()