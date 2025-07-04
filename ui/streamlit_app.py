import os
import pandas as pd
import json
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import subprocess
import sys

def ensure_file(path, headers=None, is_json=False):
    """Ensure a file exists with the correct schema."""
    if not os.path.exists(path):
        if is_json:
            with open(path, 'w') as f:
                json.dump({}, f, indent=2)
        elif headers:
            pd.DataFrame(columns=headers).to_csv(path, index=False)
        else:
            with open(path, 'w') as f:
                f.write('')

# Define required files and their schemas
REQUIRED_FILES = [
    ("data/accelerators_list.csv", ["Name", "Website", "Focus_Tags", "Country", "Status", "Careers_URL", "Discovery_Date"], False),
    ("data/jobs_raw.csv", ["title", "company", "location", "source_accelerator", "job_url", "date_posted"], False),
    ("data/jobs_scored.csv", ["title", "company", "location", "accelerator_name", "job_url", "ai_score", "confidence", "ai_reasoning", "match_date", "recommendation"], False),
    ("data/system_logs.csv", ["timestamp", "level", "module", "message"], False),
    ("data/email_logs.csv", ["timestamp", "recipient", "job_count", "success"], False),
    ("config/cmf_profile.json", None, True),
    ("config/alert_settings.json", None, True),
]

for path, headers, is_json in REQUIRED_FILES:
    ensure_file(path, headers, is_json)

# --- Enhanced Data Loading Utilities ---
def load_csv_safe(path, required_columns=None):
    try:
        if os.path.exists(path):
            df = pd.read_csv(path)
            if required_columns:
                for col in required_columns:
                    if col not in df.columns:
                        st.warning(f"Column '{col}' missing in {path}. Some features may not work.")
            return df
        else:
            st.info(f"File not found: {path}")
            return pd.DataFrame(columns=required_columns or [])
    except Exception as e:
        st.error(f"Error loading {path}: {e}")
        return pd.DataFrame(columns=required_columns or [])

def load_json_safe(path):
    try:
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        else:
            st.info(f"File not found: {path}")
            return {}
    except Exception as e:
        st.error(f"Error loading {path}: {e}")
        return {}

# --- System Health Check Utility ---
def get_system_status():
    status = {
        'files': {},
        'modules': {},
        'env': {},
        'overall_health': 'unknown'
    }
    # File health
    for path, headers, is_json in REQUIRED_FILES:
        if os.path.exists(path):
            try:
                if path.endswith('.csv'):
                    df = pd.read_csv(path)
                    status['files'][path] = {
                        'status': 'healthy',
                        'rows': len(df),
                        'last_modified': os.path.getmtime(path)
                    }
                else:
                    status['files'][path] = {
                        'status': 'healthy',
                        'last_modified': os.path.getmtime(path)
                    }
            except Exception:
                status['files'][path] = {'status': 'error', 'rows': 0}
        else:
            status['files'][path] = {'status': 'missing', 'rows': 0}
    # Module status (simple: based on file health)
    status['modules'] = {
        'Module 0 (Directory)': 'active' if status['files']['data/accelerators_list.csv']['status'] == 'healthy' else 'inactive',
        'Module 1 (Scraper)': 'active' if status['files']['data/jobs_raw.csv']['status'] == 'healthy' else 'inactive',
        'Module 2 (Matcher)': 'active' if status['files']['data/jobs_scored.csv']['status'] == 'healthy' else 'inactive',
        'Module 3 (Alerts)': 'active' if status['files']['data/email_logs.csv']['status'] == 'healthy' else 'inactive',
    }
    # Env vars
    for var in ['GOOGLE_API_KEY', 'OPENAI_API_KEY']:
        status['env'][var] = 'set' if os.getenv(var) else 'missing'
    # Overall health
    healthy_modules = sum(1 for s in status['modules'].values() if s == 'active')
    if healthy_modules >= 3:
        status['overall_health'] = 'healthy'
    elif healthy_modules >= 2:
        status['overall_health'] = 'warning'
    else:
        status['overall_health'] = 'error'
    return status

# --- Module Execution Utilities ---
def run_module(module_name, test_mode=False):
    """Execute a module and return the result"""
    try:
        if test_mode:
            cmd = [sys.executable, f"modules/{module_name}.py", "--test"]
        else:
            cmd = [sys.executable, f"modules/{module_name}.py"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Module execution timed out (5 minutes)',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }

# --- Sidebar Navigation and Modular UI Structure ---
SECTIONS = [
    ("📊 Dashboard", "dashboard"),
    ("🏢 Accelerator Management", "accelerator_management"),
    ("🔍 Job Discovery", "job_discovery"),
    ("⚡ Matching Engine", "matching_engine"),
    ("📧 Alert Settings", "alert_settings"),
    ("📈 Analytics", "analytics"),
    ("⚙️ System Settings", "system_settings"),
    ("📁 Data Management", "data_management"),
    ("❓ Help/About", "help_about"),
]

st.sidebar.title("🚀 Blockchain Job Tracker")
page = st.sidebar.selectbox("Navigation", [s[0] for s in SECTIONS])

# Add system status indicator to sidebar
status = get_system_status()
if status['overall_health'] == 'healthy':
    st.sidebar.success("🟢 System Healthy")
elif status['overall_health'] == 'warning':
    st.sidebar.warning("🟡 Issues Detected")
else:
    st.sidebar.error("🔴 System Issues")

# --- Dashboard Section ---
def show_dashboard():
    st.title("📊 System Dashboard")
    status = get_system_status()
    
    # System health summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if status['overall_health'] == 'healthy':
            st.metric("System Health", "🟢 Healthy")
        elif status['overall_health'] == 'warning':
            st.metric("System Health", "🟡 Warning") 
        else:
            st.metric("System Health", "🔴 Error")
    
    with col2:
        active_modules = sum(1 for s in status['modules'].values() if s == 'active')
        st.metric("Active Modules", f"{active_modules}/4")
    
    with col3:
        total_files = len([f for f in status['files'].values() if f['status'] == 'healthy'])
        st.metric("Data Files", f"{total_files}/{len(REQUIRED_FILES)}")
    
    with col4:
        env_vars = sum(1 for s in status['env'].values() if s == 'set')
        st.metric("API Keys", f"{env_vars}/2")

    # Quick stats
    st.subheader("📈 Quick Stats")
    col1, col2, col3 = st.columns(3)
    
    accelerators_df = load_csv_safe("data/accelerators_list.csv")
    jobs_raw_df = load_csv_safe("data/jobs_raw.csv")
    jobs_scored_df = load_csv_safe("data/jobs_scored.csv")
    
    with col1:
        st.metric("Total Accelerators", len(accelerators_df))
        if not accelerators_df.empty and 'Status' in accelerators_df.columns:
            active_accs = len(accelerators_df[accelerators_df['Status'] == 'active'])
            st.caption(f"{active_accs} active")
    
    with col2:
        st.metric("Raw Jobs", len(jobs_raw_df))
        if not jobs_raw_df.empty:
            st.caption("From job scraping")
    
    with col3:
        st.metric("Scored Jobs", len(jobs_scored_df))
        if not jobs_scored_df.empty and 'ai_score' in jobs_scored_df.columns:
            avg_score = jobs_scored_df['ai_score'].mean()
            st.caption(f"Avg score: {avg_score:.1f}/10")

    # Module status detail
    st.subheader("🔧 Module Status")
    for module, state in status['modules'].items():
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            if state == 'active':
                st.markdown(f"✅ **{module}**")
            else:
                st.markdown(f"❌ **{module}**")
        with col2:
            st.caption(state.title())
        with col3:
            if state == 'active':
                st.caption("Ready")
            else:
                st.caption("Inactive")

    # Recent activity
    st.subheader("📝 Recent Activity")
    logs_df = load_csv_safe("data/system_logs.csv")
    if not logs_df.empty:
        recent_logs = logs_df.tail(5)
        for _, log in recent_logs.iterrows():
            timestamp = log.get('timestamp', 'Unknown time')
            module = log.get('module', 'Unknown')
            message = log.get('message', 'No message')
            st.caption(f"**{timestamp}** - {module}: {message[:100]}...")
    else:
        st.info("No recent activity logged")

def show_accelerator_management():
    st.title("🏢 Accelerator Management")
    
    # Load accelerator data
    df = load_csv_safe("data/accelerators_list.csv")
    
    if df.empty:
        st.warning("No accelerator data found. Run Module 0 to discover accelerators.")
        if st.button("🔍 Run Module 0 (Discovery)"):
            with st.spinner("Running accelerator discovery..."):
                result = run_module("module_0_directory", test_mode=True)
                if result['success']:
                    st.success("✅ Discovery completed!")
                    st.rerun()
                else:
                    st.error(f"❌ Discovery failed: {result['stderr']}")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Accelerators", len(df))
    
    with col2:
        if 'Status' in df.columns:
            active_count = len(df[df['Status'] == 'active'])
            st.metric("Active", active_count)
        else:
            st.metric("Active", "N/A")
    
    with col3:
        if 'Country' in df.columns:
            country_count = df['Country'].nunique()
            st.metric("Countries", country_count)
        else:
            st.metric("Countries", "N/A")
    
    with col4:
        if 'Focus_Tags' in df.columns:
            blockchain_count = len(df[df['Focus_Tags'].str.contains('blockchain', case=False, na=False)])
            st.metric("Blockchain Focus", blockchain_count)
        else:
            st.metric("Blockchain Focus", "N/A")

    # Filters
    st.subheader("🔍 Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'Status' in df.columns:
            status_options = ['All'] + list(df['Status'].unique())
            selected_status = st.selectbox("Status", status_options)
        else:
            selected_status = 'All'
    
    with col2:
        if 'Country' in df.columns:
            country_options = ['All'] + sorted(df['Country'].unique())
            selected_country = st.selectbox("Country", country_options)
        else:
            selected_country = 'All'
    
    with col3:
        if 'Focus_Tags' in df.columns:
            focus_filter = st.text_input("Focus Contains", placeholder="e.g., blockchain, climate")
        else:
            focus_filter = ""

    # Apply filters
    filtered_df = df.copy()
    
    if selected_status != 'All' and 'Status' in df.columns:
        filtered_df = filtered_df[filtered_df['Status'] == selected_status]
    
    if selected_country != 'All' and 'Country' in df.columns:
        filtered_df = filtered_df[filtered_df['Country'] == selected_country]
    
    if focus_filter and 'Focus_Tags' in df.columns:
        filtered_df = filtered_df[filtered_df['Focus_Tags'].str.contains(focus_filter, case=False, na=False)]

    st.subheader(f"📋 Accelerators ({len(filtered_df)} shown)")
    
    # Display options
    col1, col2 = st.columns([1, 3])
    with col1:
        show_all_columns = st.checkbox("Show all columns", value=False)
    with col2:
        search_term = st.text_input("🔍 Search names", placeholder="Search accelerator names...")

    # Apply search
    if search_term and 'Name' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Name'].str.contains(search_term, case=False, na=False)]

    # Select columns to display
    if show_all_columns:
        display_columns = filtered_df.columns.tolist()
    else:
        essential_columns = ['Name', 'Website', 'Country', 'Focus_Tags', 'Status']
        display_columns = [col for col in essential_columns if col in filtered_df.columns]

    # Display the data table
    if not filtered_df.empty:
        st.dataframe(
            filtered_df[display_columns],
            use_container_width=True,
            hide_index=True
        )
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 View Analytics"):
                st.session_state.show_accelerator_analytics = True
        
        with col2:
            csv_data = filtered_df.to_csv(index=False)
            st.download_button(
                "📥 Download CSV",
                csv_data,
                file_name=f"accelerators_filtered_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col3:
            if st.button("🔄 Refresh Data"):
                st.rerun()

        # Show analytics if requested
        if st.session_state.get('show_accelerator_analytics', False):
            st.subheader("📊 Accelerator Analytics")
            
            # Status distribution
            if 'Status' in filtered_df.columns:
                col1, col2 = st.columns(2)
                
                with col1:
                    status_counts = filtered_df['Status'].value_counts()
                    fig = px.pie(values=status_counts.values, names=status_counts.index, 
                               title="Status Distribution")
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    if 'Country' in filtered_df.columns:
                        country_counts = filtered_df['Country'].value_counts().head(10)
                        fig = px.bar(x=country_counts.values, y=country_counts.index, 
                                   orientation='h', title="Top 10 Countries")
                        st.plotly_chart(fig, use_container_width=True)
            
            if st.button("❌ Close Analytics"):
                st.session_state.show_accelerator_analytics = False
                st.rerun()
    else:
        st.info("No accelerators match your filters.")

def show_job_discovery():
    st.title("🔍 Job Discovery")
    
    # Load job data
    df = load_csv_safe("data/jobs_raw.csv")
    
    if df.empty:
        st.warning("No raw job data found. Run Module 1 to scrape jobs.")
        if st.button("🕷️ Run Module 1 (Scraper)"):
            with st.spinner("Running job scraper..."):
                result = run_module("module_1_scraper", test_mode=True)
                if result['success']:
                    st.success("✅ Job scraping completed!")
                    st.rerun()
                else:
                    st.error(f"❌ Scraping failed: {result['stderr']}")
        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Jobs", len(df))
    
    with col2:
        if 'accelerator_name' in df.columns:
            company_count = df['accelerator_name'].nunique()
            st.metric("Companies", company_count)
        elif 'company' in df.columns:
            company_count = df['company'].nunique()
            st.metric("Companies", company_count)
        else:
            st.metric("Companies", "N/A")
    
    with col3:
        if 'location' in df.columns:
            remote_count = len(df[df['location'].str.contains('remote', case=False, na=False)])
            st.metric("Remote Jobs", remote_count)
        else:
            st.metric("Remote Jobs", "N/A")
    
    with col4:
        if 'discovered_date' in df.columns:
            recent_count = len(df[pd.to_datetime(df['discovered_date'], errors='coerce') >= datetime.now() - timedelta(days=7)])
            st.metric("This Week", recent_count)
        else:
            st.metric("This Week", "N/A")

    # Filters
    st.subheader("🔍 Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'location' in df.columns:
            location_options = ['All'] + sorted(df['location'].dropna().unique())
            selected_location = st.selectbox("Location", location_options[:20])  # Limit options
        else:
            selected_location = 'All'
    
    with col2:
        company_col = 'accelerator_name' if 'accelerator_name' in df.columns else 'company'
        if company_col in df.columns:
            company_options = ['All'] + sorted(df[company_col].dropna().unique())
            selected_company = st.selectbox("Company", company_options[:20])  # Limit options
        else:
            selected_company = 'All'
    
    with col3:
        if 'platform' in df.columns:
            platform_options = ['All'] + list(df['platform'].dropna().unique())
            selected_platform = st.selectbox("Platform", platform_options)
        else:
            selected_platform = 'All'

    # Apply filters
    filtered_df = df.copy()
    
    if selected_location != 'All' and 'location' in df.columns:
        filtered_df = filtered_df[filtered_df['location'] == selected_location]
    
    if selected_company != 'All':
        if company_col in df.columns:
            filtered_df = filtered_df[filtered_df[company_col] == selected_company]
    
    if selected_platform != 'All' and 'platform' in df.columns:
        filtered_df = filtered_df[filtered_df['platform'] == selected_platform]

    # Search
    search_term = st.text_input("🔍 Search job titles", placeholder="Search job titles...")
    if search_term and 'title' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['title'].str.contains(search_term, case=False, na=False)]

    st.subheader(f"📋 Raw Jobs ({len(filtered_df)} shown)")
    
    # Display jobs
    if not filtered_df.empty:
        # Select essential columns
        display_columns = ['title']
        if 'accelerator_name' in filtered_df.columns:
            display_columns.append('accelerator_name')
        elif 'company' in filtered_df.columns:
            display_columns.append('company')
        
        for col in ['location', 'platform', 'discovered_date']:
            if col in filtered_df.columns:
                display_columns.append(col)

        st.dataframe(
            filtered_df[display_columns],
            use_container_width=True,
            hide_index=True
        )
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("⚡ Run AI Matching"):
                with st.spinner("Running AI job matching..."):
                    result = run_module("module_2_matcher", test_mode=True)
                    if result['success']:
                        st.success("✅ AI matching completed!")
                        st.info("Check the Matching Engine section for results.")
                    else:
                        st.error(f"❌ Matching failed: {result['stderr']}")
        
        with col2:
            csv_data = filtered_df.to_csv(index=False)
            st.download_button(
                "📥 Download CSV",
                csv_data,
                file_name=f"jobs_raw_filtered_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col3:
            if st.button("🔄 Refresh Data"):
                st.rerun()

        # Job details view
        if len(filtered_df) > 0:
            st.subheader("📄 Job Details")
            selected_job_idx = st.selectbox(
                "Select a job to view details:",
                range(len(filtered_df)),
                format_func=lambda x: filtered_df.iloc[x]['title']
            )
            
            if selected_job_idx is not None:
                job = filtered_df.iloc[selected_job_idx]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Title:**", job.get('title', 'N/A'))
                    st.write("**Company:**", job.get('accelerator_name', job.get('company', 'N/A')))
                    st.write("**Location:**", job.get('location', 'N/A'))
                    st.write("**Platform:**", job.get('platform', 'N/A'))
                
                with col2:
                    st.write("**Job URL:**")
                    if job.get('job_url'):
                        st.markdown(f"[Open Job Posting]({job['job_url']})")
                    else:
                        st.write("N/A")
                    
                    st.write("**Discovered:**", job.get('discovered_date', 'N/A'))
                
                if job.get('snippet'):
                    st.write("**Description:**")
                    st.write(job['snippet'])
    else:
        st.info("No jobs match your filters.")

def show_matching_engine():
    st.title("⚡ Matching Engine")
    
    # Load scored job data
    df = load_csv_safe("data/jobs_scored.csv")
    
    if df.empty:
        st.warning("No scored job data found. Run Module 2 to score jobs.")
        if st.button("🤖 Run Module 2 (AI Matcher)"):
            with st.spinner("Running AI job matching..."):
                result = run_module("module_2_matcher", test_mode=True)
                if result['success']:
                    st.success("✅ AI matching completed!")
                    st.rerun()
                else:
                    st.error(f"❌ Matching failed: {result['stderr']}")
        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Scored", len(df))
    
    with col2:
        if 'ai_score' in df.columns:
            high_matches = len(df[df['ai_score'] >= 7.0])
            st.metric("High Matches (7+)", high_matches)
        else:
            st.metric("High Matches (7+)", "N/A")
    
    with col3:
        if 'ai_score' in df.columns:
            avg_score = df['ai_score'].mean()
            st.metric("Avg Score", f"{avg_score:.1f}/10")
        else:
            st.metric("Avg Score", "N/A")
    
    with col4:
        if 'recommendation' in df.columns:
            strong_recs = len(df[df['recommendation'] == 'Strong'])
            st.metric("Strong Recs", strong_recs)
        else:
            st.metric("Strong Recs", "N/A")

    # Score distribution chart
    if 'ai_score' in df.columns:
        st.subheader("📊 Score Distribution")
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.histogram(df, x="ai_score", nbins=20, 
                             title="AI Score Distribution",
                             labels={"ai_score": "AI Score", "count": "Number of Jobs"})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Score breakdown
            score_ranges = [
                (9, 10, "Excellent (9-10)"),
                (7, 8.99, "Good (7-8)"),
                (5, 6.99, "Moderate (5-6)"),
                (1, 4.99, "Poor (1-4)")
            ]
            
            breakdown_data = []
            for min_score, max_score, label in score_ranges:
                count = len(df[(df['ai_score'] >= min_score) & (df['ai_score'] <= max_score)])
                breakdown_data.append({"Range": label, "Count": count})
            
            breakdown_df = pd.DataFrame(breakdown_data)
            fig = px.bar(breakdown_df, x="Range", y="Count", 
                        title="Score Range Breakdown")
            st.plotly_chart(fig, use_container_width=True)

    # Filters
    st.subheader("🔍 Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'ai_score' in df.columns:
            min_score = st.slider("Min Score", 0.0, 10.0, 0.0, 0.5)
        else:
            min_score = 0.0
    
    with col2:
        if 'recommendation' in df.columns:
            rec_options = ['All'] + list(df['recommendation'].unique())
            selected_rec = st.selectbox("Recommendation", rec_options)
        else:
            selected_rec = 'All'
    
    with col3:
        if 'accelerator_name' in df.columns:
            company_options = ['All'] + sorted(df['accelerator_name'].dropna().unique())
            selected_company = st.selectbox("Company", company_options[:20])
        else:
            selected_company = 'All'

    # Apply filters
    filtered_df = df.copy()
    
    if 'ai_score' in df.columns:
        filtered_df = filtered_df[filtered_df['ai_score'] >= min_score]
    
    if selected_rec != 'All' and 'recommendation' in df.columns:
        filtered_df = filtered_df[filtered_df['recommendation'] == selected_rec]
    
    if selected_company != 'All' and 'accelerator_name' in df.columns:
        filtered_df = filtered_df[filtered_df['accelerator_name'] == selected_company]

    # Search
    search_term = st.text_input("🔍 Search job titles", placeholder="Search job titles...")
    if search_term and 'title' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['title'].str.contains(search_term, case=False, na=False)]

    st.subheader(f"📋 Scored Jobs ({len(filtered_df)} shown)")
    
    # Sort options
    col1, col2 = st.columns([1, 3])
    with col1:
        if 'ai_score' in filtered_df.columns:
            sort_by = st.selectbox("Sort by", ["Score (High-Low)", "Score (Low-High)", "Title", "Company"])
        else:
            sort_by = "Title"
    
    with col2:
        show_ai_reasoning = st.checkbox("Show AI Reasoning", value=False)

    # Sort data
    if sort_by == "Score (High-Low)" and 'ai_score' in filtered_df.columns:
        filtered_df = filtered_df.sort_values('ai_score', ascending=False)
    elif sort_by == "Score (Low-High)" and 'ai_score' in filtered_df.columns:
        filtered_df = filtered_df.sort_values('ai_score', ascending=True)
    elif sort_by == "Title" and 'title' in filtered_df.columns:
        filtered_df = filtered_df.sort_values('title')
    elif sort_by == "Company" and 'accelerator_name' in filtered_df.columns:
        filtered_df = filtered_df.sort_values('accelerator_name')

    # Display jobs
    if not filtered_df.empty:
        # Select display columns
        display_columns = ['title']
        if 'accelerator_name' in filtered_df.columns:
            display_columns.append('accelerator_name')
        if 'ai_score' in filtered_df.columns:
            display_columns.append('ai_score')
        if 'recommendation' in filtered_df.columns:
            display_columns.append('recommendation')
        for col in ['location', 'match_date']:
            if col in filtered_df.columns:
                display_columns.append(col)

        st.dataframe(
            filtered_df[display_columns],
            use_container_width=True,
            hide_index=True
        )
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📧 Send Alerts"):
                with st.spinner("Sending email alerts..."):
                    result = run_module("module_3_alerts", test_mode=True)
                    if result['success']:
                        st.success("✅ Alerts sent!")
                    else:
                        st.error(f"❌ Alerts failed: {result['stderr']}")
        
        with col2:
            csv_data = filtered_df.to_csv(index=False)
            st.download_button(
                "📥 Download CSV",
                csv_data,
                file_name=f"jobs_scored_filtered_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col3:
            if st.button("🔄 Refresh Data"):
                st.rerun()

        # Detailed job view
        if len(filtered_df) > 0:
            st.subheader("📄 Job Analysis")
            selected_job_idx = st.selectbox(
                "Select a job for detailed analysis:",
                range(len(filtered_df)),
                format_func=lambda x: f"{filtered_df.iloc[x]['title']} (Score: {filtered_df.iloc[x].get('ai_score', 'N/A')})"
            )
            
            if selected_job_idx is not None:
                job = filtered_df.iloc[selected_job_idx]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Title:**", job.get('title', 'N/A'))
                    st.write("**Company:**", job.get('accelerator_name', 'N/A'))
                    st.write("**Location:**", job.get('location', 'N/A'))
                    
                    if 'ai_score' in job:
                        score = job['ai_score']
                        if score >= 8:
                            st.success(f"**AI Score:** {score}/10 (Excellent Match)")
                        elif score >= 6:
                            st.info(f"**AI Score:** {score}/10 (Good Match)")
                        else:
                            st.warning(f"**AI Score:** {score}/10 (Moderate Match)")
                    
                    if 'recommendation' in job:
                        rec = job['recommendation']
                        if rec == 'Strong':
                            st.success(f"**Recommendation:** {rec}")
                        elif rec == 'Good':
                            st.info(f"**Recommendation:** {rec}")
                        else:
                            st.warning(f"**Recommendation:** {rec}")
                
                with col2:
                    st.write("**Job URL:**")
                    if job.get('job_url'):
                        st.markdown(f"[Open Job Posting]({job['job_url']})")
                    else:
                        st.write("N/A")
                    
                    st.write("**Match Date:**", job.get('match_date', 'N/A'))
                    st.write("**Confidence:**", job.get('confidence', 'N/A'))
                
                # AI Reasoning
                if show_ai_reasoning and job.get('ai_reasoning'):
                    st.subheader("🤖 AI Reasoning")
                    st.write(job['ai_reasoning'])
                elif show_ai_reasoning:
                    st.info("No AI reasoning available for this job.")
    else:
        st.info("No jobs match your filters.")

def show_alert_settings():
    st.title("📧 Alert Settings")
    alert_settings = load_json_safe("config/alert_settings.json")
    cmf_profile = load_json_safe("config/cmf_profile.json")
    st.subheader("Edit Alert Settings")
    with st.form("alert_settings_form"):
        frequency = st.selectbox("Email Frequency", ["daily", "weekly", "bi-weekly", "monthly", "on-demand"],
                                 index=["daily", "weekly", "bi-weekly", "monthly", "on-demand"].index(alert_settings.get('frequency', 'weekly')) if alert_settings.get('frequency') else 1)
        min_score = st.slider("Minimum Match Score", 0.0, 10.0, float(alert_settings.get('min_score', 7.0)), 0.1)
        max_jobs = st.number_input("Maximum Jobs per Email", 1, 50, int(alert_settings.get('max_jobs_per_alert', 10)))
        email = st.text_input("Recipient Email", alert_settings.get('email', ''))
        submitted = st.form_submit_button("Save Alert Settings")
        if submitted:
            alert_settings.update({
                'frequency': frequency,
                'min_score': min_score,
                'max_jobs_per_alert': max_jobs,
                'email': email
            })
            try:
                with open("config/alert_settings.json", "w") as f:
                    json.dump(alert_settings, f, indent=2)
                st.success("✅ Alert settings saved!")
            except Exception as e:
                st.error(f"Error saving alert settings: {e}")
    st.subheader("Edit CMF Profile (JSON)")
    cmf_json = st.text_area("CMF Profile JSON", json.dumps(cmf_profile, indent=2), height=200)
    if st.button("Save CMF Profile"):
        try:
            parsed = json.loads(cmf_json)
            with open("config/cmf_profile.json", "w") as f:
                json.dump(parsed, f, indent=2)
            st.success("✅ CMF profile saved!")
        except Exception as e:
            st.error(f"Error saving CMF profile: {e}")

def show_analytics():
    st.title("📈 Analytics")
    jobs_scored = load_csv_safe("data/jobs_scored.csv", ["ai_score", "match_date"])
    accelerators = load_csv_safe("data/accelerators_list.csv", ["Name", "Country"])
    st.subheader("Key Metrics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Jobs Scored", len(jobs_scored))
        st.metric("Total Accelerators", len(accelerators))
    with col2:
        if not jobs_scored.empty and "ai_score" in jobs_scored.columns:
            st.metric("Avg Match Score", f"{jobs_scored['ai_score'].mean():.2f}")
        else:
            st.metric("Avg Match Score", "N/A")
    st.subheader("Match Score Distribution")
    if not jobs_scored.empty and "ai_score" in jobs_scored.columns:
        fig = px.histogram(jobs_scored, x="ai_score", nbins=20, title="Job Match Score Distribution")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No scored jobs available for analytics.")

def show_system_settings():
    st.title("⚙️ System Settings")
    st.subheader("Danger Zone")
    if st.button("🧹 Clean Old Logs"):
        if st.confirm("Are you sure you want to clean old logs? This cannot be undone."):
            try:
                log_file = "data/system_logs.csv"
                if os.path.exists(log_file):
                    df = pd.read_csv(log_file)
                    if len(df) > 1000:
                        df.tail(1000).to_csv(log_file, index=False)
                        st.success("✅ Cleaned log file. Kept last 1000 entries.")
                    else:
                        st.info("Log file is already small enough.")
            except Exception as e:
                st.error(f"❌ Error cleaning logs: {e}")
    if st.button("💾 Backup Data"):
        if st.confirm("Create a backup of all data/config files?"):
            try:
                import shutil
                from datetime import datetime
                backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.makedirs(backup_dir, exist_ok=True)
                for path, _, _ in REQUIRED_FILES:
                    if os.path.exists(path):
                        shutil.copy2(path, f"{backup_dir}/{os.path.basename(path)}")
                st.success(f"✅ Backup created: {backup_dir}")
            except Exception as e:
                st.error(f"❌ Backup failed: {e}")
    if st.button("🔄 Reset System"):
        if st.confirm("⚠️ This will delete all data files! Are you sure?"):
            st.error("Reset functionality disabled for safety.")

def show_data_management():
    st.title("📁 Data Management")
    st.subheader("Import/Export")
    uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
    if uploaded_file:
        st.write("Preview:")
        df_preview = pd.read_csv(uploaded_file)
        st.dataframe(df_preview.head())
        target_file = st.selectbox("Replace which file?", [f[0] for f in REQUIRED_FILES if f[0].endswith('.csv')])
        if st.button("Import & Replace"):
            if st.confirm(f"Are you sure you want to overwrite {target_file}?"):
                try:
                    df_preview.to_csv(target_file, index=False)
                    st.success(f"✅ Successfully imported to {target_file}")
                except Exception as e:
                    st.error(f"❌ Import failed: {e}")

    st.subheader("File Management (data/)")
    data_dir = "data/"
    now = datetime.now()
    # List files, excluding hidden and critical files
    def is_protected(fname):
        fname_lower = fname.lower()
        return (
            fname.startswith('.') or
            'template' in fname_lower or
            'config' in fname_lower or
            'profile' in fname_lower
        )
    files = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f)) and not is_protected(f)]
    if not files:
        st.info("No user data files found in data/ directory.")
        return
    file_info = []
    for f in files:
        path = os.path.join(data_dir, f)
        stat = os.stat(path)
        mtime = datetime.fromtimestamp(stat.st_mtime)
        age_days = (now - mtime).days
        file_info.append({
            'name': f,
            'size': stat.st_size,
            'mtime': mtime,
            'age_days': age_days,
            'path': path
        })
    df_files = pd.DataFrame(file_info)
    st.dataframe(df_files[['name', 'size', 'mtime', 'age_days']].sort_values('mtime', ascending=False), use_container_width=True)

    st.markdown("**Select files to delete:**")
    selected_files = st.multiselect("Files", df_files['name'].tolist())
    if st.button("Delete Selected Files"):
        if selected_files and st.confirm(f"Are you sure you want to delete {len(selected_files)} file(s)? This cannot be undone."):
            deleted = []
            for fname in selected_files:
                try:
                    os.remove(os.path.join(data_dir, fname))
                    deleted.append(fname)
                except Exception as e:
                    st.error(f"❌ Failed to delete {fname}: {e}")
            if deleted:
                st.success(f"✅ Deleted: {', '.join(deleted)}")

    # Bulk delete files older than 30 days
    old_files = df_files[df_files['age_days'] > 30]['name'].tolist()
    if old_files:
        if st.button(f"Delete All Files Older Than 30 Days ({len(old_files)})"):
            if st.confirm(f"Are you sure you want to delete {len(old_files)} file(s) older than 30 days? This cannot be undone."):
                deleted = []
                for fname in old_files:
                    try:
                        os.remove(os.path.join(data_dir, fname))
                        deleted.append(fname)
                    except Exception as e:
                        st.error(f"❌ Failed to delete {fname}: {e}")
                if deleted:
                    st.success(f"✅ Deleted old files: {', '.join(deleted)}")
    else:
        st.info("No files older than 30 days.")

def show_help_about():
    st.title("❓ Help & About")
    st.markdown("""
    ## Blockchain Job Tracker Dashboard
    This dashboard helps you manage, analyze, and configure your intelligent job discovery pipeline for blockchain, climate, and AI accelerators.

    **Sections:**
    - **Dashboard:** System and module health, file and environment status.
    - **Accelerator Management:** View, filter, and edit accelerator data.
    - **Job Discovery:** Explore raw job listings and sources.
    - **Matching Engine:** Analyze AI-powered job matches and scores.
    - **Alert Settings:** Configure email alerts and your CMF profile.
    - **Analytics:** Visualize trends, scores, and system performance.
    - **System Settings:** Clean logs, backup, and manage environment.
    - **Data Management:** Import/export CSVs and manage data files.

    **Expected File Schemas:**
    - `data/accelerators_list.csv`: Name, Website, Focus_Tags, Country, Status, Careers_URL, Discovery_Date
    - `data/jobs_raw.csv`: title, company, location, source_accelerator, job_url, date_posted
    - `data/jobs_scored.csv`: title, company, location, accelerator_name, job_url, ai_score, confidence, ai_reasoning, match_date, recommendation
    - `data/system_logs.csv`: timestamp, level, module, message
    - `data/email_logs.csv`: timestamp, recipient, job_count, success
    - `config/cmf_profile.json`: Your candidate-market fit profile (JSON)
    - `config/alert_settings.json`: Email alert settings (JSON)

    **Troubleshooting Tips:**
    - If a section shows missing data, check that the corresponding file exists and has the correct columns.
    - For environment variable errors, ensure your `.env` file is set up and loaded.
    - Use the System Settings section to clean logs or backup data.
    - For further help, consult the project README or contact support.
    """)

# --- Page Routing ---
section_map = {
    "dashboard": show_dashboard,
    "accelerator_management": show_accelerator_management,
    "job_discovery": show_job_discovery,
    "matching_engine": show_matching_engine,
    "alert_settings": show_alert_settings,
    "analytics": show_analytics,
    "system_settings": show_system_settings,
    "data_management": show_data_management,
    "help_about": show_help_about,
}

selected_section = [s[1] for s in SECTIONS if s[0] == page][0]
section_map[selected_section]() 