"""
Module 3: Enhanced Email Alert System
Purpose: Deliver curated job matches via configurable email alerts
Compatible with successful Module 2 results (5.8/10 avg score, 14 high matches)
"""

import os
import csv
import json
import logging
import smtplib
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
import pandas as pd
from jinja2 import Template
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

class EnhancedEmailAlerts:
    """Enhanced email alert system with smart filtering and beautiful templates"""
    
    def __init__(self):
        self.scored_jobs_file = "data/jobs_scored.csv"
        self.alert_settings_file = "config/alert_settings.json"
        self.email_logs_file = "data/email_logs.csv"
        self.failed_alerts_file = "data/failed_alerts.csv"
        self.last_sent_file = "data/last_email_sent.json"
        
        # Load configuration
        self.alert_settings = self.load_alert_settings()
        self.email_config = self.load_email_config()
        
        # Email frequency mapping
        self.frequency_days = {
            'daily': 1,
            'weekly': 7,
            'bi-weekly': 14,
            'monthly': 30,
            'on-demand': 0
        }
        
    def load_alert_settings(self) -> Dict:
        """Load alert configuration with intelligent defaults"""
        try:
            with open(self.alert_settings_file, 'r') as f:
                settings = json.load(f)
            logging.info("Loaded alert settings successfully")
            return settings
        except Exception as e:
            logging.warning(f"Failed to load alert settings: {e}. Using defaults.")
            # Create default settings based on successful Module 2 results
            default_settings = {
                "frequency": "weekly",
                "min_score": 7.0,  # Focus on high matches from Module 2
                "max_jobs": 10,
                "sectors": ["blockchain", "climate", "ai"],
                "locations": ["remote", "berlin", "mumbai", "london", "amsterdam"],
                "email": {
                    "recipient": os.getenv('ALERT_EMAIL', 'your.email@example.com'),
                    "subject_prefix": "🚀 Weekly Blockchain Jobs",
                    "include_trends": True,
                    "include_csv": True,
                    "include_reasoning": True
                },
                "filtering": {
                    "exclude_keywords": ["intern", "unpaid", "junior"],
                    "require_remote": False,
                    "min_confidence": "medium"
                }
            }
            
            # Save default settings
            os.makedirs("config", exist_ok=True)
            with open(self.alert_settings_file, 'w') as f:
                json.dump(default_settings, f, indent=2)
            
            return default_settings
    
    def load_email_config(self) -> Dict:
        """Load email SMTP configuration"""
        return {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'username': os.getenv('SMTP_USERNAME', ''),
            'password': os.getenv('SMTP_PASSWORD', ''),
            'from_email': os.getenv('FROM_EMAIL', os.getenv('SMTP_USERNAME', ''))
        }
    
    def load_scored_jobs(self) -> List[Dict]:
        """Load jobs from Module 2 results"""
        try:
            if not os.path.exists(self.scored_jobs_file):
                logging.error(f"No scored jobs found at {self.scored_jobs_file}")
                logging.info("Run Module 2 first: python modules/module_2_matcher.py")
                return []
            
            jobs = []
            with open(self.scored_jobs_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Ensure score is numeric
                    try:
                        row['ai_score'] = float(row.get('ai_score', 0))
                        jobs.append(row)
                    except ValueError:
                        logging.warning(f"Invalid score for job: {row.get('title', 'Unknown')}")
                        continue
            
            logging.info(f"Loaded {len(jobs)} scored jobs from Module 2 results")
            return jobs
            
        except Exception as e:
            logging.error(f"Failed to load scored jobs: {e}")
            return []
    
    def filter_jobs_for_alert(self, jobs: List[Dict]) -> List[Dict]:
        """Apply smart filtering based on alert settings"""
        if not jobs:
            return []
        
        filtered_jobs = []
        settings = self.alert_settings
        
        for job in jobs:
            # Score threshold filter
            score = job.get('ai_score', 0)
            if score < settings.get('min_score', 7.0):
                continue
            
            # Exclude keywords filter
            title = job.get('title', '').lower()
            snippet = job.get('snippet', '').lower()
            text_content = f"{title} {snippet}"
            
            exclude_keywords = settings.get('filtering', {}).get('exclude_keywords', [])
            if any(keyword.lower() in text_content for keyword in exclude_keywords):
                logging.info(f"Filtered out job '{title}' due to exclude keywords")
                continue
            
            # Location filter
            location = job.get('location', '').lower()
            preferred_locations = settings.get('locations', [])
            
            # If location preferences specified, job must match at least one
            if preferred_locations:
                location_match = any(
                    pref_loc.lower() in location 
                    for pref_loc in preferred_locations
                )
                if not location_match:
                    continue
            
            # Confidence filter
            confidence = job.get('confidence', '').lower()
            min_confidence = settings.get('filtering', {}).get('min_confidence', 'low')
            
            if min_confidence == 'high' and confidence not in ['high']:
                continue
            elif min_confidence == 'medium' and confidence not in ['high', 'medium']:
                continue
            
            # Recommendation filter
            recommendation = job.get('recommendation', '').lower()
            if recommendation in ['poor', 'avoid']:
                continue
            
            filtered_jobs.append(job)
        
        # Sort by score (highest first) and limit
        filtered_jobs.sort(key=lambda x: x.get('ai_score', 0), reverse=True)
        max_jobs = settings.get('max_jobs', 10)
        
        result = filtered_jobs[:max_jobs]
        logging.info(f"Filtered jobs: {len(jobs)} → {len(result)} (min_score: {settings.get('min_score', 7.0)})")
        
        return result
    
    def should_send_alert(self) -> bool:
        """Check if it's time to send an alert based on frequency"""
        frequency = self.alert_settings.get('frequency', 'weekly')
        
        if frequency == 'on-demand':
            return False  # Only manual triggers
        
        try:
            with open(self.last_sent_file, 'r') as f:
                last_sent_data = json.load(f)
                last_sent = datetime.fromisoformat(last_sent_data['timestamp'])
        except:
            # No previous send record, should send
            return True
        
        days_since_last = (datetime.now() - last_sent).days
        required_days = self.frequency_days.get(frequency, 7)
        
        should_send = days_since_last >= required_days
        logging.info(f"Days since last alert: {days_since_last}, Required: {required_days}, Should send: {should_send}")
        
        return should_send
    
    def calculate_trends(self, jobs: List[Dict]) -> Dict:
        """Calculate job trends and analytics for email"""
        if not jobs:
            return {}
        
        # Score distribution
        scores = [job.get('ai_score', 0) for job in jobs]
        avg_score = sum(scores) / len(scores)
        
        # Sector breakdown
        sectors = {}
        for job in jobs:
            focus_tags = job.get('accelerator_focus', job.get('Focus_Tags', '')).lower()
            if 'blockchain' in focus_tags or 'web3' in focus_tags:
                sectors['blockchain'] = sectors.get('blockchain', 0) + 1
            if 'climate' in focus_tags:
                sectors['climate'] = sectors.get('climate', 0) + 1
            if 'ai' in focus_tags:
                sectors['ai'] = sectors.get('ai', 0) + 1
        
        # Location breakdown
        locations = {}
        for job in jobs:
            location = job.get('location', 'Unknown')
            if 'remote' in location.lower():
                locations['Remote'] = locations.get('Remote', 0) + 1
            elif any(city in location.lower() for city in ['berlin', 'london', 'amsterdam']):
                locations['Europe'] = locations.get('Europe', 0) + 1
            elif any(city in location.lower() for city in ['mumbai', 'bangalore', 'delhi']):
                locations['India'] = locations.get('India', 0) + 1
            else:
                locations['Other'] = locations.get('Other', 0) + 1
        
        # Top accelerators
        accelerators = {}
        for job in jobs:
            acc_name = job.get('accelerator_name', job.get('company', 'Unknown'))
            accelerators[acc_name] = accelerators.get(acc_name, 0) + 1
        
        top_accelerators = sorted(accelerators.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_jobs': len(jobs),
            'avg_score': round(avg_score, 1),
            'score_distribution': {
                'excellent (9-10)': len([s for s in scores if s >= 9]),
                'good (7-8)': len([s for s in scores if 7 <= s < 9]),
                'moderate (5-6)': len([s for s in scores if 5 <= s < 7])
            },
            'sector_breakdown': sectors,
            'location_breakdown': locations,
            'top_accelerators': top_accelerators
        }
    
    def create_email_template(self) -> str:
        """Beautiful HTML email template inspired by successful results"""
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Weekly Blockchain Job Matches</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 20px; background-color: #f7f9fc; }
        .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 20px; text-align: center; }
        .header h1 { margin: 0; font-size: 24px; font-weight: 600; }
        .summary { background: #f8fafc; padding: 20px; border-left: 4px solid #4f46e5; margin: 20px; border-radius: 4px; }
        .summary h2 { margin: 0 0 10px 0; color: #1e293b; font-size: 18px; }
        .summary-stats { display: flex; justify-content: space-between; flex-wrap: wrap; margin-top: 15px; }
        .stat { text-align: center; }
        .stat-number { font-size: 24px; font-weight: bold; color: #4f46e5; }
        .stat-label { font-size: 12px; color: #64748b; text-transform: uppercase; }
        .job { border: 1px solid #e2e8f0; margin: 20px; border-radius: 8px; overflow: hidden; }
        .job-header { background: #f8fafc; padding: 15px 20px; border-bottom: 1px solid #e2e8f0; }
        .job-title { font-size: 18px; font-weight: 600; color: #1e293b; margin: 0; }
        .job-meta { font-size: 14px; color: #64748b; margin: 5px 0 0 0; }
        .job-content { padding: 20px; }
        .score-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 14px; font-weight: 600; }
        .score-excellent { background: #dcfce7; color: #166534; }
        .score-good { background: #dbeafe; color: #1d4ed8; }
        .score-moderate { background: #fef3c7; color: #d97706; }
        .reasoning { background: #f1f5f9; padding: 15px; border-radius: 6px; margin: 15px 0; font-style: italic; }
        .match-factors { margin: 10px 0; }
        .factor { display: inline-block; background: #e0e7ff; color: #3730a3; padding: 4px 8px; border-radius: 12px; font-size: 12px; margin: 2px; }
        .apply-btn { display: inline-block; background: #4f46e5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: 500; margin: 10px 0; }
        .apply-btn:hover { background: #4338ca; }
        .trends { margin: 20px; padding: 20px; background: #f8fafc; border-radius: 8px; }
        .trends h3 { margin: 0 0 15px 0; color: #1e293b; }
        .trend-item { margin: 8px 0; }
        .footer { text-align: center; padding: 20px; color: #64748b; font-size: 14px; }
        .footer a { color: #4f46e5; text-decoration: none; }
        @media (max-width: 600px) {
            .summary-stats { flex-direction: column; }
            .stat { margin: 10px 0; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 {{ subject_prefix }}</h1>
            <p>{{ formatted_date }} • {{ total_jobs }} High-Quality Matches Found</p>
        </div>
        
        {% if include_trends and trends %}
        <div class="summary">
            <h2>📊 Weekly Summary</h2>
            <p>Great week for blockchain opportunities! Found <strong>{{ trends.total_jobs }}</strong> jobs with an average match score of <strong>{{ trends.avg_score }}/10</strong>.</p>
            
            <div class="summary-stats">
                <div class="stat">
                    <div class="stat-number">{{ trends.score_distribution.get('excellent (9-10)', 0) }}</div>
                    <div class="stat-label">Excellent Matches</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{{ trends.score_distribution.get('good (7-8)', 0) }}</div>
                    <div class="stat-label">Good Matches</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{{ trends.location_breakdown.get('Remote', 0) }}</div>
                    <div class="stat-label">Remote Jobs</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{{ trends.sector_breakdown.get('blockchain', 0) }}</div>
                    <div class="stat-label">Blockchain Roles</div>
                </div>
            </div>
        </div>
        {% endif %}
        
        {% for job in jobs %}
        <div class="job">
            <div class="job-header">
                <h3 class="job-title">{{ job.title }}</h3>
                <p class="job-meta">
                    <strong>{{ job.get('accelerator_name', job.get('company', 'Unknown')) }}</strong> • 
                    {{ job.get('location', 'Location not specified') }} •
                    <span class="score-badge score-{% if job.ai_score >= 9 %}excellent{% elif job.ai_score >= 7 %}good{% else %}moderate{% endif %}">
                        {{ job.ai_score }}/10 Match
                    </span>
                </p>
            </div>
            
            <div class="job-content">
                {% if include_reasoning and job.ai_reasoning %}
                <div class="reasoning">
                    <strong>Why it's a great match:</strong> {{ job.ai_reasoning }}
                </div>
                {% endif %}
                
                {% if job.match_factors %}
                <div class="match-factors">
                    <strong>Key Match Factors:</strong><br>
                    {% for factor in job.match_factors.split(';') %}
                        <span class="factor">{{ factor.strip() }}</span>
                    {% endfor %}
                </div>
                {% endif %}
                
                {% if job.recommendation %}
                <p><strong>Recommendation:</strong> {{ job.recommendation }}</p>
                {% endif %}
                
                {% if job.job_url and job.job_url != job.get('accelerator_website', '') %}
                <a href="{{ job.job_url }}" class="apply-btn" target="_blank">Apply Now →</a>
                {% else %}
                <a href="{{ job.get('accelerator_website', '#') }}" class="apply-btn" target="_blank">View on {{ job.get('accelerator_name', 'Company') }} →</a>
                {% endif %}
            </div>
        </div>
        {% endfor %}
        
        {% if include_trends and trends %}
        <div class="trends">
            <h3>📈 Market Trends</h3>
            
            {% if trends.top_accelerators %}
            <div class="trend-item">
                <strong>Most Active Accelerators:</strong>
                {% for acc, count in trends.top_accelerators %}
                    {{ acc }} ({{ count }} jobs){% if not loop.last %}, {% endif %}
                {% endfor %}
            </div>
            {% endif %}
            
            {% if trends.sector_breakdown %}
            <div class="trend-item">
                <strong>Sector Distribution:</strong>
                {% for sector, count in trends.sector_breakdown.items() %}
                    {{ sector|title }}: {{ count }}{% if not loop.last %}, {% endif %}
                {% endfor %}
            </div>
            {% endif %}
        </div>
        {% endif %}
        
        <div class="footer">
            <p>This alert was generated by your Blockchain Job Tracker system.</p>
            <p>To adjust your preferences or stop alerts, update your <code>config/alert_settings.json</code> file.</p>
            <p><a href="mailto:{{ from_email }}">Reply</a> to this email if you have feedback on the job matches.</p>
        </div>
    </div>
</body>
</html>
        """
    
    def generate_email_content(self, jobs: List[Dict], trends: Dict) -> Dict:
        """Generate beautiful email content with your successful Module 2 results"""
        template = Template(self.create_email_template())
        
        email_data = {
            'subject_prefix': self.alert_settings['email'].get('subject_prefix', '🚀 Weekly Blockchain Jobs'),
            'formatted_date': datetime.now().strftime('%B %d, %Y'),
            'total_jobs': len(jobs),
            'jobs': jobs,
            'trends': trends,
            'include_trends': self.alert_settings['email'].get('include_trends', True),
            'include_reasoning': self.alert_settings['email'].get('include_reasoning', True),
            'from_email': self.email_config['from_email']
        }
        
        html_content = template.render(**email_data)
        
        # Generate plain text version
        text_content = self.generate_text_content(jobs, trends)
        
        # Subject line with match count
        excellent_count = len([j for j in jobs if j.get('ai_score', 0) >= 9])
        good_count = len([j for j in jobs if 7 <= j.get('ai_score', 0) < 9])
        
        if excellent_count > 0:
            subject = f"🚀 {excellent_count} Excellent Blockchain Job Matches This Week!"
        elif good_count > 0:
            subject = f"🚀 {good_count} Great Blockchain Job Matches This Week"
        else:
            subject = f"🚀 {len(jobs)} New Blockchain Job Matches"
        
        return {
            'subject': subject,
            'html_content': html_content,
            'text_content': text_content
        }
    
    def generate_text_content(self, jobs: List[Dict], trends: Dict) -> str:
        """Generate plain text version of email"""
        lines = []
        lines.append("🚀 YOUR WEEKLY BLOCKCHAIN JOB MATCHES")
        lines.append("=" * 50)
        lines.append(f"Date: {datetime.now().strftime('%B %d, %Y')}")
        lines.append(f"Total Matches: {len(jobs)}")
        
        if trends:
            lines.append(f"Average Score: {trends.get('avg_score', 0)}/10")
            lines.append("")
        
        for i, job in enumerate(jobs, 1):
            lines.append(f"{i}. {job.get('title', 'Unknown Title')} - {job.get('ai_score', 0)}/10")
            lines.append(f"   Company: {job.get('accelerator_name', job.get('company', 'Unknown'))}")
            lines.append(f"   Location: {job.get('location', 'Not specified')}")
            
            if job.get('ai_reasoning'):
                lines.append(f"   Why it matches: {job.get('ai_reasoning', '')}")
            
            if job.get('job_url'):
                lines.append(f"   Apply: {job.get('job_url')}")
            
            lines.append("")
        
        lines.append("Generated by your Blockchain Job Tracker system")
        return "\n".join(lines)
    
    def create_csv_attachment(self, jobs: List[Dict]) -> str:
        """Create CSV attachment with job details"""
        try:
            csv_filename = f"data/job_matches_{datetime.now().strftime('%Y%m%d')}.csv"
            
            # Select key fields for CSV
            csv_fields = [
                'title', 'accelerator_name', 'location', 'ai_score', 
                'recommendation', 'confidence', 'job_url', 'ai_reasoning'
            ]
            
            with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=csv_fields)
                writer.writeheader()
                
                for job in jobs:
                    row = {field: job.get(field, '') for field in csv_fields}
                    writer.writerow(row)
            
            logging.info(f"Created CSV attachment: {csv_filename}")
            return csv_filename
            
        except Exception as e:
            logging.error(f"Failed to create CSV attachment: {e}")
            return ""
    
    def send_email_with_retries(self, email_content: Dict, jobs: List[Dict], max_retries: int = 3) -> bool:
        """Send email with retry logic and attachment support"""
        
        for attempt in range(max_retries):
            try:
                # Create message
                msg = MimeMultipart('alternative')
                msg['Subject'] = email_content['subject']
                msg['From'] = self.email_config['from_email']
                msg['To'] = self.alert_settings['email']['recipient']
                
                # Add text and HTML parts
                text_part = MimeText(email_content['text_content'], 'plain', 'utf-8')
                html_part = MimeText(email_content['html_content'], 'html', 'utf-8')
                
                msg.attach(text_part)
                msg.attach(html_part)
                
                # Add CSV attachment if requested
                if self.alert_settings['email'].get('include_csv', True):
                    csv_file = self.create_csv_attachment(jobs)
                    if csv_file and os.path.exists(csv_file):
                        with open(csv_file, 'rb') as f:
                            part = MimeBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {os.path.basename(csv_file)}'
                            )
                            msg.attach(part)
                
                # Send email
                with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                    server.starttls()
                    server.login(self.email_config['username'], self.email_config['password'])
                    server.send_message(msg)
                
                # Log successful send
                self.log_email_sent(email_content, len(jobs), True)
                logging.info(f"✅ Email sent successfully to {self.alert_settings['email']['recipient']}")
                return True
                
            except Exception as e:
                logging.error(f"Email send attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    # Final failure - save for manual review
                    self.save_failed_alert(email_content, jobs, str(e))
                    self.log_email_sent(email_content, len(jobs), False, str(e))
                else:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        return False
    
    def log_email_sent(self, email_content: Dict, job_count: int, success: bool, error: str = ""):
        """Log email sending results"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'recipient': self.alert_settings['email']['recipient'],
                'subject': email_content['subject'],
                'job_count': job_count,
                'success': success,
                'error': error,
                'frequency': self.alert_settings.get('frequency', 'unknown')
            }
            
            # Create logs file if it doesn't exist
            file_exists = os.path.exists(self.email_logs_file)
            
            with open(self.email_logs_file, 'a', newline='', encoding='utf-8') as f:
                fieldnames = ['timestamp', 'recipient', 'subject', 'job_count', 'success', 'error', 'frequency']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                writer.writerow(log_entry)
                
        except Exception as e:
            logging.error(f"Failed to log email: {e}")
    
    def save_failed_alert(self, email_content: Dict, jobs: List[Dict], error: str):
        """Save failed alert for manual review"""
        try:
            failed_alert = {
                'timestamp': datetime.now().isoformat(),
                'recipient': self.alert_settings['email']['recipient'],
                'subject': email_content['subject'],
                'job_count': len(jobs),
                'error': error,
                'html_content': email_content['html_content'][:500] + "...",  # Truncated
                'recovery_instructions': "Check SMTP settings and retry with: python modules/module_3_alerts.py --retry-failed"
            }
            
            file_exists = os.path.exists(self.failed_alerts_file)
            
            with open(self.failed_alerts_file, 'a', newline='', encoding='utf-8') as f:
                fieldnames = ['timestamp', 'recipient', 'subject', 'job_count', 'error', 'html_content', 'recovery_instructions']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                writer.writerow(failed_alert)
            
            logging.info(f"Failed alert saved to {self.failed_alerts_file}")
            
        except Exception as e:
            logging.error(f"Failed to save failed alert: {e}")
    
    def update_last_sent_timestamp(self):
        """Update the last sent timestamp"""
        try:
            last_sent_data = {
                'timestamp': datetime.now().isoformat(),
                'frequency': self.alert_settings.get('frequency', 'weekly'),
                'jobs_sent': True
            }
            
            with open(self.last_sent_file, 'w') as f:
                json.dump(last_sent_data, f, indent=2)
                
        except Exception as e:
            logging.error(f"Failed to update last sent timestamp: {e}")
    
    def test_email_configuration(self) -> bool:
        """Test email configuration with a simple test email"""
        try:
            test_content = {
                'subject': '🧪 Blockchain Job Tracker - Test Email',
                'text_content': 'This is a test email from your Blockchain Job Tracker system. If you received this, your email configuration is working correctly!',
                'html_content': '''
                <html><body style="font-family: Arial, sans-serif;">
                <h2 style="color: #4f46e5;">🧪 Test Email Success!</h2>
                <p>This is a test email from your <strong>Blockchain Job Tracker</strong> system.</p>
                <p>If you received this, your email configuration is working correctly!</p>
                <p style="color: #64748b; font-size: 14px;">Generated at: {}</p>
                </body></html>
                '''.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            }
            
            # Send test email without retries for faster testing
            msg = MimeMultipart('alternative')
            msg['Subject'] = test_content['subject']
            msg['From'] = self.email_config['from_email']
            msg['To'] = self.alert_settings['email']['recipient']
            
            text_part = MimeText(test_content['text_content'], 'plain', 'utf-8')
            html_part = MimeText(test_content['html_content'], 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['username'], self.email_config['password'])
                server.send_message(msg)
            
            logging.info("✅ Test email sent successfully!")
            return True
            
        except Exception as e:
            logging.error(f"❌ Test email failed: {e}")
            return False
    
    def send_job_alerts(self, force_send: bool = False) -> bool:
        """Main method to send job alerts based on Module 2 results"""
        try:
            logging.info("Starting enhanced email alert system...")
            
            # Check if we should send (unless forced)
            if not force_send and not self.should_send_alert():
                logging.info("Not time to send alert yet. Use --force to override.")
                return False
            
            # Load and filter jobs from Module 2
            jobs = self.load_scored_jobs()
            if not jobs:
                logging.warning("No scored jobs available for alerts")
                return False
            
            # Apply smart filtering
            filtered_jobs = self.filter_jobs_for_alert(jobs)
            if not filtered_jobs:
                logging.warning(f"No jobs passed filtering criteria (min_score: {self.alert_settings.get('min_score', 7.0)})")
                return False
            
            # Calculate trends
            trends = self.calculate_trends(filtered_jobs) if self.alert_settings['email'].get('include_trends', True) else {}
            
            # Generate beautiful email content
            email_content = self.generate_email_content(filtered_jobs, trends)
            
            # Send email with retries
            success = self.send_email_with_retries(email_content, filtered_jobs)
            
            if success:
                # Update last sent timestamp
                self.update_last_sent_timestamp()
                
                logging.info(f"🎉 Email alert sent successfully!")
                logging.info(f"  Jobs sent: {len(filtered_jobs)}")
                logging.info(f"  Average score: {trends.get('avg_score', 0)}/10")
                logging.info(f"  Recipient: {self.alert_settings['email']['recipient']}")
                
                return True
            else:
                logging.error("Failed to send email alert after all retries")
                return False
                
        except Exception as e:
            logging.error(f"Failed to send job alerts: {e}")
            return False


def main():
    """Main CLI interface for Module 3"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Email Alert System')
    parser.add_argument('--test', action='store_true', help='Test email configuration')
    parser.add_argument('--force', action='store_true', help='Force send alerts (ignore frequency)')
    parser.add_argument('--config', action='store_true', help='Show current alert configuration')
    args = parser.parse_args()
    
    try:
        alerts = EnhancedEmailAlerts()
        
        if args.test:
            print("🧪 Testing email configuration...")
            
            # Test SMTP connection
            if alerts.test_email_configuration():
                print("✅ Email configuration test passed!")
                print(f"✅ Test email sent to: {alerts.alert_settings['email']['recipient']}")
                print("✅ Check your inbox to confirm delivery")
            else:
                print("❌ Email configuration test failed")
                print("💡 Check your SMTP settings in .env file:")
                print("   - SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD")
                return
            
            # Test with sample jobs
            print("\n🧪 Testing alert generation with Module 2 results...")
            jobs = alerts.load_scored_jobs()
            if jobs:
                filtered = alerts.filter_jobs_for_alert(jobs)
                print(f"✅ Found {len(jobs)} total jobs, {len(filtered)} passed filtering")
                print(f"✅ Filter criteria: min_score >= {alerts.alert_settings.get('min_score', 7.0)}")
                
                if filtered:
                    trends = alerts.calculate_trends(filtered)
                    print(f"✅ Average score of filtered jobs: {trends.get('avg_score', 0)}/10")
                    print(f"✅ Ready to send {len(filtered)} high-quality job matches!")
                else:
                    print("⚠️  No jobs passed filtering. Consider lowering min_score in config/alert_settings.json")
            else:
                print("⚠️  No jobs found. Run Module 2 first: python modules/module_2_matcher.py")
        
        elif args.config:
            print("📋 Current Alert Configuration:")
            print(f"  Frequency: {alerts.alert_settings.get('frequency', 'weekly')}")
            print(f"  Min Score: {alerts.alert_settings.get('min_score', 7.0)}")
            print(f"  Max Jobs: {alerts.alert_settings.get('max_jobs', 10)}")
            print(f"  Recipient: {alerts.alert_settings['email']['recipient']}")
            print(f"  Include Trends: {alerts.alert_settings['email'].get('include_trends', True)}")
            print(f"  Include CSV: {alerts.alert_settings['email'].get('include_csv', True)}")
            
        else:
            # Send alerts
            print("📧 Sending enhanced job alerts...")
            success = alerts.send_job_alerts(force_send=args.force)
            
            if success:
                print("🎉 Job alerts sent successfully!")
                print("📧 Check your email for the latest blockchain job matches")
                print("📊 Detailed logs saved to data/email_logs.csv")
            else:
                print("❌ Failed to send job alerts")
                print("🔍 Check data/system_logs.csv for error details")
                print("🛠️  Try: python modules/module_3_alerts.py --test")
        
    except Exception as e:
        logging.error(f"Module 3 execution failed: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
