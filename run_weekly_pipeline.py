# run_weekly_pipeline.py - Complete Weekly Automation Script

import os
import sys
import time
import logging
import subprocess
from datetime import datetime
from typing import Dict, List

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/automation_logs.csv'),
        logging.StreamHandler()
    ]
)

class BlockchainJobPipeline:
    """Complete automation for blockchain job discovery pipeline"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.modules = {
            'module_0': 'modules/module_0_directory.py',
            'module_0_5': 'modules/module_0_5_validator.py', 
            'module_1': 'modules/module_1_scraper.py',
            'module_2': 'modules/module_2_matcher.py',
            'module_3': 'modules/module_3_alerts.py'
        }
        self.results = {}
        
    def run_module(self, module_name: str, module_path: str) -> Dict:
        """Run a single module with error handling"""
        logging.info(f"🚀 Starting {module_name}...")
        start_time = time.time()
        
        try:
            # Run the module
            result = subprocess.run(
                [sys.executable, module_path],
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                logging.info(f"✅ {module_name} completed successfully in {execution_time:.1f}s")
                return {
                    'status': 'success',
                    'execution_time': execution_time,
                    'output': result.stdout[-500:],  # Last 500 chars
                    'error': None
                }
            else:
                logging.error(f"❌ {module_name} failed with return code {result.returncode}")
                return {
                    'status': 'failed',
                    'execution_time': execution_time,
                    'output': result.stdout[-500:],
                    'error': result.stderr[-500:]
                }
                
        except subprocess.TimeoutExpired:
            logging.error(f"⏰ {module_name} timed out after 30 minutes")
            return {
                'status': 'timeout',
                'execution_time': 1800,
                'output': '',
                'error': 'Module execution timed out'
            }
        except Exception as e:
            logging.error(f"💥 {module_name} crashed: {str(e)}")
            return {
                'status': 'crashed',
                'execution_time': time.time() - start_time,
                'output': '',
                'error': str(e)
            }
    
    def run_complete_pipeline(self) -> Dict:
        """Run all modules in sequence"""
        logging.info("🎯 Starting complete blockchain job discovery pipeline...")
        
        # Module execution order matters!
        execution_order = [
            ('Discovery', 'module_0'),
            ('Validation', 'module_0_5'),
            ('Scraping', 'module_1'), 
            ('AI Matching', 'module_2'),
            ('Email Alerts', 'module_3')
        ]
        
        for step_name, module_key in execution_order:
            module_path = self.modules[module_key]
            
            # Check if module file exists
            if not os.path.exists(module_path):
                logging.error(f"❌ Module file not found: {module_path}")
                self.results[module_key] = {
                    'status': 'missing',
                    'execution_time': 0,
                    'output': '',
                    'error': f'Module file not found: {module_path}'
                }
                continue
            
            # Run the module
            self.results[module_key] = self.run_module(step_name, module_path)
            
            # Check if critical modules failed
            if module_key in ['module_2', 'module_3'] and self.results[module_key]['status'] != 'success':
                logging.warning(f"⚠️ Critical module {module_key} failed, but continuing...")
            
            # Small delay between modules
            time.sleep(2)
        
        # Calculate total execution time
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        # Generate summary
        successful_modules = sum(1 for r in self.results.values() if r['status'] == 'success')
        total_modules = len(self.results)
        
        summary = {
            'pipeline_start': self.start_time.isoformat(),
            'pipeline_end': datetime.now().isoformat(),
            'total_execution_time': total_time,
            'successful_modules': successful_modules,
            'total_modules': total_modules,
            'success_rate': successful_modules / total_modules,
            'modules': self.results
        }
        
        # Log final summary
        logging.info(f"🎉 Pipeline completed!")
        logging.info(f"   Total time: {total_time:.1f} seconds")
        logging.info(f"   Success rate: {successful_modules}/{total_modules}")
        logging.info(f"   Modules: {list(self.results.keys())}")
        
        return summary

def main():
    """Main automation function"""
    print("🚀 Blockchain Job Tracker - Weekly Pipeline Automation")
    print("=" * 60)
    
    # Check working directory
    if not os.path.exists('modules') or not os.path.exists('data'):
        print("❌ Error: Please run from the blockchain_job_tracker directory")
        print("Current directory:", os.getcwd())
        sys.exit(1)
    
    # Initialize and run pipeline
    pipeline = BlockchainJobPipeline()
    results = pipeline.run_complete_pipeline()
    
    # Print final summary
    print("\n" + "=" * 60)
    print("📊 PIPELINE EXECUTION SUMMARY")
    print("=" * 60)
    print(f"⏱️  Total Execution Time: {results['total_execution_time']:.1f} seconds")
    print(f"✅ Successful Modules: {results['successful_modules']}/{results['total_modules']}")
    print(f"📈 Success Rate: {results['success_rate']:.1%}")
    
    print("\n📋 Module Results:")
    for module, result in results['modules'].items():
        status_emoji = {
            'success': '✅',
            'failed': '❌', 
            'timeout': '⏰',
            'crashed': '💥',
            'missing': '📁'
        }.get(result['status'], '❓')
        
        print(f"  {status_emoji} {module}: {result['status']} ({result['execution_time']:.1f}s)")
        
        if result['error']:
            print(f"    Error: {result['error'][:100]}...")
    
    # Save detailed results
    import json
    with open('data/last_pipeline_run.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: data/last_pipeline_run.json")
    print(f"📊 Logs saved to: data/automation_logs.csv")
    
    # Exit code based on success
    if results['success_rate'] >= 0.6:  # 60% success rate minimum
        print("\n🎉 Pipeline completed successfully!")
        sys.exit(0)
    else:
        print("\n⚠️ Pipeline completed with errors. Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()

# =============================================================================
# run_scheduler.py - Background Python Scheduler
# =============================================================================

import schedule
import time
import threading
from datetime import datetime

def run_weekly_automation():
    """Function to run the complete pipeline"""
    print(f"\n🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Starting scheduled pipeline run...")
    
    # Import and run the main pipeline
    from run_weekly_pipeline import BlockchainJobPipeline
    
    pipeline = BlockchainJobPipeline()
    results = pipeline.run_complete_pipeline()
    
    print(f"✅ Scheduled run completed. Success rate: {results['success_rate']:.1%}")

def start_scheduler():
    """Start the background scheduler"""
    print("🚀 Blockchain Job Tracker - Background Scheduler")
    print("=" * 50)
    print("📅 Scheduled: Every Monday at 9:00 AM")
    print("🔄 Running in background...")
    print("💡 Press Ctrl+C to stop")
    print("=" * 50)
    
    # Schedule the job
    schedule.every().monday.at("09:00").do(run_weekly_automation)
    
    # Option to run daily during testing
    # schedule.every().day.at("09:00").do(run_weekly_automation)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n⛔ Scheduler stopped by user")

if __name__ == "__main__":
    start_scheduler()

# =============================================================================
# Manual Execution Commands
# =============================================================================

"""
USAGE INSTRUCTIONS:

1. MANUAL WEEKLY RUN:
   python run_weekly_pipeline.py
   
2. BACKGROUND SCHEDULER:
   python run_scheduler.py
   
3. TEST INDIVIDUAL MODULES:
   python modules/module_2_matcher.py
   python modules/module_3_alerts.py --test
   
4. CHECK LAST RUN RESULTS:
   cat data/last_pipeline_run.json
   tail data/automation_logs.csv

5. EMERGENCY STOP SCHEDULER:
   Ctrl+C (if running in terminal)
   
Expected execution time: 10-20 minutes for complete pipeline
"""

