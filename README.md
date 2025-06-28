# 🚀 Blockchain Job Tracker

An **intelligent job discovery system** that automatically finds, validates, and matches relevant opportunities from **blockchain, climate, and AI accelerators** across Europe and India. The system uses AI-powered matching against your personal Candidate-Market Fit (CMF) profile and delivers curated weekly email alerts.

## 🎯 Project Goal

**Primary Objective:** Automate the discovery and intelligent filtering of high-quality job opportunities from 100+ blockchain, climate tech, and AI accelerators, eliminating manual search time while ensuring no relevant opportunities are missed.

**Target Outcome:** Weekly email alerts containing 5-10 highly relevant, AI-scored job matches with detailed reasoning, sourced from validated accelerators across Europe and India.

### **Core Problem Solved:**
- **Manual Inefficiency:** Searching 100+ accelerator websites is time-consuming
- **Missed Opportunities:** Lesser-known but high-quality accelerators often overlooked  
- **Information Overload:** Need intelligent filtering and relevance scoring
- **Inconsistent Monitoring:** Job opportunities appear and disappear quickly

---

## 🏗️ Project Architecture

```
blockchain_job_tracker/
├── 📁 modules/                 # Core processing pipeline
│   ├── module_0_directory.py       # Accelerator discovery via Google CSE
│   ├── module_0_5_validator.py     # Accelerator validation & health scoring
│   ├── module_1_scraper.py         # Job scraping from validated sources
│   ├── module_2_matcher.py         # AI-powered job matching & scoring
│   ├── module_3_alerts.py          # Configurable email alert system
│   ├── module_4_dashboard.py       # Streamlit control panel
│   └── utils/
│       ├── error_handling.py       # Centralized error management
│       ├── analytics.py            # Performance tracking
│       └── testing_utils.py        # Module testing framework
│
├── 📁 data/                    # Data storage (CSV-based MVP)
│   ├── accelerators_list.csv       # Master accelerator directory (170+ entries)
│   ├── jobs_raw.csv                # Raw scraped job listings
│   ├── jobs_scored.csv             # AI-scored job matches with reasoning
│   ├── analytics_summary.csv       # Performance metrics & trends
│   ├── system_logs.csv             # Error and execution logs
│   └── test_results/               # Module testing outputs
│
├── 📁 config/                  # Configuration management
│   ├── cmf_profile.json           # Your Candidate-Market Fit profile
│   ├── alert_settings.json        # Email preferences & thresholds
│   └── system_config.json         # API keys, module settings
│
├── 📁 ui/                      # User interfaces
│   └── streamlit_app.py            # Interactive dashboard & analytics
│
├── 📁 analysis/                # Debugging & research tools
│   ├── debug_job_scraper.py       # Troubleshoot scraping issues
│   ├── validation_analysis.py     # Accelerator quality assessment
│   └── enhanced_debugger.py       # Comprehensive diagnostic tool
│
├── 📁 tests/                   # Automated testing suite
│   ├── test_modules.py             # Unit tests for all modules
│   ├── integration_tests.py       # End-to-end workflow testing
│   └── test_data/                  # Sample data for testing
│
├── venv/                       # Virtual environment (ignored)
├── .env                        # API keys and secrets (ignored)
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
└── README.md                   # This documentation
```

---

## 🔄 Processing Pipeline

### **Module 0: Accelerator Discovery** 🔍
**Purpose:** Build comprehensive database of blockchain/climate/AI accelerators

**Process:**
1. Execute targeted Google Custom Search queries
2. Extract organization metadata (name, website, focus, location)
3. Identify careers pages and tag by sector focus
4. Deduplicate and normalize data

**Testing Stage:**
```bash
python modules/module_0_directory.py --test
# Expected output: 20+ new accelerators discovered
# Validation: Check focus_tags accuracy, careers_url detection
```

**Success Criteria:**
- ✅ 100+ relevant accelerators identified
- ✅ 90%+ accurate focus tagging (blockchain/climate/AI)
- ✅ Valid careers URLs for 80%+ of entries

---

### **Module 0.5: Accelerator Validation** ✅
**Purpose:** Filter to high-quality, actively hiring accelerators

**Process:**
1. Website health checks (response time, uptime)
2. Careers page validation and job posting detection
3. Activity scoring (1-10 scale) based on multiple factors
4. Priority classification (high/medium/low) for scraping

**Testing Stage:**
```bash
python modules/module_0_5_validator.py --test
# Expected output: 15-25 "active" status accelerators
# Validation: Verify job_count accuracy, activity_score reasonableness
```

**Success Criteria:**
- ✅ 15+ accelerators classified as "active"
- ✅ Job count estimates within 20% accuracy
- ✅ Activity scores correlate with actual hiring activity

---

### **Module 1: Job Scraping** 🕷️
**Purpose:** Extract job listings from validated accelerator sources

**Process:**
1. Smart platform detection (Greenhouse, Lever, Workday)
2. Adaptive CSS selector system with fallbacks
3. Job title validation and blockchain/climate relevance scoring
4. Deduplication and metadata enrichment

**Testing Stage:**
```bash
python modules/module_1_scraper.py --test
# Expected output: 15-30 quality job listings
# Validation: Check job_title relevance, URL validity, platform detection
```

**Success Criteria:**
- ✅ 15+ valid job listings extracted
- ✅ 90%+ job URLs are accessible
- ✅ 70%+ job titles pass relevance validation

---

### **Module 2: AI Job Matching** 🎯
**Purpose:** Score job relevance against CMF profile using AI

**Process:**
1. Load candidate profile and job requirements
2. OpenAI GPT analysis for role-profile alignment
3. Generate detailed scoring (1-10) with reasoning
4. Extract key match factors and confidence levels

**Testing Stage:**
```bash
python modules/module_2_matcher.py --test
# Expected output: Jobs scored with detailed reasoning
# Validation: Score consistency, reasoning quality, processing time
```

**Success Criteria:**
- ✅ All jobs receive valid scores (1-10)
- ✅ Reasoning explanations are substantive (>50 words)
- ✅ Processing time <30 seconds per job

---

### **Module 3: Alert System** 📧
**Purpose:** Deliver curated job matches via configurable email alerts

**Process:**
1. Filter jobs above configured score threshold
2. Template generation with match reasoning
3. Deduplication across time periods
4. Email delivery with tracking and retry logic

**Testing Stage:**
```bash
python modules/module_3_alerts.py --test
# Expected output: Test email sent with sample jobs
# Validation: Email formatting, link validity, delivery confirmation
```

**Success Criteria:**
- ✅ Email successfully delivered to configured address
- ✅ All job links in email are accessible
- ✅ Email formatting renders correctly across clients

---

### **Module 4: Dashboard** 📊
**Purpose:** Interactive analytics and system management interface

**Process:**
1. Real-time system health monitoring
2. Job discovery trends and match analytics
3. Module configuration and manual triggers
4. Performance metrics visualization

**Testing Stage:**
```bash
streamlit run ui/streamlit_app.py --test-mode
# Expected output: Dashboard loads with sample data
# Validation: All charts render, buttons functional, data accurate
```

**Success Criteria:**
- ✅ Dashboard loads without errors
- ✅ All interactive elements functional
- ✅ Charts display accurate data from CSV files

---

## 🌍 Geographic & Sector Focus

### **Target Regions:**
- **Europe:** Berlin, London, Amsterdam, Zurich, Stockholm, Paris
- **India:** Mumbai, Bangalore, Delhi, Hyderabad

### **Sector Priorities:**
1. **Blockchain/Web3:** DeFi, Infrastructure, Smart contracts, Crypto exchanges
2. **Climate Tech:** Carbon markets, Renewable energy, Sustainability platforms
3. **AI/ML:** Applied AI, Machine learning infrastructure, Data platforms

### **Role Types:**
- **Technical:** Engineers, Developers, Architects, Data Scientists
- **Business:** Product Managers, Strategy, Partnerships, Business Development
- **Leadership:** Directors, VPs, Heads of Department

---

## 🛠️ Environment Setup

### Prerequisites
- **Python 3.10** (recommended version)
- **Git** for version control
- **API Keys** for Google Custom Search and OpenAI (required for full functionality)

### 1. Python 3.10 Installation
- **macOS (Homebrew):**
  ```bash
  brew install python@3.10
  python3.10 --version  # Should output: Python 3.10.x
  ```
- **Ubuntu/Debian:**
  ```bash
  sudo apt update
  sudo apt install python3.10 python3.10-venv python3.10-dev
  python3.10 --version
  ```
- **Windows:**
  - Download Python 3.10 from [python.org](https://www.python.org/downloads/release/python-3100/)
  - During installation, check "Add Python to PATH"
  - Verify: `python --version` in Command Prompt

### 2. Project Setup
```bash
git clone <your-repository-url>
cd blockchain_job_tracker
python3.10 -m venv venv
# Activate venv:
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
python --version  # Should show Python 3.10.x
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip list | grep -E "(beautifulsoup4|requests|streamlit|pandas)"
```

### 4. Environment Variables Setup
```bash
cp .env.example .env  # If template exists, else create .env manually
# Edit .env with your API keys and config
```
**Required .env variables:**
- `GOOGLE_API_KEY`, `GOOGLE_CSE_ID` (Google Custom Search)
- `OPENAI_API_KEY` (OpenAI)
- Email config: `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`

### 5. Configuration Setup
```bash
cp config/cmf_profile.example.json config/cmf_profile.json  # If template exists
# Edit config/cmf_profile.json with your details
```

### 6. Verification & Testing
```bash
# Test Python and dependencies
python -c "import requests, pandas, streamlit, bs4; print('✅ All dependencies loaded')"
# Test environment variables
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✅ Google API Key loaded') if os.getenv('GOOGLE_API_KEY') else print('❌ Google API Key missing')"
```

### 7. Initial Test Run
```bash
python modules/module_0_directory.py --test
# Should output: Found 20+ accelerators, data saved to data/accelerators_list.csv
```

---

## 🔄 Resumption Instructions

### **Quick Resume After Break (5 minutes)**

If you're returning to the project after a break, follow these steps to get back up and running:

#### 1. **Activate Environment**
```bash
cd /Users/pranav/coding/blockchain_job_tracker
source blockchain_job_tracker/venv/bin/activate
python --version  # Should show Python 3.10.18
```

#### 2. **Verify Dependencies**
```bash
pip list | grep -E "(openai|httpx|requests|pandas)"
# Should show: openai==1.12.0, httpx==0.24.1, requests==2.32.4, pandas==2.1.4
```

#### 3. **Test Core Modules**
```bash
# Test Module 0 (Accelerator Discovery)
python modules/module_0_directory.py --test

# Test Module 0.5 (Validation)
python modules/module_0_5_validator.py --test

# Test Module 1 (Job Scraping)
python modules/module_1_scraper.py --test

# Test Module 2 (AI Job Matcher)
python modules/module_2_matcher.py --test
```

#### 4. **Check System Status**
```bash
# Verify data files exist
ls -la data/*.csv

# Check recent logs
tail -n 10 data/system_logs.csv

# Verify configuration
cat config/cmf_profile.json | head -5
```

### **Troubleshooting Common Resume Issues**

#### **Issue: Virtual Environment Not Found**
```bash
# Recreate virtual environment with Python 3.10
rm -rf blockchain_job_tracker/venv
python3.10 -m venv blockchain_job_tracker/venv
source blockchain_job_tracker/venv/bin/activate
pip install -r blockchain_job_tracker/requirements.txt
```

#### **Issue: OpenAI Import Error**
```bash
# Fix httpx compatibility issue
pip uninstall httpx -y
pip install httpx==0.24.1
python -c "import openai; client = openai.OpenAI(api_key='test'); print('✅ OpenAI working')"
```

#### **Issue: Module Import Errors**
```bash
# Ensure you're in the correct directory
pwd  # Should show: /Users/pranav/coding/blockchain_job_tracker
python -c "import sys; print(sys.path)"  # Check Python path
```

#### **Issue: API Key Errors**
```bash
# Check .env file
cat .env | grep -E "(OPENAI|GOOGLE)" | head -3

# Test API connectivity
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('OpenAI Key:', '✅' if os.getenv('OPENAI_API_KEY') else '❌')"
```

### **Current Project Status (Last Updated: June 2025)**

#### **✅ Working Modules:**
- **Module 0**: Accelerator discovery via Google CSE
- **Module 0.5**: Accelerator validation and health scoring
- **Module 1**: Job scraping from validated sources
- **Module 2**: AI-powered job matching (OpenAI integration)

#### **🔄 In Development:**
- **Module 3**: Email alert system
- **Module 4**: Streamlit dashboard
- **UI**: Interactive web interface

#### **📊 Data Status:**
- **Accelerators**: 170+ entries in `data/accelerators_list.csv`
- **Active Accelerators**: 15-25 validated and ready for scraping
- **Jobs**: Varies based on active accelerator availability
- **AI Matching**: Fully functional with fallback analysis

#### **🔧 Environment:**
- **Python**: 3.10.18 (virtual environment)
- **Key Dependencies**: 
  - openai==1.12.0
  - httpx==0.24.1 (compatibility fix)
  - pandas==2.1.4
  - requests==2.32.4
- **APIs**: Google CSE, OpenAI (quota-aware)

### **Next Development Steps**

#### **Immediate Priorities:**
1. **Complete Module 3**: Email alert system
2. **Build Module 4**: Streamlit dashboard
3. **Add real job data**: Run Module 1 with active accelerators
4. **Test full pipeline**: End-to-end workflow validation

#### **Testing Strategy:**
```bash
# Run comprehensive test suite
python modules/module_0_directory.py --test
python modules/module_0_5_validator.py --test
python modules/module_1_scraper.py --test
python modules/module_2_matcher.py --test

# Check results
ls -la data/*.csv
cat data/system_logs.csv | tail -20
```

#### **Git Workflow:**
```bash
# Before starting work
git status
git pull origin main

# After making changes
git add .
git commit -m "Description of changes"
git push origin main
```

---

## �� Quick Start Guide

### **Initial Setup:**
```bash
# 1. Clone and navigate to project
cd blockchain_job_tracker

# 2. Set up virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys (Google CSE, OpenAI)

# 5. Configure your profile
# Edit config/cmf_profile.json with your skills and preferences
```

### **Run Complete Pipeline:**
```bash
# Run all modules in sequence
python -m modules.module_0_directory      # Discover accelerators
python -m modules.module_0_5_validator    # Validate and score
python -m modules.module_1_scraper        # Scrape job listings
python -m modules.module_2_matcher        # AI-powered matching
python -m modules.module_3_alerts         # Send email alerts

# Or run with testing validation
python run_pipeline.py --with-tests
```

### **Launch Dashboard:**
```bash
streamlit run ui/streamlit_app.py
# Access at http://localhost:8501
```

---

## 🧹 Development Hygiene Checklist

Before each development session:

1. **Activate Virtual Environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Check Git Status:**
   ```bash
   git status
   git pull origin main
   ```

3. **Review System Health:**
   ```bash
   tail -n 20 data/system_logs.csv
   python -c "import modules.utils.analytics as a; a.system_health_check()"
   ```

4. **Run Module Tests:**
   ```bash
   python -m pytest tests/ -v
   ```

5. **Check Data Freshness:**
   ```bash
   ls -la data/*.csv  # Check last modified dates
   wc -l data/jobs_raw.csv  # Verify job count
   ```

---

## 📊 Success Metrics & KPIs

### **Discovery Quality:**
- **Coverage:** 100+ relevant accelerators in database
- **Accuracy:** 90%+ "active" accelerators actually hiring
- **Freshness:** New accelerators discovered weekly

### **Job Matching Performance:**
- **Volume:** 15-30 relevant jobs found per week
- **Relevance:** 70%+ user satisfaction with top-scored matches
- **Efficiency:** <10 minutes manual review time per week

### **System Reliability:**
- **Uptime:** 95%+ successful weekly pipeline runs
- **Error Rate:** <5% module execution failures
- **Response Time:** Complete pipeline execution <30 minutes

### **User Experience:**
- **Email Delivery:** 98%+ successful alert delivery
- **Match Quality:** Average score >7.0 for delivered jobs
- **Action Rate:** 20%+ of delivered jobs result in applications

---

## 🔧 Configuration Management

### **Candidate Profile (config/cmf_profile.json):**
```json
{
  "skills": ["blockchain", "web3", "defi", "smart contracts"],
  "roles": ["senior engineer", "lead developer", "architect"],
  "experience_level": "senior",
  "location_preferences": ["remote", "berlin", "mumbai"],
  "salary_range": {"min": 80000, "currency": "EUR"},
  "deal_breakers": ["junior", "unpaid", "equity-only"],
  "nice_to_haves": ["startup", "early-stage", "crypto-native"]
}
```

### **Alert Settings (config/alert_settings.json):**
```json
{
  "frequency": "weekly",
  "min_score": 7.0,
  "max_jobs_per_alert": 10,
  "email": "your.email@example.com",
  "sectors": ["blockchain", "climate"],
  "include_trends": true
}
```

---

## 🔍 Debugging & Troubleshooting

### **Common Issues:**

**Issue: Module 1 finds 0 jobs**
```bash
python analysis/debug_job_scraper.py
# This will diagnose CSS selector and scraping issues
```

**Issue: AI matching fails**
```bash
python modules/module_2_matcher.py --debug
# Check OpenAI API connectivity and quota
```

**Issue: Email alerts not sending**
```bash
python modules/module_3_alerts.py --test-email
# Verify SMTP configuration and credentials
```

### **Performance Monitoring:**
```bash
# View system analytics
python -c "
import pandas as pd
df = pd.read_csv('data/analytics_summary.csv')
print(df.tail(10))
"

# Check module execution times
grep "execution time" data/system_logs.csv | tail -5
```

---

## 🚀 Future Enhancements

### **Phase 2 Improvements:**
1. **Database Migration:** SQLite/PostgreSQL for better data management
2. **Real-time Monitoring:** Slack/Telegram integration for instant alerts  
3. **ML Improvements:** Custom matching models trained on feedback
4. **API Development:** RESTful API for external integrations
5. **Mobile App:** React Native companion for job alerts

### **Advanced Features:**
1. **Company Tracking:** Monitor specific organizations for new openings
2. **Network Analysis:** LinkedIn integration for referral opportunities
3. **Salary Intelligence:** Market rate analysis and negotiation insights
4. **Application Tracking:** CRM-style application management
5. **Interview Prep:** AI-powered interview question generation

### **Scalability Considerations:**
1. **Multi-user Support:** User accounts and personalized profiles
2. **Cloud Deployment:** AWS/Google Cloud hosting with auto-scaling
3. **Performance Optimization:** Redis caching and parallel processing
4. **Data Pipeline:** Apache Airflow for production scheduling

---

## 📝 Contributing

### **Development Workflow:**
1. Create feature branch: `git checkout -b feature/new-module`
2. Implement changes with tests: `python -m pytest tests/`
3. Update documentation: Include testing stages and success criteria
4. Submit pull request with performance metrics

### **Code Standards:**
- **Testing:** All modules must include testing stages and success criteria
- **Logging:** Use structured logging for debugging and analytics
- **Error Handling:** Implement retry logic and graceful degradation
- **Documentation:** Update README and inline comments for new features

---

## 📄 License

This project is developed for personal use in job discovery automation. See LICENSE file for details.

---

**Last Updated:** June 2025 | **Version:** 1.0.0 | **Status:** Active Development