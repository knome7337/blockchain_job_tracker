"""
Climate + AI + Blockchain Accelerator Job Tracker
Module 0.5: Accelerator Validator
Python 3.10+ Compatible

Validates accelerator activity and job posting availability
"""

import os
import csv
import time
import logging
import requests
from datetime import datetime
from typing import Dict, List, Tuple
from urllib.parse import urljoin, urlparse
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

class AcceleratorValidator:
    """Module 0.5: Validate accelerator activity and job posting availability"""
    
    def __init__(self):
        self.accelerators_file = "data/accelerators_list.csv"
        self.timeout = 10  # seconds
        self.user_agent = "Mozilla/5.0 (compatible; JobTracker/1.0)"
        
    def check_website_health(self, url: str) -> Dict:
        """Check if website is accessible and responsive"""
        try:
            start_time = time.time()
            headers = {'User-Agent': self.user_agent}
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response_time = time.time() - start_time
            
            return {
                'accessible': True,
                'status_code': response.status_code,
                'response_time': round(response_time, 2),
                'error': None
            }
            
        except requests.exceptions.Timeout:
            return {
                'accessible': False,
                'status_code': 0,
                'response_time': self.timeout,
                'error': 'timeout'
            }
        except requests.exceptions.ConnectionError:
            return {
                'accessible': False,
                'status_code': 0,
                'response_time': 0,
                'error': 'connection_error'
            }
        except Exception as e:
            return {
                'accessible': False,
                'status_code': 0,
                'response_time': 0,
                'error': str(e)[:100]  # Truncate long errors
            }
    
    def check_careers_page(self, careers_url: str, website_url: str) -> Dict:
        """Check if careers page exists and has job-related content"""
        try:
            # If careers_url is same as website, try to find actual careers page
            if careers_url == website_url:
                careers_url = self._find_careers_page(website_url)
            
            headers = {'User-Agent': self.user_agent}
            response = requests.get(careers_url, headers=headers, timeout=self.timeout)
            
            if response.status_code != 200:
                return {
                    'careers_accessible': False,
                    'has_jobs': False,
                    'careers_url_final': careers_url,
                    'error': f'HTTP {response.status_code}'
                }
            
            # Check for job-related content
            content = response.text.lower()
            job_indicators = self._detect_job_content(content)
            
            return {
                'careers_accessible': True,
                'has_jobs': job_indicators['has_jobs'],
                'job_count_estimate': job_indicators['job_count'],
                'careers_url_final': careers_url,
                'job_platforms': job_indicators['platforms'],
                'error': None
            }
            
        except Exception as e:
            return {
                'careers_accessible': False,
                'has_jobs': False,
                'careers_url_final': careers_url,
                'error': str(e)[:100]
            }
    
    def _find_careers_page(self, website_url: str) -> str:
        """Try to find actual careers page from website"""
        careers_paths = [
            '/careers', '/jobs', '/career', '/work-with-us', '/join-us',
            '/open-positions', '/opportunities', '/hiring', '/team/join'
        ]
        
        headers = {'User-Agent': self.user_agent}
        
        for path in careers_paths:
            try:
                careers_url = urljoin(website_url, path)
                response = requests.head(careers_url, headers=headers, timeout=5)
                if response.status_code == 200:
                    return careers_url
            except:
                continue
        
        return website_url  # Fallback to main website
    
    def _detect_job_content(self, content: str) -> Dict:
        """Detect job-related content on careers page"""
        content_lower = content.lower()
        
        # Job keywords
        job_keywords = [
            'open position', 'job opening', 'we are hiring', 'join our team',
            'current openings', 'available position', 'career opportunity',
            'apply now', 'job application', 'send resume', 'cv'
        ]
        
        # Platform indicators
        platform_indicators = {
            'greenhouse': 'greenhouse.io' in content_lower,
            'lever': 'lever.co' in content_lower or 'jobs.lever.co' in content_lower,
            'workday': 'workday.com' in content_lower,
            'bamboohr': 'bamboohr.com' in content_lower,
            'linkedin': 'linkedin.com/jobs' in content_lower,
            'indeed': 'indeed.com' in content_lower,
            'angellist': 'angel.co' in content_lower or 'wellfound.com' in content_lower
        }
        
        # Count job indicators
        job_count = sum(1 for keyword in job_keywords if keyword in content_lower)
        
        # Estimate number of jobs based on content patterns
        job_estimate = 0
        job_patterns = [
            r'(\d+)\s*(open|available|current)\s*(position|job|role)',
            r'(\d+)\s*(job|position|role|opening)',
            r'view\s*all\s*(\d+)\s*(job|position)'
        ]
        
        for pattern in job_patterns:
            matches = re.findall(pattern, content_lower)
            if matches:
                try:
                    numbers = [int(match[0]) for match in matches]
                    job_estimate = max(numbers)
                    break
                except:
                    continue
        
        # Detect active platforms
        active_platforms = [platform for platform, present in platform_indicators.items() if present]
        
        return {
            'has_jobs': job_count > 0 or job_estimate > 0 or len(active_platforms) > 0,
            'job_count': job_estimate if job_estimate > 0 else job_count,
            'platforms': ', '.join(active_platforms) if active_platforms else 'none'
        }
    
    def calculate_activity_score(self, website_health: Dict, careers_info: Dict, accelerator_data: Dict) -> int:
        """Calculate activity score from 1-10 based on multiple factors"""
        score = 0
        
        # Website accessibility (3 points max)
        if website_health['accessible']:
            if website_health['status_code'] == 200:
                score += 2
            else:
                score += 1
            
            # Response time bonus
            if website_health['response_time'] < 3:
                score += 1
        
        # Careers page accessibility (2 points max)
        if careers_info['careers_accessible']:
            score += 1
            if careers_info['has_jobs']:
                score += 1
        
        # Job content quality (3 points max)
        if careers_info.get('job_count_estimate', 0) > 0:
            if careers_info['job_count_estimate'] >= 5:
                score += 3
            elif careers_info['job_count_estimate'] >= 2:
                score += 2
            else:
                score += 1
        
        # Platform integration (2 points max)
        platforms = careers_info.get('job_platforms', 'none')
        if platforms != 'none':
            platform_count = len(platforms.split(', '))
            score += min(platform_count, 2)
        
        return min(score, 10)  # Cap at 10
    
    def determine_status(self, activity_score: int, website_health: Dict, careers_info: Dict) -> str:
        """Determine accelerator status based on validation results"""
        if not website_health['accessible']:
            return 'error'
        
        if activity_score >= 7:
            return 'active'
        elif activity_score >= 4:
            return 'monitor'
        else:
            return 'inactive'
    
    def determine_scrape_priority(self, status: str, activity_score: int) -> str:
        """Determine scraping priority"""
        if status == 'active':
            return 'high'
        elif status == 'monitor':
            return 'medium'
        else:
            return 'low'
    
    def validate_accelerator(self, accelerator_row: Dict) -> Dict:
        """Validate single accelerator and return enhanced data"""
        try:
            logging.info(f"Validating {accelerator_row.get('Name', 'Unknown')}")
            
            # Check website health
            website_health = self.check_website_health(accelerator_row['Website'])
            
            # Check careers page
            careers_info = self.check_careers_page(
                accelerator_row.get('Careers_URL', accelerator_row['Website']),
                accelerator_row['Website']
            )
            
            # Calculate activity score
            activity_score = self.calculate_activity_score(website_health, careers_info, accelerator_row)
            
            # Determine status and priority
            status = self.determine_status(activity_score, website_health, careers_info)
            scrape_priority = self.determine_scrape_priority(status, activity_score)
            
            # Generate validation notes
            notes = self._generate_validation_notes(website_health, careers_info, activity_score)
            
            # Return enhanced accelerator data
            enhanced_data = accelerator_row.copy()
            enhanced_data.update({
                'Status': status,
                'Activity_Score': activity_score,
                'Last_Validated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Validation_Notes': notes,
                'Scrape_Priority': scrape_priority,
                'Website_Accessible': website_health['accessible'],
                'Response_Time': website_health['response_time'],
                'Careers_Accessible': careers_info['careers_accessible'],
                'Has_Jobs': careers_info['has_jobs'],
                'Job_Count_Estimate': careers_info.get('job_count_estimate', 0),
                'Job_Platforms': careers_info.get('job_platforms', 'none'),
                'Careers_URL': careers_info.get('careers_url_final', accelerator_row.get('Careers_URL', ''))
            })
            
            return enhanced_data
            
        except Exception as e:
            logging.error(f"Validation failed for {accelerator_row.get('Name', 'Unknown')}: {e}")
            
            # Return error status
            error_data = accelerator_row.copy()
            error_data.update({
                'Status': 'error',
                'Activity_Score': 0,
                'Last_Validated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Validation_Notes': f'Validation error: {str(e)[:100]}',
                'Scrape_Priority': 'low'
            })
            return error_data
    
    def _generate_validation_notes(self, website_health: Dict, careers_info: Dict, activity_score: int) -> str:
        """Generate human-readable validation notes"""
        notes = []
        
        if website_health['accessible']:
            notes.append(f"Website OK ({website_health['response_time']}s)")
        else:
            notes.append(f"Website issues: {website_health['error']}")
        
        if careers_info['careers_accessible']:
            if careers_info['has_jobs']:
                job_count = careers_info.get('job_count_estimate', 0)
                if job_count > 0:
                    notes.append(f"Jobs found: ~{job_count}")
                else:
                    notes.append("Job content detected")
                
                platforms = careers_info.get('job_platforms', 'none')
                if platforms != 'none':
                    notes.append(f"Platforms: {platforms}")
            else:
                notes.append("Careers page exists, no jobs")
        else:
            notes.append("No careers page")
        
        notes.append(f"Score: {activity_score}/10")
        
        return "; ".join(notes)
    
    def validate_all_accelerators(self) -> int:
        """Validate all accelerators in the CSV file"""
        if not os.path.exists(self.accelerators_file):
            logging.error(f"Accelerators file not found: {self.accelerators_file}")
            return 0
        
        logging.info("Starting accelerator validation...")
        
        # Read accelerators
        accelerators = []
        with open(self.accelerators_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            accelerators = list(reader)
        
        if not accelerators:
            logging.warning("No accelerators found to validate")
            return 0
        
        # Validate each accelerator
        validated_accelerators = []
        for i, accelerator in enumerate(accelerators, 1):
            logging.info(f"Validating {i}/{len(accelerators)}: {accelerator.get('Name', 'Unknown')}")
            
            validated = self.validate_accelerator(accelerator)
            validated_accelerators.append(validated)
            
            # Rate limiting - be respectful to websites
            time.sleep(1)
        
        # Save enhanced data
        self._save_validated_accelerators(validated_accelerators)
        
        # Log summary
        self._log_validation_summary(validated_accelerators)
        
        return len(validated_accelerators)
    
    def _save_validated_accelerators(self, validated_accelerators: List[Dict]):
        """Save validated accelerators back to CSV"""
        try:
            with open(self.accelerators_file, 'w', newline='', encoding='utf-8') as csvfile:
                if validated_accelerators:
                    fieldnames = validated_accelerators[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(validated_accelerators)
            
            logging.info(f"Saved {len(validated_accelerators)} validated accelerators")
            
        except Exception as e:
            logging.error(f"Failed to save validated accelerators: {e}")
    
    def _log_validation_summary(self, validated_accelerators: List[Dict]):
        """Log validation summary statistics"""
        total = len(validated_accelerators)
        if total == 0:
            return
        
        # Count by status
        status_counts = {}
        priority_counts = {}
        score_sum = 0
        
        for acc in validated_accelerators:
            status = acc.get('Status', 'unknown')
            priority = acc.get('Scrape_Priority', 'unknown')
            score = acc.get('Activity_Score', 0)
            
            status_counts[status] = status_counts.get(status, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
            score_sum += score
        
        avg_score = round(score_sum / total, 1)
        
        logging.info(f"Validation Summary:")
        logging.info(f"  Total: {total} accelerators")
        logging.info(f"  Average Score: {avg_score}/10")
        logging.info(f"  Status: {dict(status_counts)}")
        logging.info(f"  Priority: {dict(priority_counts)}")


def main():
    """Run accelerator validation"""
    try:
        validator = AcceleratorValidator()
        count = validator.validate_all_accelerators()
        
        print(f"\n🎉 Validation Complete!")
        print(f"Validated {count} accelerators")
        print(f"Enhanced data saved to: {validator.accelerators_file}")
        print(f"Check logs for detailed summary")
        
    except Exception as e:
        logging.error(f"Validation failed: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
