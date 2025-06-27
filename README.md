# 🚀 Blockchain Job Tracker

This project is an automated job tracker designed to find and validate senior-level strategic roles (like Chief of Staff, Director of Strategy, and Grant Manager) in niche, high-impact sectors: **Blockchain**, **Climate Tech**, and **Sustainable Fashion**. It focuses on opportunities in **Mumbai** and **remote** settings.

## 🎯 Project Goal

The primary goal is to automate the discovery, filtering, and validation of job openings that align with a specific candidate profile (`config/cmf_profile.json`). The system identifies potential roles from across the web, validates them against strict criteria (roles, skills, industry, location, deal-breakers), and prepares a clean, high-quality list of opportunities, saving significant manual search time.

## 📂 Project Structure

```
blockchain_job_tracker/
├── venv/                    # Virtual environment (ignored by Git)
├── data/                    # Generated data and logs (ignored by Git)
│   ├── accelerators_list.csv
│   └── system_logs.csv
├── config/
│   └── cmf_profile.json     # Your candidate profile
├── modules/
│   ├── __init__.py
│   ├── module_0_directory.py
│   └── module_0_5_validator.py
├── ui/                      # For future Streamlit app
├── tests/                   # For future tests
├── .env                     # API keys and secrets (ignored by Git)
├── .gitignore               # Specifies files for Git to ignore
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## 🧼 Hygiene Checklist

Each time you return to this project, please perform the following checks to ensure a smooth workflow:

1.  **Activate Virtual Environment**: Make sure you are running commands within the project's isolated environment.
    ```bash
    source venv/bin/activate
    ```
2.  **Check Git Status**: See if there are any uncommitted changes.
    ```bash
    git status
    ```
3.  **Pull Latest Changes**: Ensure you have the latest version of the code from your repository.
    ```bash
    git pull origin main
    ```
4.  **Review Logs**: Check `data/system_logs.csv` for any errors or unexpected warnings from the last run.
    ```bash
    tail -n 50 data/system_logs.csv
    ```

---

## 📈 Future Enhancements & Suggestions

To increase the project's effectiveness, the following improvements are recommended:

1.  **Expand and Prioritize Search Sources**: Add direct scraping or API integration for high-value job boards (e.g., Climatebase, Web3 Jobs, Wellfound) instead of relying solely on generic searches.
2.  **Refine Filtering and Validation Logic**: Implement a scoring system to rank jobs based on how well they match the candidate profile, including roles, keywords, location, seniority, deal-breakers, and nice-to-haves.
3.  **Automate Alerts and Tracking**: Create a notification system (e.g., email, Slack) for newly discovered, high-scoring jobs.
4.  **Networking and Company Tracking**: Automate scraping of career pages and LinkedIn feeds for target organizations that may not post on general job boards.
5.  **User Customization**: Make preferences in `cmf_profile.json` more dynamic and easier to update, perhaps through a simple UI.
6.  **Testing and Validation**: Build a robust test suite in the `tests/` directory to unit test filtering logic, scrapers, and validation rules.
7.  **Documentation**: Keep this README and code comments updated, especially when adding new modules or changing logic.

### Summary of Key Code/Logic Changes Needed

To implement the suggestions above, the following changes are key:
*   **Add direct scrapers/API clients** for top job boards.
*   **Use a scoring/tagging system** in the validator for roles, industry, location, seniority, deal-breakers, and nice-to-haves.
*   **Automate alerts and deduplication** of job listings.
*   **Track company pages and LinkedIn** for unlisted roles.
*   **Make preferences easily configurable**.
*   **Add tests for your logic**. 