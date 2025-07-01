"""
Climate + AI + Blockchain Accelerator Job Tracker
Module 0.5 IMPROVED: Accelerator Validator with Noise Filtering
Python 3.10+ Compatible

Enhanced to filter out job boards, news articles, and duplicates
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

class ImprovedAcceleratorValidator:
    """Module 0.5 Improved: Enhanced validator with noise filtering"""
    
    def __init__(self):
        self.accelerators_file = "data/accelerators_list.csv"
        self.timeout = 10
        self.user_agent = "Mozilla/5.0 (compatible; JobTracker/1.0)"
        
        # NOISE FILTERING PATTERNS
        self.job_board_domains = {
            'web3.career', 'cryptojobslist.com', 'builtin.com', 'glassdoor.co.in',
            'glassdoor.com', 'indeed.com', 'linkedin.com', 'angellist.com',
            'wellfound.com', 'jobs.lever.co', 'greenhouse.io'
        }
        
        self.news_patterns = [
            'announces', 'launches', 'signs mou', 'press release',
            'news', 'article', 'blog', 'questions with', 'interview'
        ]
        
        self.corporate_patterns = [
            'pwc.com', 'deloitte.com', 'kpmg.com', 'ey.com',
            'jobs-ta.pwc.com', 'careers.', 'job-listing'
        ]
        
        # REAL ACCELERATOR INDICATORS
        self.accelerator_keywords = [
            'accelerator', 'incubator', 'venture', 'startup program',
            'innovation lab', 'startup studio', 'venture studio'
        ]
        
    def is_noise_entry(self, accelerator_data: Dict) -> Tuple[bool, str]:
        """Detect if entry is noise (job board, news, duplicate, etc.)"""
        
        name = accelerator_data.get('Name', '').lower()
        website = accelerator_data.get('Website', '').lower()
        notes = accelerator_data.get('Notes', '').lower()
        
        # Check for job board domains
        domain = urlparse(website).netloc.lower()
        if any(job_domain in domain for job_domain in self.job_board_domains):
            return True, f"Job board domain: {domain}"
        
        # Check for news/blog patterns
        full_text = f"{name} {notes}".lower()
        for pattern in self.news_patterns:
            if pattern in full_text:
                return True, f"News/blog pattern: {pattern}"
        
        # Check for corporate job pages
        if any(corp_pattern in website for corp_pattern in self.corporate_patterns):
            return True, f"Corporate job page"
        
        # Check for obvious job listings
        if 'job-listing' in website or '/jobs/' in website:
            return True, "Direct job listing URL"
        
        # Check for specific noise patterns from our analysis
        noise_indicators = [
            'web3 jobs in', 'crypto jobs in', 'blockchain jobs in',
            'best startup programs', 'top companies', 'hiring'
        ]
        
        if any(indicator in full_text for indicator in noise_indicators):
            return True, f"Job aggregator content"
        
        return False, ""
    
    def calculate_accelerator_relevance(self, accelerator_data: Dict) -> int:
        """Calculate how likely this is a real accelerator (0-10)"""
        
        name = accelerator_data.get('Name', '').lower()
        website = accelerator_data.get('Website', '').lower()
        notes = accelerator_data.get('Notes', '').lower()
        focus_tags = accelerator_data.get('Focus_Tags', '').lower()
        
        relevance_score = 0
        
        # Positive indicators for real accelerators
        full_text = f"{name} {notes}".lower()
        
        # Strong accelerator keywords (+3 points each)
        strong_keywords = ['accelerator', 'incubator', 'venture capital', 'vc fund']
        for keyword in strong_keywords:
            if keyword in full_text:
                relevance_score += 3
                break  # Don't double count
        
        # Medium accelerator keywords (+2 points each)
        medium_keywords = ['startup program', 'innovation lab', 'venture studio', 'early stage']
        for keyword in medium_keywords:
            if keyword in full_text:
                relevance_score += 2
                break
        
        # Blockchain focus bonus (+2 points)
        if 'blockchain' in focus_tags:
            relevance_score += 2
        
        # Target geography bonus (+1 point)
        country = accelerator_data.get('Country', '').lower()
        target_countries = ['india', 'germany', 'france', 'united kingdom', 'netherlands', 'switzerland', 'sweden']
        if any(target_country in country for target_country in target_countries):
            relevance_score += 1
        
        # Known accelerator names (+3 points)
        known_accelerators = ['techstars', 'y combinator', 'masschallenge', 'startupbootcamp', 'outlier ventures']
        if any(known in name for known in known_accelerators):
            relevance_score += 3
        
        # Penalty for suspicious patterns
        suspicious_patterns = [
            'jobs in', 'hiring', 'career opportunities', 'job openings',
            'press release', 'announces', 'news'
        ]
        
        for pattern in suspicious_patterns:
            if pattern in full_text:
                relevance_score -= 2
        
        return max(0, min(relevance_score, 10))  # Cap between 0-10
    
    def enhanced_activity_score(self, website_health: Dict, careers_info: Dict, accelerator_data: Dict) -> int:
        """Enhanced activity scoring with accelerator relevance"""
        
        # First check if this is even a real accelerator
        relevance_score = self.calculate_accelerator_relevance(accelerator_data)
        
        # If relevance is too low, cap the activity score
        if relevance_score < 3:
            return min(self.original_activity_score(website_health, careers_info, accelerator_data), 4)
        
        # Calculate base activity score
        base_score = self.original_activity_score(website_health, careers_info, accelerator_data)
        
        # Apply relevance weighting
        if relevance_score >= 7:
            return base_score  # No penalty for highly relevant
        elif relevance_score >= 5:
            return max(base_score - 1, 0)  # Small penalty
        else:
            return max(base_score - 2, 0)  # Larger penalty
    
    def original_activity_score(self, website_health: Dict, careers_info: Dict, accelerator_data: Dict) -> int:
        """Original activity score calculation"""
        score = 0
        
        # Website accessibility (3 points max)
        if website_health['accessible']:
            if website_health['status_code'] == 200:
                score += 2
            else:
                score += 1
            
            if website_health['response_time'] < 3:
                score += 1
        
        # Careers page accessibility (2 points max)
        if careers_info['careers_accessible']:
            score += 1
            if careers_info['has_jobs']:
                score += 1
        
        # Job content quality (3 points max) - ADJUSTED TO BE LESS GENEROUS
        job_count = careers_info.get('job_count_estimate', 0)
        if job_count >= 10:  # Increased from 5
            score += 3
        elif job_count >= 3:  # Increased from 2
            score += 2
        elif job_count >= 1:
            score += 1
        
        # Platform integration (2 points max) - MORE SELECTIVE
        platforms = careers_info.get('job_platforms', 'none')
        if platforms != 'none':
            # Only give points for real job platforms, not mentions
            real_platforms = ['greenhouse', 'lever', 'workday', 'bamboohr']
            platform_list = platforms.split(', ')
            real_platform_count = sum(1 for p in platform_list if p in real_platforms)
            score += min(real_platform_count, 2)
        
        return min(score, 10)
    
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
                'error': str(e)[:100]
            }
    
    def check_careers_page(self, careers_url: str, website_url: str) -> Dict:
        """Check if careers page exists and has job-related content"""
        try:
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
        
        return website_url
    
    def _detect_job_content(self, content: str) -> Dict:
        """Detect job-related content with improved accuracy"""
        content_lower = content.lower()
        
        # More specific job keywords
        job_keywords = [
            'open position', 'job opening', 'we are hiring', 'join our team',
            'current openings', 'available position', 'career opportunity',
            'apply now', 'job application', 'send resume'
        ]
        
        # More accurate platform detection - require actual integration
        platform_indicators = {
            'greenhouse': 'greenhouse.io' in content_lower and 'apply' in content_lower,
            'lever': ('lever.co' in content_lower or 'jobs.lever.co' in content_lower) and 'apply' in content_lower,
            'workday': 'workday.com' in content_lower and 'jobs' in content_lower,
            'bamboohr': 'bamboohr.com' in content_lower and 'careers' in content_lower,
            # Remove LinkedIn/Indeed as they're often just mentions
        }
        
        job_count = sum(1 for keyword in job_keywords if keyword in content_lower)
        
        # More conservative job estimation
        job_estimate = 0
        job_patterns = [
            r'(\d+)\s*(open|available|current)\s*(position|job|role)',
            r'(\d+)\s*(job|position|role|opening)',
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
        
        # Cap job estimates to prevent job board inflation
        if job_estimate > 100:
            job_estimate = min(job_estimate, 50)  # Cap inflated counts
        
        active_platforms = [platform for platform, present in platform_indicators.items() if present]
        
        return {
            'has_jobs': job_count > 0 or job_estimate > 0 or len(active_platforms) > 0,
            'job_count': job_estimate if job_estimate > 0 else job_count,
            'platforms': ', '.join(active_platforms) if active_platforms else 'none'
        }
    
    def validate_accelerator(self, accelerator_row: Dict) -> Dict:
        """Validate single accelerator with noise filtering"""
        try:
            # First check if this is noise
            is_noise, noise_reason = self.is_noise_entry(accelerator_row)
            
            if is_noise:
                logging.info(f"FILTERED OUT {accelerator_row.get('Name', 'Unknown')}: {noise_reason}")
                filtered_data = accelerator_row.copy()
                filtered_data.update({
                    'Status': 'filtered',
                    'Activity_Score': 0,
                    'Last_Validated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Validation_Notes': f'Filtered: {noise_reason}',
                    'Scrape_Priority': 'excluded',
                    'Accelerator_Relevance': 0
                })
                return filtered_data
            
            logging.info(f"Validating {accelerator_row.get('Name', 'Unknown')}")
            
            # Check website health
            website_health = self.check_website_health(accelerator_row['Website'])
            
            # Check careers page
            careers_info = self.check_careers_page(
                accelerator_row.get('Careers_URL', accelerator_row['Website']),
                accelerator_row['Website']
            )
            
            # Calculate enhanced activity score
            activity_score = self.enhanced_activity_score(website_health, careers_info, accelerator_row)
            relevance_score = self.calculate_accelerator_relevance(accelerator_row)
            
            # Determine status with higher thresholds
            status = self._determine_status_enhanced(activity_score, relevance_score)
            scrape_priority = self._determine_priority_enhanced(status, activity_score, relevance_score)
            
            notes = self._generate_validation_notes(website_health, careers_info, activity_score, relevance_score)
            
            enhanced_data = accelerator_row.copy()
            enhanced_data.update({
                'Status': status,
                'Activity_Score': activity_score,
                'Accelerator_Relevance': relevance_score,
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
            
            error_data = accelerator_row.copy()
            error_data.update({
                'Status': 'error',
                'Activity_Score': 0,
                'Last_Validated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Validation_Notes': f'Validation error: {str(e)[:100]}',
                'Scrape_Priority': 'low'
            })
            return error_data
    
    def _determine_status_enhanced(self, activity_score: int, relevance_score: int) -> str:
        """Enhanced status determination with relevance weighting"""
        
        # Must be relevant to be active
        if relevance_score < 4:
            return 'low_relevance'
        
        # Higher thresholds for active status
        if activity_score >= 8 and relevance_score >= 6:
            return 'active'
        elif activity_score >= 5 and relevance_score >= 4:
            return 'monitor'
        else:
            return 'inactive'
    
    def _determine_priority_enhanced(self, status: str, activity_score: int, relevance_score: int) -> str:
        """Enhanced priority determination"""
        if status == 'active' and relevance_score >= 7:
            return 'high'
        elif status == 'active' or (status == 'monitor' and activity_score >= 6):
            return 'medium'
        elif status == 'filtered':
            return 'excluded'
        else:
            return 'low'
    
    def _generate_validation_notes(self, website_health: Dict, careers_info: Dict, activity_score: int, relevance_score: int) -> str:
        """Generate enhanced validation notes"""
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
        
        notes.append(f"Activity: {activity_score}/10")
        notes.append(f"Relevance: {relevance_score}/10")
        
        return "; ".join(notes)
    
    def validate_all_accelerators(self) -> int:
        """Validate all accelerators with enhanced filtering"""
        if not os.path.exists(self.accelerators_file):
            logging.error(f"Accelerators file not found: {self.accelerators_file}")
            return 0
        
        logging.info("Starting enhanced accelerator validation with noise filtering...")
        
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
        filtered_count = 0
        
        for i, accelerator in enumerate(accelerators, 1):
            logging.info(f"Processing {i}/{len(accelerators)}: {accelerator.get('Name', 'Unknown')}")
            
            validated = self.validate_accelerator(accelerator)
            validated_accelerators.append(validated)
            
            if validated.get('Status') == 'filtered':
                filtered_count += 1
            
            # Rate limiting
            time.sleep(1)
        
        # Save enhanced data
        self._save_validated_accelerators(validated_accelerators)
        
        # Log enhanced summary
        self._log_enhanced_summary(validated_accelerators, filtered_count)
        
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
    
    def _log_enhanced_summary(self, validated_accelerators: List[Dict], filtered_count: int):
        """Log enhanced validation summary"""
        total = len(validated_accelerators)
        if total == 0:
            return
        
        # Count by status
        status_counts = {}
        priority_counts = {}
        score_sum = 0
        relevance_sum = 0
        
        for acc in validated_accelerators:
            status = acc.get('Status', 'unknown')
            priority = acc.get('Scrape_Priority', 'unknown')
            score = acc.get('Activity_Score', 0)
            relevance = acc.get('Accelerator_Relevance', 0)
            
            status_counts[status] = status_counts.get(status, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
            score_sum += score
            relevance_sum += relevance
        
        valid_entries = total - filtered_count
        avg_score = round(score_sum / total, 1) if total > 0 else 0
        avg_relevance = round(relevance_sum / total, 1) if total > 0 else 0
        
        logging.info(f"Enhanced Validation Summary:")
        logging.info(f"  Total processed: {total}")
        logging.info(f"  Filtered as noise: {filtered_count} ({(filtered_count/total)*100:.1f}%)")
        logging.info(f"  Valid accelerators: {valid_entries}")
        logging.info(f"  Average Activity Score: {avg_score}/10")
        logging.info(f"  Average Relevance Score: {avg_relevance}/10")
        logging.info(f"  Status Distribution: {dict(status_counts)}")
        logging.info(f"  Priority Distribution: {dict(priority_counts)}")


def main():
    """Run enhanced accelerator validation"""
    try:
        validator = ImprovedAcceleratorValidator()
        count = validator.validate_all_accelerators()
        
        print(f"\n🎉 Enhanced Validation Complete!")
        print(f"Processed {count} accelerators with noise filtering")
        print(f"Enhanced data saved to: {validator.accelerators_file}")
        print(f"Check logs for detailed summary including filtered entries")
        
    except Exception as e:
        logging.error(f"Enhanced validation failed: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()