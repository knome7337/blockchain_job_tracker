import os
import pandas as pd
from typing import Dict

class Module0Tester:
    def run_quality_analysis(self) -> Dict:
        if not os.path.exists(self.programs_file):
            print("❌ No programs file found. Run Module 0 first.")
            return {}
        df = pd.read_csv(self.programs_file)
        results = {
            'total_programs': len(df),
            'analysis_timestamp': pd.Timestamp.now().isoformat()
        }
        # Check for time limit warning in logs
        if os.path.exists('data/system_logs.csv'):
            with open('data/system_logs.csv') as f:
                log_content = f.read()
                if 'Time limit of' in log_content:
                    results['time_limit_reached'] = True
                else:
                    results['time_limit_reached'] = False
        # ... rest of your analysis ...
        # (existing code continues)
        return results

def main():
    tester = Module0Tester()
    report = tester.generate_test_report()
    print(report)
    # Save report
    with open('data/module_0_test_report.txt', 'w') as f:
        f.write(report)
    print(f"\n📄 Report saved to: data/module_0_test_report.txt") 