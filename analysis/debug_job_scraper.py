"""
Enhanced debug to see actual HTML structure
"""

import requests
from bs4 import BeautifulSoup
import re

def enhanced_debug(url):
    """Show actual HTML structure to understand job board layout"""
    print(f"\n🔍 ENHANCED DEBUG: {url}")
    print("=" * 80)
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; JobTracker/1.0)'}
        response = requests.get(url, headers=headers, timeout=15)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Method 1: Look for any elements with "job" in class name
            print("\n📋 METHOD 1: Elements with 'job' in class name")
            job_classes = soup.find_all(class_=re.compile(r'job', re.I))
            print(f"Found {len(job_classes)} elements with 'job' in class")
            for i, elem in enumerate(job_classes[:3]):
                print(f"  {i+1}. Tag: {elem.name}, Class: {elem.get('class')}")
                print(f"     Text: {elem.get_text(strip=True)[:100]}...")
            
            # Method 2: Look for any elements with "opening" in class name
            print("\n📋 METHOD 2: Elements with 'opening' in class name")
            opening_classes = soup.find_all(class_=re.compile(r'opening', re.I))
            print(f"Found {len(opening_classes)} elements with 'opening' in class")
            for i, elem in enumerate(opening_classes[:3]):
                print(f"  {i+1}. Tag: {elem.name}, Class: {elem.get('class')}")
                print(f"     Text: {elem.get_text(strip=True)[:100]}...")
            
            # Method 3: Look for any elements with "position" in class name
            print("\n📋 METHOD 3: Elements with 'position' in class name")
            position_classes = soup.find_all(class_=re.compile(r'position', re.I))
            print(f"Found {len(position_classes)} elements with 'position' in class")
            for i, elem in enumerate(position_classes[:3]):
                print(f"  {i+1}. Tag: {elem.name}, Class: {elem.get('class')}")
                print(f"     Text: {elem.get_text(strip=True)[:100]}...")
            
            # Method 4: Look for links that might be job postings
            print("\n📋 METHOD 4: Links with job-like text")
            all_links = soup.find_all('a', href=True)
            job_like_links = []
            
            for link in all_links:
                text = link.get_text(strip=True)
                href = link.get('href', '')
                
                # Look for job-like keywords in link text
                if any(keyword in text.lower() for keyword in [
                    'engineer', 'developer', 'manager', 'director', 'analyst',
                    'specialist', 'coordinator', 'lead', 'senior', 'junior'
                ]):
                    job_like_links.append((text, href))
            
            print(f"Found {len(job_like_links)} job-like links")
            for i, (text, href) in enumerate(job_like_links[:5]):
                print(f"  {i+1}. Text: {text}")
                print(f"     URL: {href}")
            
            # Method 5: Show page title and key structure
            print("\n📋 METHOD 5: Page structure")
            title = soup.find('title')
            if title:
                print(f"Page title: {title.get_text(strip=True)}")
            
            # Look for common container elements
            containers = soup.find_all(['div', 'section', 'ul'], limit=10)
            print(f"Found {len(containers)} potential container elements")
            
            # Method 6: Raw text search for job-related content
            print("\n📋 METHOD 6: Raw text search")
            page_text = response.text.lower()
            job_keywords = ['software engineer', 'product manager', 'data analyst', 
                          'senior', 'junior', 'full-time', 'remote']
            
            found_keywords = []
            for keyword in job_keywords:
                if keyword in page_text:
                    found_keywords.append(keyword)
            
            print(f"Job keywords found in page text: {found_keywords}")
            
            # Method 7: Check if page is JavaScript-heavy
            print("\n📋 METHOD 7: JavaScript detection")
            scripts = soup.find_all('script')
            print(f"Found {len(scripts)} script tags")
            
            js_frameworks = ['react', 'vue', 'angular', 'ember']
            js_detected = []
            for script in scripts:
                script_text = script.get_text().lower()
                for framework in js_frameworks:
                    if framework in script_text:
                        js_detected.append(framework)
            
            if js_detected:
                print(f"JavaScript frameworks detected: {js_detected}")
                print("⚠️  Page might be dynamically loaded (need browser automation)")
            else:
                print("No major JS frameworks detected - static HTML")
        
        else:
            print(f"❌ Failed to access URL: HTTP {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Test the Greenhouse URL with enhanced debugging
    enhanced_debug("https://job-boards.greenhouse.io/techstars57")