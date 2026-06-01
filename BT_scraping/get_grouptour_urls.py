#!/usr/bin/env python3
"""
Discover all group tour URLs from Backpacking Tours website
Searches for URLs containing:
- https://www.backpackingtours.com/group
- https://www.backpackingtours.com/book-a-backpacking-tour  
- https://www.backpackingtours.com/film-photography-thailand

Saves results to group_tour_urls.json with structure:
[
    {
        "bt_url": "https://www.backpackingtours.com/group-tour-bali",
        "alfred_url": null
    }
]
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin, urlparse
import time

class GroupTourURLDiscovery:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.base_url = 'https://www.backpackingtours.com'
        self.discovered_urls = set()
        
        # URL patterns we're looking for
        self.target_patterns = [
            'https://www.backpackingtours.com/group',
            'https://www.backpackingtours.com/book-a-backpacking-tour',
            'https://www.backpackingtours.com/film-photography-thailand'
        ]
    
    def discover_urls(self):
        """Main method to discover all group tour URLs"""
        print("🔍 Discovering group tour URLs from Backpacking Tours website...")
        print("=" * 70)
        
        # Try multiple discovery methods
        self._discover_from_sitemap()
        self._discover_from_main_pages()
        self._discover_from_tours_page()
        
        # Convert to JSON format
        url_list = self._format_urls_for_json()
        
        # Save to file
        self._save_to_json(url_list)
        
        return url_list
    
    def _discover_from_sitemap(self):
        """Try to discover URLs from sitemap"""
        print("\n📋 Checking sitemap...")
        
        sitemap_urls = [
            f'{self.base_url}/sitemap.xml',
            f'{self.base_url}/sitemap_index.xml',
            f'{self.base_url}/sitemap-tours.xml'
        ]
        
        for sitemap_url in sitemap_urls:
            try:
                print(f"  Checking: {sitemap_url}")
                response = self.session.get(sitemap_url, timeout=10)
                
                if response.status_code == 200:
                    # Parse XML sitemap
                    soup = BeautifulSoup(response.content, 'xml')
                    
                    # Look for <loc> tags containing our target patterns
                    for loc in soup.find_all('loc'):
                        url = loc.get_text().strip()
                        if self._is_target_url(url):
                            self.discovered_urls.add(url)
                            print(f"    ✅ Found: {url.split('/')[-1]}")
                    
                    time.sleep(1)  # Be respectful
                    
            except Exception as e:
                print(f"    ❌ Error accessing {sitemap_url}: {e}")
    
    def _discover_from_main_pages(self):
        """Discover URLs from main navigation and tour listing pages"""
        print("\n🏠 Checking main website pages...")
        
        pages_to_check = [
            f'{self.base_url}/',
            f'{self.base_url}/tours',
            f'{self.base_url}/group-tours',
            f'{self.base_url}/backpacking-tours',
            f'{self.base_url}/destinations'
        ]
        
        for page_url in pages_to_check:
            try:
                print(f"  Scanning: {page_url}")
                response = self.session.get(page_url, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find all links on the page
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        full_url = urljoin(self.base_url, href)
                        
                        if self._is_target_url(full_url):
                            if full_url not in self.discovered_urls:
                                self.discovered_urls.add(full_url)
                                print(f"    ✅ Found: {full_url.split('/')[-1]}")
                
                time.sleep(2)  # Be respectful
                
            except Exception as e:
                print(f"    ❌ Error accessing {page_url}: {e}")
    
    def _discover_from_tours_page(self):
        """Specifically check tours listing pages"""
        print("\n🗂️ Checking tours listing pages...")
        
        # Try common tour listing patterns
        tour_pages = [
            f'{self.base_url}/group-tours',
            f'{self.base_url}/tours/group',
            f'{self.base_url}/destinations/group-tours'
        ]
        
        for page_url in tour_pages:
            try:
                print(f"  Scanning: {page_url}")
                response = self.session.get(page_url, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for tour cards, buttons, or links
                    selectors = [
                        'a[href*="group"]',
                        'a[href*="book-a-backpacking-tour"]',
                        'a[href*="film-photography"]',
                        '.tour-card a',
                        '.tour-link',
                        '[data-tour-url]'
                    ]
                    
                    for selector in selectors:
                        for element in soup.select(selector):
                            href = element.get('href') or element.get('data-tour-url')
                            if href:
                                full_url = urljoin(self.base_url, href)
                                if self._is_target_url(full_url):
                                    if full_url not in self.discovered_urls:
                                        self.discovered_urls.add(full_url)
                                        print(f"    ✅ Found: {full_url.split('/')[-1]}")
                
                time.sleep(2)  # Be respectful
                
            except Exception as e:
                print(f"    ❌ Could not access {page_url}: {e}")
    
    def _is_target_url(self, url):
        """Check if URL matches our target patterns"""
        if not url or not isinstance(url, str):
            return False

        # Clean up the URL
        url = url.strip()

        # Must be from backpackingtours.com domain
        if 'backpackingtours.com' not in url:
            return False

        # CRITICAL FIX: Exclude the generic booking page
        # This page has generic content like "Group Travel Tours Asia 2025/2026"
        # Instead of specific tour information
        if url.rstrip('/') == 'https://www.backpackingtours.com/book-a-backpacking-tour':
            print(f"    ❌ Excluding generic booking page: {url}")
            return False

        # Check against our target patterns
        for pattern in self.target_patterns:
            if pattern in url:
                # Additional filters to avoid non-tour pages
                exclude_patterns = [
                    '/blog', '/about', '/contact', '/faq', '/terms',
                    '/privacy', '/login', '/register', '.jpg', '.png',
                    '.pdf', '/admin', '/api', '#', '?'
                ]

                if not any(exclude in url.lower() for exclude in exclude_patterns):
                    return True

        return False
    
    def _format_urls_for_json(self):
        """Convert discovered URLs to JSON format"""
        print(f"\n📝 Formatting {len(self.discovered_urls)} URLs for JSON...")
        
        url_list = []
        for url in sorted(self.discovered_urls):
            url_list.append({
                "bt_url": url,
                "alfred_url": None  # Will be populated later
            })
        
        return url_list
    
    def _save_to_json(self, url_list):
        """Save URLs to JSON file"""
        filename = 'group_tour_urls.json'
        
        try:
            with open(filename, 'w') as f:
                json.dump(url_list, f, indent=2)
            
            print(f"\n💾 Saved {len(url_list)} URLs to {filename}")
            
            # Show sample of discovered URLs
            if url_list:
                print(f"\n🏷️  Sample URLs discovered:")
                for i, item in enumerate(url_list[:5], 1):
                    url = item['bt_url']
                    print(f"   {i}. {url.split('/')[-1]}")
                
                if len(url_list) > 5:
                    print(f"   ... and {len(url_list) - 5} more")
        
        except Exception as e:
            print(f"❌ Error saving to JSON: {e}")
    
    def validate_discovery(self):
        """Validate that we found the expected number of tours"""
        print(f"\n✅ Discovery Summary:")
        print(f"   🎯 Total URLs found: {len(self.discovered_urls)}")
        
        # Categorize by pattern
        categories = {
            'group': 0,
            'book-a-backpacking-tour': 0,
            'film-photography': 0
        }
        
        for url in self.discovered_urls:
            if '/group' in url:
                categories['group'] += 1
            elif '/book-a-backpacking-tour' in url:
                categories['book-a-backpacking-tour'] += 1
            elif '/film-photography' in url:
                categories['film-photography'] += 1
        
        print(f"   📊 Breakdown:")
        print(f"      • Group tours: {categories['group']}")
        print(f"      • Backpacking tours: {categories['book-a-backpacking-tour']}")
        print(f"      • Photography tours: {categories['film-photography']}")
        
        if len(self.discovered_urls) >= 25:  # Expect around 30, allow some flexibility
            print(f"   ✅ Good! Found sufficient URLs (expected ~30)")
        else:
            print(f"   ⚠️  Found fewer URLs than expected. May need additional discovery methods.")

def main():
    """Main function to run URL discovery"""
    discoverer = GroupTourURLDiscovery()
    
    try:
        # Discover URLs
        url_list = discoverer.discover_urls()
        
        # Validate results
        discoverer.validate_discovery()
        
        print(f"\n🎉 URL DISCOVERY COMPLETE!")
        print(f"   📁 Results saved to: group_tour_urls.json")
        print(f"   🔗 Ready for scraping with scrape_grouptours.py")
        
        return url_list
        
    except Exception as e:
        print(f"❌ Discovery failed: {e}")
        return []

if __name__ == "__main__":
    main()