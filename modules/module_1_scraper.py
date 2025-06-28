"""
Module 1 IMPROVED: Smart Job Scraper with Better Detection
Fixes the issues identified in manual review
"""

import os
import csv
import time
import logging
import requests
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(module)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/system_logs.csv'),
        logging.StreamHandler()
    ]
)

class ImprovedJobScraper:
    """Improved job scraper with better job detection and filtering"""
    
    def __init__(self):
        self.accelerators_file = "data/accelerators_list.csv"
        self.jobs_file = "data/jobs_raw.csv"
        self.timeout = 15
        self.user_agent = "Mozilla/5.0 (compatible; JobTracker/1.0)"
        
        # Improved job title patterns - more specific
        self.valid_job_keywords = [
            'engineer', 'developer', 'manager', 'director', 'lead', 'analyst', 
            'specialist', 'coordinator', 'intern', 'associate', 'officer',
            'consultant', 'advisor', 'head of', 'chief', 'founder', 'partner',
            'scientist', 'researcher', 'designer', 'architect', 'product',
            'marketing', 'sales', 'business development', 'operations',
            'finance', 'legal', 'hr', 'human resources', 'strategy'
        ]
        
        # Patterns to EXCLUDE (noise filters)
        self.noise_patterns = [
            r'^(apply now|read more|careers|news|latest|about|contact)$',
            r'^[A-Z][a-z]+ [A-Z][a-z]+$',  # Just names like "John Smith"
            r'^(the|a|an) [^,]+$',  # Articles followed by single word
            r'^\d+$',  # Just numbers
            r'^(home|about us|contact|privacy|terms)$',
            r'^(program|accelerator|incubator|apply|application)$',
            r'^[^a-zA-Z]*$',  # No letters
        ]
        
        # Accelerator program indicators (not job openings)
        self.program_indicators = [
            'apply now', 'application', 'program', 'accelerator', 'cohort',
            'deadline', 'batch', 'startup', 'entrepreneur', 'founder'
        ]
        
        # Known job board patterns (more specific)
        self.job_board_patterns = {
            'greenhouse': {
                'indicators': ['greenhouse.io', 'boards.greenhouse.io'],
                'job_selector': '.opening a, [data-job]',
                'title_selector': None,  # Title is in the link text
                'exclude_selectors': ['.location', '.metadata']
            },
            'lever': {
                'indicators': ['lever.co', 'jobs.lever.co'],
                'job_selector': '.posting-title a, [data-qa="posting-title"]',
                'title_selector': None,
                'exclude_selectors': ['.posting-categories', '.posting-location']
            },
            'workday': {
                'indicators': ['workday.com'],
                'job_selector': '[data-automation-id="jobPostingTitle"] a',
                'title_selector': None,
                'exclude_selectors': ['[data-automation-id="jobPostingLocation"]']
            }
        }
        
    def load_accelerators_to_scrape(self) -> List[Dict]:
        """Load only high-quality accelerators for scraping"""
        try:
            accelerators = []
            with open(self.accelerators_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    status = row.get('Status', '').lower()
                    priority = row.get('Scrape_Priority', '').lower()
                    
                    # Include both high and medium priority accelerators for testing
                    if status in ['active', 'monitor'] and priority in ['high', 'medium']:
                        accelerators.append(row)
            
            # Sort by activity score
            accelerators.sort(key=lambda x: -int(x.get('Activity_Score', 0)))
            
            logging.info(f"Loaded {len(accelerators)} high and medium priority accelerators for scraping")
            return accelerators
            
        except Exception as e:
            logging.error(f"Failed to load accelerators: {e}")
            return []
    
    def is_valid_job_title(self, title: str) -> bool:
        """Check if a title looks like a real job posting"""
        if not title or len(title.strip()) < 3:
            return False
        
        title_clean = title.strip().lower()
        
        # Check noise patterns
        for pattern in self.noise_patterns:
            if re.match(pattern, title_clean, re.IGNORECASE):
                return False
        
        # Check for program/application indicators
        if any(indicator in title_clean for indicator in self.program_indicators):
            return False
        
        # Must contain at least one job-related keyword
        if not any(keyword in title_clean for keyword in self.valid_job_keywords):
            return False
        
        # Length checks
        if len(title) < 5 or len(title) > 150:
            return False
        
        return True
    
    def find_actual_careers_page(self, base_url: str) -> str:
        """Try to find the actual careers page URL"""
        try:
            headers = {'User-Agent': self.user_agent}
            response = requests.get(base_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return base_url
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for actual careers links
            careers_patterns = [
                r'careers?(?!\.)',  # careers but not careers.something (domain)
                r'jobs?(?!\.)',
                r'work.with.us',
                r'join.us',
                r'opportunities'
            ]
            
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').lower()
                text = link.get_text(strip=True).lower()
                
                for pattern in careers_patterns:
                    if re.search(pattern, href) or re.search(pattern, text):
                        careers_url = urljoin(base_url, link.get('href'))
                        
                        # Verify it's not a domain or external link
                        if urlparse(careers_url).netloc == urlparse(base_url).netloc:
                            return careers_url
            
            return base_url
            
        except Exception as e:
            logging.warning(f"Failed to find careers page for {base_url}: {e}")
            return base_url
    
    def detect_job_board_type(self, content: str, url: str) -> Optional[str]:
        """Detect job board type more accurately"""
        content_lower = content.lower()
        url_lower = url.lower()
        
        for board_type, config in self.job_board_patterns.items():
            for indicator in config['indicators']:
                if indicator in url_lower:
                    # Also check if the page actually has job board structure
                    soup = BeautifulSoup(content, 'html.parser')
                    if soup.select(config['job_selector']):
                        return board_type
        
        return None
    
    def scrape_job_board_jobs(self, soup: BeautifulSoup, base_url: str, board_type: str) -> List[Dict]:
        """Scrape jobs from known job boards with better filtering"""
        jobs = []
        
        try:
            config = self.job_board_patterns[board_type]
            job_elements = soup.select(config['job_selector'])
            
            for job_elem in job_elements[:10]:  # Limit to prevent spam
                try:
                    # Extract title and URL
                    if job_elem.name == 'a':
                        title = job_elem.get_text(strip=True)
                        job_url = job_elem.get('href', '')
                    else:
                        title_link = job_elem.find('a')
                        if title_link:
                            title = title_link.get_text(strip=True)
                            job_url = title_link.get('href', '')
                        else:
                            title = job_elem.get_text(strip=True)
                            job_url = ''
                    
                    # Validate job title
                    if not self.is_valid_job_title(title):
                        continue
                    
                    # Make URL absolute
                    if job_url and not job_url.startswith('http'):
                        job_url = urljoin(base_url, job_url)
                    
                    # Extract location (try to find nearby location element)
                    location = 'Remote/Unknown'
                    location_elem = job_elem.find_next(class_=re.compile(r'location', re.I))
                    if location_elem:
                        location = location_elem.get_text(strip=True)
                    
                    jobs.append({
                        'title': title,
                        'location': location,
                        'job_url': job_url or base_url,
                        'snippet': title,  # Keep it simple
                        'platform': board_type
                    })
                    
                except Exception as e:
                    logging.warning(f"Failed to parse {board_type} job element: {e}")
                    continue
            
            logging.info(f"Found {len(jobs)} valid jobs via {board_type}")
            
        except Exception as e:
            logging.error(f"Failed to scrape {board_type} jobs: {e}")
        
        return jobs
    
    def scrape_generic_jobs(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Improved generic job scraping with better filtering"""
        jobs = []
        
        try:
            # Method 1: Look for dedicated job/career sections
            job_sections = soup.find_all(['div', 'section', 'ul'], 
                                       class_=re.compile(r'job|career|position|opening', re.I))
            
            for section in job_sections:
                # Look for job links within the section
                job_links = section.find_all('a', href=True)
                
                for link in job_links:
                    title = link.get_text(strip=True)
                    href = link.get('href')
                    
                    # Validate the job title
                    if self.is_valid_job_title(title):
                        if href and not href.startswith('http'):
                            href = urljoin(base_url, href)
                        
                        jobs.append({
                            'title': title,
                            'location': 'Remote/Unknown',
                            'job_url': href or base_url,
                            'snippet': title,
                            'platform': 'generic'
                        })
            
            # Method 2: Look for career page links (if no jobs found)
            if not jobs:
                career_links = soup.find_all('a', href=True)
                for link in career_links:
                    href = link.get('href', '').lower()
                    text = link.get_text(strip=True)
                    
                    # Look for careers page indicators
                    if any(indicator in href for indicator in ['/careers', '/jobs', '/opportunities']):
                        if self.is_valid_job_title(text):
                            full_url = urljoin(base_url, link.get('href'))
                            jobs.append({
                                'title': text,
                                'location': 'Remote/Unknown',
                                'job_url': full_url,
                                'snippet': text,
                                'platform': 'generic'
                            })
            
            # Remove duplicates and limit results
            seen_titles = set()
            unique_jobs = []
            for job in jobs:
                title_key = job['title'].lower().strip()
                if title_key not in seen_titles and len(unique_jobs) < 5:
                    seen_titles.add(title_key)
                    unique_jobs.append(job)
            
            logging.info(f"Found {len(unique_jobs)} valid jobs via generic scraping")
            return unique_jobs
            
        except Exception as e:
            logging.error(f"Failed to scrape generic jobs: {e}")
            return []
    
    def scrape_accelerator_jobs(self, accelerator: Dict) -> List[Dict]:
        """Scrape jobs from a single accelerator with improved logic"""
        try:
            accelerator_name = accelerator.get('Name', 'Unknown')
            website_url = accelerator.get('Website', '')
            
            logging.info(f"Scraping jobs from {accelerator_name}")
            
            # Try to find actual careers page
            careers_url = self.find_actual_careers_page(website_url)
            
            # Make request
            headers = {'User-Agent': self.user_agent}
            response = requests.get(careers_url, headers=headers, timeout=self.timeout)
            
            if response.status_code != 200:
                logging.warning(f"Failed to access {careers_url}: HTTP {response.status_code}")
                return []
            
            # Parse content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Detect job board type
            job_board_type = self.detect_job_board_type(response.text, careers_url)
            
            # Scrape based on detected platform
            jobs = []
            if job_board_type:
                jobs = self.scrape_job_board_jobs(soup, careers_url, job_board_type)
            else:
                jobs = self.scrape_generic_jobs(soup, careers_url)
            
            # Add accelerator context to each job
            for job in jobs:
                job.update({
                    'accelerator_name': accelerator_name,
                    'accelerator_website': website_url,
                    'accelerator_country': accelerator.get('Country', 'Unknown'),
                    'accelerator_focus': accelerator.get('Focus_Tags', ''),
                    'discovered_date': datetime.now().strftime('%Y-%m-%d'),
                    'source_url': careers_url
                })
            
            if jobs:
                logging.info(f"✅ Found {len(jobs)} valid jobs from {accelerator_name}")
            else:
                logging.warning(f"❌ No valid jobs found from {accelerator_name}")
            
            return jobs
            
        except Exception as e:
            logging.error(f"Failed to scrape {accelerator_name}: {e}")
            return []
    
    def save_jobs_to_csv(self, jobs: List[Dict]):
        """Save jobs with overwrite to ensure clean data"""
        if not jobs:
            logging.warning("No jobs to save")
            return
        
        try:
            with open(self.jobs_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'title', 'location', 'job_url', 'snippet', 'platform',
                    'accelerator_name', 'accelerator_website', 'accelerator_country',
                    'accelerator_focus', 'discovered_date', 'source_url'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # Write job data
                for job in jobs:
                    writer.writerow(job)
                        
            logging.info(f"Saved {len(jobs)} jobs to {self.jobs_file}")
            
        except Exception as e:
            logging.error(f"Failed to save jobs to CSV: {e}")
    
    def scrape_high_quality_jobs(self) -> int:
        """Main method focusing on high-quality accelerators only"""
        logging.info("Starting improved job scraping from high-quality accelerators...")
        
        # Load only high-priority accelerators
        accelerators = self.load_accelerators_to_scrape()
        
        if not accelerators:
            logging.error("No high-priority accelerators found for scraping")
            return 0
        
        all_jobs = []
        successful_scrapes = 0
        
        for i, accelerator in enumerate(accelerators, 1):
            accelerator_name = accelerator.get('Name', 'Unknown')
            
            logging.info(f"Processing {i}/{len(accelerators)}: {accelerator_name}")
            
            # Scrape jobs from this accelerator
            jobs = self.scrape_accelerator_jobs(accelerator)
            
            if jobs:
                all_jobs.extend(jobs)
                successful_scrapes += 1
            
            # Rate limiting
            time.sleep(3)  # Slightly longer delay
        
        # Remove duplicates globally
        unique_jobs = self.deduplicate_jobs_advanced(all_jobs)
        
        # Save jobs
        if unique_jobs:
            self.save_jobs_to_csv(unique_jobs)
        
        # Log summary
        logging.info(f"Improved scraping complete!")
        logging.info(f"  High-priority accelerators processed: {len(accelerators)}")
        logging.info(f"  Successful scrapes: {successful_scrapes}")
        logging.info(f"  Raw jobs found: {len(all_jobs)}")
        logging.info(f"  Unique quality jobs: {len(unique_jobs)}")
        
        return len(unique_jobs)
    
    def deduplicate_jobs_advanced(self, jobs: List[Dict]) -> List[Dict]:
        """Advanced deduplication based on title similarity and URL"""
        if not jobs:
            return []
        
        unique_jobs = []
        seen_combinations = set()
        
        for job in jobs:
            # Create a unique key based on normalized title and domain
            title_normalized = re.sub(r'[^\w\s]', '', job['title'].lower().strip())
            domain = urlparse(job.get('job_url', '')).netloc.lower()
            
            key = (title_normalized, domain)
            
            if key not in seen_combinations:
                seen_combinations.add(key)
                unique_jobs.append(job)
        
        logging.info(f"Advanced deduplication: {len(jobs)} → {len(unique_jobs)} jobs")
        return unique_jobs


def main():
    """Run improved job scraping"""
    try:
        scraper = ImprovedJobScraper()
        job_count = scraper.scrape_high_quality_jobs()
        
        print(f"\n🎉 Improved Job Scraping Complete!")
        print(f"Found {job_count} high-quality jobs from top accelerators")
        print(f"Results saved to: {scraper.jobs_file}")
        print(f"Focus: Only 'active' status, 'high' priority accelerators")
        
    except Exception as e:
        logging.error(f"Job scraping failed: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()