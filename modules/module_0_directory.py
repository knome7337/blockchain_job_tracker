"""
Climate + AI + Blockchain Accelerator Job Tracker
Module 0: Accelerator Directory Builder
Python 3.10+ Compatible

Focus: Europe and India blockchain accelerators
"""

import os
import csv
import json
import time
import logging
import requests
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import re
from dotenv import load_dotenv

# Load environment variables from .env file
# Make path to .env file explicit to avoid issues with -m flag
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(project_dir, '.env')
load_dotenv(dotenv_path=dotenv_path)

# Setup logging
os.makedirs("data", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(module)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/system_logs.csv'),
        logging.StreamHandler()
    ]
)

class AcceleratorDirectoryBuilder:
    """Module 0: Discover and maintain global accelerators working in blockchain/climate/AI"""
    
    def __init__(self):
        # Load environment variables
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.google_cse_id = os.getenv('GOOGLE_CSE_ID')
        
        if not self.google_api_key or not self.google_cse_id:
            raise ValueError("Missing Google API credentials. Please set GOOGLE_API_KEY and GOOGLE_CSE_ID in .env file")
        
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.accelerators_file = "data/accelerators_list.csv"
        self.ensure_data_directory()
        
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        os.makedirs("data", exist_ok=True)
        
    def safe_search(self, query: str, max_retries: int = 3) -> List[Dict]:
        """Safely execute Google Custom Search with retry logic"""
        for attempt in range(max_retries):
            try:
                return self._execute_search(query)
            except Exception as e:
                logging.error(f"Search attempt {attempt + 1} failed for query '{query}': {e}")
                if attempt == max_retries - 1:
                    return []
                time.sleep(2 ** attempt)  # Exponential backoff
                
    def _execute_search(self, query: str) -> List[Dict]:
        """Execute single Google Custom Search"""
        params = {
            'key': self.google_api_key,
            'cx': self.google_cse_id,
            'q': query,
            'num': 10  # Get 10 results per query
        }
        
        response = requests.get(self.base_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        if 'items' in data:
            for item in data['items']:
                result = {
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'query_used': query
                }
                results.append(result)
                
        return results
    
    def extract_accelerator_info(self, search_result: Dict) -> Dict:
        """Extract and normalize accelerator information from search result"""
        try:
            # Extract domain for organization name fallback
            domain = urlparse(search_result['link']).netloc
            org_name = search_result['title'].split(' - ')[0].strip()
            
            # Try to identify careers page
            careers_url = self._find_careers_url(search_result['link'])
            
            # Determine focus tags based on title and snippet
            focus_tags = self._determine_focus_tags(
                search_result['title'] + ' ' + search_result['snippet']
            )
            
            # Try to extract country (basic heuristic)
            country = self._extract_country(search_result['snippet'])
            
            accelerator_info = {
                'Name': org_name,
                'Website': search_result['link'],
                'Country': country,
                'Focus_Tags': ', '.join(focus_tags),
                'Careers_URL': careers_url,
                'Notes': search_result['snippet'][:200] + '...' if len(search_result['snippet']) > 200 else search_result['snippet'],
                'Discovery_Date': datetime.now().strftime('%Y-%m-%d'),
                'Status': 'discovered',
                'Query_Source': search_result['query_used']
            }
            
            return accelerator_info
            
        except Exception as e:
            logging.error(f"Failed to extract accelerator info: {e}")
            return {}
    
    def _find_careers_url(self, website_url: str) -> str:
        """Try to construct careers page URL"""
        try:
            # Common careers page patterns
            careers_paths = ['/careers', '/jobs', '/career', '/work-with-us', '/join-us']
            
            for path in careers_paths:
                careers_url = urljoin(website_url, path)
                # Quick check if URL is reachable (with short timeout)
                try:
                    response = requests.head(careers_url, timeout=5)
                    if response.status_code == 200:
                        return careers_url
                except:
                    continue
            
            # Fallback to base website
            return website_url
            
        except Exception:
            return website_url
    
    def _determine_focus_tags(self, text: str) -> List[str]:
        """Determine focus areas based on text content"""
        text_lower = text.lower()
        tags = []
        
        # Blockchain keywords
        blockchain_keywords = ['blockchain', 'crypto', 'web3', 'defi', 'nft', 'dao', 'bitcoin', 'ethereum']
        if any(keyword in text_lower for keyword in blockchain_keywords):
            tags.append('blockchain')
        
        # Climate keywords
        climate_keywords = ['climate', 'sustainability', 'green', 'carbon', 'renewable', 'clean energy', 'environment']
        if any(keyword in text_lower for keyword in climate_keywords):
            tags.append('climate')
        
        # AI keywords
        ai_keywords = ['artificial intelligence', 'machine learning', 'ai', 'ml', 'deep learning']
        if any(keyword in text_lower for keyword in ai_keywords):
            tags.append('ai')
        
        # Default to unknown if no clear focus
        if not tags:
            tags.append('unknown')
            
        return tags
    
    def _extract_country(self, text: str) -> str:
        """Extract country information from text (basic heuristics)"""
        text_lower = text.lower()
        
        # European countries
        european_countries = {
            'germany': 'Germany', 'berlin': 'Germany', 'munich': 'Germany',
            'france': 'France', 'paris': 'France',
            'uk': 'United Kingdom', 'london': 'United Kingdom', 'britain': 'United Kingdom',
            'netherlands': 'Netherlands', 'amsterdam': 'Netherlands',
            'switzerland': 'Switzerland', 'zurich': 'Switzerland',
            'sweden': 'Sweden', 'stockholm': 'Sweden',
            'estonia': 'Estonia', 'tallinn': 'Estonia',
            'finland': 'Finland', 'helsinki': 'Finland',
            'norway': 'Norway', 'oslo': 'Norway',
            'denmark': 'Denmark', 'copenhagen': 'Denmark',
            'spain': 'Spain', 'madrid': 'Spain', 'barcelona': 'Spain',
            'italy': 'Italy', 'milan': 'Italy', 'rome': 'Italy',
            'portugal': 'Portugal', 'lisbon': 'Portugal'
        }
        
        # Indian locations
        indian_locations = {
            'india': 'India', 'mumbai': 'India', 'bangalore': 'India', 
            'delhi': 'India', 'hyderabad': 'India', 'pune': 'India',
            'chennai': 'India', 'kolkata': 'India', 'gurgaon': 'India'
        }
        
        # Check for matches
        all_locations = {**european_countries, **indian_locations}
        
        for location, country in all_locations.items():
            if location in text_lower:
                return country
        
        return 'Unknown'
    
    def get_blockchain_search_queries(self) -> List[str]:
        """Generate targeted search queries for European and Indian blockchain accelerators"""
        
        # Base terms
        base_terms = [
            "blockchain accelerator",
            "crypto startup accelerator", 
            "web3 accelerator",
            "blockchain incubator",
            "defi accelerator"
        ]
        
        # European focus
        european_queries = []
        european_regions = ["Europe", "Berlin", "London", "Amsterdam", "Zurich", "Paris", "Stockholm"]
        
        for term in base_terms:
            for region in european_regions:
                european_queries.extend([
                    f"{term} {region}",
                    f"{term} site:.eu",
                    f"{region} {term}"
                ])
        
        # Indian focus  
        indian_queries = []
        indian_cities = ["India", "Mumbai", "Bangalore", "Delhi", "Hyderabad"]
        
        for term in base_terms:
            for city in indian_cities:
                indian_queries.extend([
                    f"{term} {city}",
                    f"{term} site:.in",
                    f"{city} {term}"
                ])
        
        # Combine and deduplicate
        all_queries = list(set(european_queries + indian_queries))
        
        # Add some general high-value queries
        all_queries.extend([
            "blockchain startup accelerator Europe",
            "crypto venture accelerator India", 
            "web3 incubator program 2024",
            "blockchain accelerator program application"
        ])
        
        return all_queries[:20]  # Limit to 20 queries for MVP
    
    def save_accelerators_to_csv(self, accelerators: List[Dict]):
        """Save discovered accelerators to CSV file"""
        try:
            # Check if file exists to determine if we need headers
            file_exists = os.path.exists(self.accelerators_file)
            
            with open(self.accelerators_file, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'Name', 'Website', 'Country', 'Focus_Tags', 'Careers_URL', 
                    'Notes', 'Discovery_Date', 'Status', 'Query_Source'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write headers if new file
                if not file_exists:
                    writer.writeheader()
                
                # Write accelerator data
                for accelerator in accelerators:
                    if accelerator:  # Skip empty results
                        writer.writerow(accelerator)
                        
            logging.info(f"Saved {len(accelerators)} accelerators to {self.accelerators_file}")
            
        except Exception as e:
            logging.error(f"Failed to save accelerators to CSV: {e}")
    
    def deduplicate_accelerators(self):
        """Remove duplicate accelerators based on website URL"""
        try:
            if not os.path.exists(self.accelerators_file):
                return
            
            # Read existing data
            seen_websites = set()
            unique_accelerators = []
            
            with open(self.accelerators_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    website = row.get('Website', '').strip().lower()
                    if website and website not in seen_websites:
                        seen_websites.add(website)
                        unique_accelerators.append(row)
            
            # Rewrite file with unique entries
            with open(self.accelerators_file, 'w', newline='', encoding='utf-8') as csvfile:
                if unique_accelerators:
                    fieldnames = unique_accelerators[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(unique_accelerators)
            
            logging.info(f"Deduplicated accelerators. Kept {len(unique_accelerators)} unique entries")
            
        except Exception as e:
            logging.error(f"Failed to deduplicate accelerators: {e}")
    
    def discover_accelerators(self) -> int:
        """Main method to discover blockchain accelerators in Europe and India"""
        logging.info("Starting accelerator discovery for Europe and India...")
        
        queries = self.get_blockchain_search_queries()
        total_found = 0
        
        for i, query in enumerate(queries, 1):
            logging.info(f"Processing query {i}/{len(queries)}: {query}")
            
            # Execute search with safety wrapper
            search_results = self.safe_search(query)
            
            if not search_results:
                logging.warning(f"No results for query: {query}")
                continue
            
            # Extract accelerator info from results
            accelerators = []
            for result in search_results:
                accelerator_info = self.extract_accelerator_info(result)
                if accelerator_info:
                    accelerators.append(accelerator_info)
            
            # Save to CSV
            if accelerators:
                self.save_accelerators_to_csv(accelerators)
                total_found += len(accelerators)
                logging.info(f"Found {len(accelerators)} accelerators from query: {query}")
            
            # Rate limiting - be respectful to Google API
            time.sleep(1)
        
        # Clean up duplicates
        self.deduplicate_accelerators()
        
        logging.info(f"Discovery complete! Found {total_found} total accelerators")
        return total_found


def main():
    """Run accelerator discovery"""
    try:
        # Initialize builder
        builder = AcceleratorDirectoryBuilder()
        
        # Discover accelerators
        count = builder.discover_accelerators()
        
        print(f"🎉 Discovery Complete!")
        print(f"Found {count} blockchain accelerators in Europe and India")
        print(f"Results saved to: {builder.accelerators_file}")
        print(f"Logs saved to: data/system_logs.csv")
        
    except Exception as e:
        logging.error(f"Main execution failed: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()