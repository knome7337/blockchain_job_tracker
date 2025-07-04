"""
Climate + AI + Blockchain Accelerator Job Tracker
Module 0: Accelerator Directory Builder (Optimized)
Python 3.10+ Compatible

Focus: Climate x Web3 accelerators and job opportunities
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
    
    # Configuration constants - easier to maintain and modify
    SEARCH_TERMS = {
        'climate': ['climate tech', 'sustainability', 'green startup', 'clean energy', 'carbon removal', 'climate nonprofit'],
        'blockchain': ['blockchain startup', 'web3', 'crypto', 'defi', 'nft startup', 'DAO', 'smart contract'],
        'ai': ['AI for climate', 'ethical AI', 'AI sustainability', 'machine learning climate', 'AI governance'],
        'cross_sector': ['impact startup', 'climate + web3', 'regenerative finance', 'climate DAO', 'ReFi'],
        'high_intent': ['climate web3', 'climate blockchain', 'web3 for climate', 'climate crypto', 'blockchain sustainability'],
        'accelerator': ['fellowship program', 'incubator program', 'accelerator program', 'startup program'],
        'roles': ['community lead', 'smart contract developer', 'grant manager', 'tokenomics strategist', 'product manager']
    }
    
    LOCATIONS = {
        'europe': ['Europe', 'Berlin', 'London', 'Amsterdam', 'Zurich', 'Paris', 'Stockholm'],
        'india': ['India', 'Mumbai', 'Bangalore', 'Delhi', 'Hyderabad', 'Pune']
    }
    
    KEYWORDS_MAPPING = {
        'blockchain': ['blockchain', 'crypto', 'web3', 'defi', 'nft', 'dao', 'bitcoin', 'ethereum'],
        'climate': ['climate', 'sustainability', 'green', 'carbon', 'renewable', 'clean energy', 'environment'],
        'ai': ['artificial intelligence', 'machine learning', 'ai', 'ml', 'deep learning']
    }
    
    COUNTRY_MAPPING = {
        **{city.lower(): 'Germany' for city in ['germany', 'berlin', 'munich']},
        **{city.lower(): 'France' for city in ['france', 'paris']},
        **{city.lower(): 'United Kingdom' for city in ['uk', 'london', 'britain']},
        **{city.lower(): 'Netherlands' for city in ['netherlands', 'amsterdam']},
        **{city.lower(): 'Switzerland' for city in ['switzerland', 'zurich']},
        **{city.lower(): 'Sweden' for city in ['sweden', 'stockholm']},
        **{city.lower(): 'India' for city in ['india', 'mumbai', 'bangalore', 'delhi', 'hyderabad', 'pune', 'chennai']}
    }
    
    def __init__(self):
        # Load environment variables
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.google_cse_id = os.getenv('GOOGLE_CSE_ID')
        
        if not self.google_api_key or not self.google_cse_id:
            raise ValueError("Missing Google API credentials. Please set GOOGLE_API_KEY and GOOGLE_CSE_ID in .env file")
        
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.programs_file = "data/talent_programs_directory.csv"
        
        # Load discovery settings
        self.discovery_settings = self.load_discovery_settings()
        
        self.ensure_data_directory()
        
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        os.makedirs("data", exist_ok=True)
    
    def load_discovery_settings(self) -> Dict:
        """Load discovery configuration from JSON file"""
        try:
            settings_file = "config/discovery_settings.json"
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    return json.load(f)
            else:
                logging.warning(f"Discovery settings file not found: {settings_file}. Using defaults.")
                return self.get_default_discovery_settings()
        except Exception as e:
            logging.error(f"Failed to load discovery settings: {e}. Using defaults.")
            return self.get_default_discovery_settings()
    
    def get_default_discovery_settings(self) -> Dict:
        """Return default discovery settings if config file is missing"""
        return {
            "discovery_limits": {
                "default_time_limit_minutes": 20,
                "default_max_accelerators": 150,
                "comprehensive_time_limit_minutes": 30,
                "comprehensive_max_accelerators": 200,
                "emergency_time_limit_minutes": 10,
                "emergency_max_accelerators": 50
            },
            "rate_limiting": {
                "delay_between_queries_seconds": 1,
                "max_retries_per_query": 3,
                "timeout_per_request_seconds": 10
            },
            "quality_filters": {
                "min_query_results": 1,
                "max_queries_per_session": 25,
                "enable_deduplication": True
            },
            "logging": {
                "log_progress_interval": 5,
                "detailed_logging": True
            }
        }
        
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
            'num': 10
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
            org_name = search_result['title'].split(' - ')[0].strip()
            careers_url = self._find_careers_url(search_result['link'])
            
            text_content = f"{search_result['title']} {search_result['snippet']}"
            focus_tags = self._determine_focus_tags(text_content)
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
            careers_paths = ['/careers', '/jobs', '/career', '/work-with-us', '/join-us']
            
            for path in careers_paths:
                careers_url = urljoin(website_url, path)
                try:
                    response = requests.head(careers_url, timeout=5)
                    if response.status_code == 200:
                        return careers_url
                except:
                    continue
            
            return website_url
            
        except Exception:
            return website_url
    
    def _determine_focus_tags(self, text: str) -> List[str]:
        """Determine focus areas based on text content using keyword mapping"""
        text_lower = text.lower()
        tags = []
        
        for category, keywords in self.KEYWORDS_MAPPING.items():
            if any(keyword in text_lower for keyword in keywords):
                tags.append(category)
        
        return tags if tags else ['unknown']
    
    def _extract_country(self, text: str) -> str:
        """Extract country information from text using mapping"""
        text_lower = text.lower()
        
        for location, country in self.COUNTRY_MAPPING.items():
            if location in text_lower:
                return country
        
        return 'Unknown'
    
    def _generate_location_queries(self, base_terms: List[str], locations: List[str]) -> List[str]:
        """Generate location-specific queries efficiently"""
        queries = []
        for term in base_terms:
            for location in locations:
                queries.extend([
                    f"{term} {location}",
                    f"{term} jobs {location}",
                    f"{location} {term}"
                ])
        return queries
    
    def _generate_compound_queries(self, term_sets: List[List[str]], max_combinations: int = 10) -> List[str]:
        """Generate compound queries from multiple term sets"""
        queries = []
        import itertools
        
        for combo in itertools.product(*term_sets):
            if len(queries) >= max_combinations:
                break
            query = ' '.join(combo)
            queries.append(query)
        
        return queries
    
    def get_optimized_search_queries(self) -> List[str]:
        """Generate optimized search queries with priority ranking"""
        all_queries = []
        
        # 1. High-priority climate x Web3 queries
        high_priority = [
            "climate web3 jobs 2025",
            "ReFi jobs remote",
            "climate DAO hiring",
            "blockchain sustainability jobs",
            "climate tech web3 accelerator"
        ]
        
        # 2. Generate compound queries efficiently
        compound_base = [
            self.SEARCH_TERMS['climate'][:3],  # Top 3 climate terms
            self.SEARCH_TERMS['blockchain'][:3],  # Top 3 blockchain terms
            ['jobs', 'hiring', 'accelerator']
        ]
        compound_queries = self._generate_compound_queries(compound_base, max_combinations=15)
        
        # 3. Location-specific queries for key regions
        location_queries = []
        key_terms = self.SEARCH_TERMS['high_intent'] + self.SEARCH_TERMS['cross_sector']
        location_queries.extend(self._generate_location_queries(key_terms[:5], self.LOCATIONS['europe'][:3]))
        location_queries.extend(self._generate_location_queries(key_terms[:5], self.LOCATIONS['india'][:3]))
        
        # 4. Role and accelerator specific queries
        role_accelerator_queries = [
            f"{role} {acc_type}" 
            for role in self.SEARCH_TERMS['roles'][:3] 
            for acc_type in self.SEARCH_TERMS['accelerator'][:2]
        ]
        
        # Combine and prioritize
        all_queries.extend(high_priority)
        all_queries.extend(compound_queries[:10])
        all_queries.extend(location_queries[:15])
        all_queries.extend(role_accelerator_queries[:8])
        
        # Add site-specific searches for better targeting
        site_specific = [
            "climate blockchain site:.org",
            "web3 sustainability site:.io",
            "climate accelerator site:.com"
        ]
        all_queries.extend(site_specific)
        
        # Remove duplicates while preserving order (priority)
        seen = set()
        unique_queries = []
        for query in all_queries:
            if query.lower() not in seen:
                seen.add(query.lower())
                unique_queries.append(query)
        
        return unique_queries[:25]  # Limit to 25 high-quality queries
    
    def save_accelerators_to_csv(self, accelerators: List[Dict]):
        """Save discovered accelerators to CSV file"""
        try:
            file_exists = os.path.exists(self.programs_file)
            
            with open(self.programs_file, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'Name', 'Website', 'Country', 'Focus_Tags', 'Careers_URL', 
                    'Notes', 'Discovery_Date', 'Status', 'Query_Source'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                for accelerator in accelerators:
                    if accelerator:
                        writer.writerow(accelerator)
                        
            logging.info(f"Saved {len(accelerators)} accelerators to {self.programs_file}")
            
        except Exception as e:
            logging.error(f"Failed to save accelerators to CSV: {e}")
    
    def deduplicate_accelerators(self):
        """Remove duplicate accelerators based on website URL"""
        try:
            if not os.path.exists(self.programs_file):
                return
            
            seen_websites = set()
            unique_accelerators = []
            
            with open(self.programs_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    website = row.get('Website', '').strip().lower()
                    if website and website not in seen_websites:
                        seen_websites.add(website)
                        unique_accelerators.append(row)
            
            with open(self.programs_file, 'w', newline='', encoding='utf-8') as csvfile:
                if unique_accelerators:
                    fieldnames = unique_accelerators[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(unique_accelerators)
            
            logging.info(f"Deduplicated accelerators. Kept {len(unique_accelerators)} unique entries")
            
        except Exception as e:
            logging.error(f"Failed to deduplicate accelerators: {e}")
    
    def discover_accelerators(self, time_limit_minutes: int = None, max_accelerators: int = None) -> int:
        """Main method to discover climate x Web3 accelerators with safety limits"""
        # Use config values if not specified
        if time_limit_minutes is None:
            time_limit_minutes = self.discovery_settings['discovery_limits']['default_time_limit_minutes']
        if max_accelerators is None:
            max_accelerators = self.discovery_settings['discovery_limits']['default_max_accelerators']
            
        logging.info(f"Starting optimized accelerator discovery...")
        logging.info(f"Safety limits: {time_limit_minutes} minutes, max {max_accelerators} accelerators")
        
        queries = self.get_optimized_search_queries()
        total_found = 0
        start_time = time.time()
        time_limit_seconds = time_limit_minutes * 60
        
        for i, query in enumerate(queries, 1):
            # Check time limit
            elapsed_time = time.time() - start_time
            if elapsed_time > time_limit_seconds:
                logging.warning(f"⏰ Time limit of {time_limit_minutes} minutes reached. Stopping discovery.")
                break
            
            # Check entry limit
            if total_found >= max_accelerators:
                logging.warning(f"📊 Entry limit of {max_accelerators} accelerators reached. Stopping discovery.")
                break
            
            logging.info(f"Processing query {i}/{len(queries)}: {query} (Found: {total_found}, Time: {elapsed_time/60:.1f}m)")
            
            search_results = self.safe_search(query)
            
            if not search_results:
                logging.warning(f"No results for query: {query}")
                continue
            
            accelerators = []
            for result in search_results:
                # Check entry limit before processing each result
                if total_found + len(accelerators) >= max_accelerators:
                    logging.info(f"Entry limit reached while processing results. Stopping.")
                    break
                    
                accelerator_info = self.extract_accelerator_info(result)
                if accelerator_info:
                    accelerators.append(accelerator_info)
            
            if accelerators:
                self.save_accelerators_to_csv(accelerators)
                total_found += len(accelerators)
                logging.info(f"Found {len(accelerators)} accelerators from query: {query}")
            
            time.sleep(1)  # Rate limiting
        
        self.deduplicate_accelerators()
        
        final_time = (time.time() - start_time) / 60
        logging.info(f"Discovery complete! Found {total_found} total accelerators in {final_time:.1f} minutes")
        return total_found

    def run_comprehensive_discovery(self, time_limit_minutes: int = None, max_accelerators: int = None) -> int:
        """Comprehensive discovery with extended limits for thorough search"""
        # Use comprehensive config values if not specified
        if time_limit_minutes is None:
            time_limit_minutes = self.discovery_settings['discovery_limits']['comprehensive_time_limit_minutes']
        if max_accelerators is None:
            max_accelerators = self.discovery_settings['discovery_limits']['comprehensive_max_accelerators']
            
        logging.info("🚀 Starting comprehensive talent program discovery...")
        logging.info(f"Comprehensive mode: {time_limit_minutes} minutes, max {max_accelerators} accelerators")
        return self.discover_accelerators(time_limit_minutes, max_accelerators)
    
    def run_emergency_discovery(self) -> int:
        """Emergency discovery with minimal limits for quick testing"""
        time_limit = self.discovery_settings['discovery_limits']['emergency_time_limit_minutes']
        max_accelerators = self.discovery_settings['discovery_limits']['emergency_max_accelerators']
        
        logging.info("🚨 Starting emergency discovery mode...")
        logging.info(f"Emergency mode: {time_limit} minutes, max {max_accelerators} accelerators")
        return self.discover_accelerators(time_limit, max_accelerators)


def main():
    """Run accelerator discovery"""
    try:
        builder = AcceleratorDirectoryBuilder()
        count = builder.discover_accelerators()
        
        print(f"🎉 Discovery Complete!")
        print(f"Found {count} climate x Web3 accelerators")
        print(f"Results saved to: {builder.programs_file}")
        print(f"Logs saved to: data/system_logs.csv")
        
    except Exception as e:
        logging.error(f"Main execution failed: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()