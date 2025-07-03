import os
import pandas as pd
import json
import streamlit as st
import plotly.express as px

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

# --- Robust Data Loading Utilities ---
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

# --- Section Stubs ---
def show_dashboard():
    st.title("📊 System Dashboard")
    status = get_system_status()
    # System health summary
    if status['overall_health'] == 'healthy':
        st.success("🟢 System Healthy")
    elif status['overall_health'] == 'warning':
        st.warning("🟡 Some Issues Detected")
    else:
        st.error("🔴 System Issues Detected")
    # Module status
    st.subheader("Module Status")
    for module, state in status['modules'].items():
        if state == 'active':
            st.markdown(f"✅ {module}")
        else:
            st.markdown(f"❌ {module}")
    # File health
    st.subheader("File Health")
    for path, info in status['files'].items():
        st.write(f"{path}: {info['status']} (rows: {info.get('rows', '-')})")
    # Env vars
    st.subheader("Environment Variables")
    for var, state in status['env'].items():
        if state == 'set':
            st.markdown(f"✅ {var} set")
        else:
            st.markdown(f"❌ {var} missing")

def show_accelerator_management():
    st.title("🏢 Accelerator Management")
    st.info("Accelerator management content coming soon.")

def show_job_discovery():
    st.title("🔍 Job Discovery")
    st.info("Job discovery content coming soon.")

def show_matching_engine():
    st.title("⚡ Matching Engine")
    st.info("Matching engine content coming soon.")

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