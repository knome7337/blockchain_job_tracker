#!/usr/bin/env python3
"""
Debug script to understand job filtering issues
"""

import pandas as pd
import json
from modules.module_3_alerts import EnhancedEmailAlerts

def debug_filtering():
    # Load the alert system
    alerts = EnhancedEmailAlerts()
    
    # Load jobs
    jobs = alerts.load_scored_jobs()
    print(f"📊 Total jobs loaded: {len(jobs)}")
    
    # Show filtering settings
    print(f"\n🔧 Filtering Settings:")
    print(f"  Min score: {alerts.alert_settings.get('min_score', 5.0)}")
    print(f"  Exclude keywords: {alerts.alert_settings.get('filtering', {}).get('exclude_keywords', [])}")
    print(f"  Min confidence: {alerts.alert_settings.get('filtering', {}).get('min_confidence', 'low')}")
    print(f"  Max jobs: {alerts.alert_settings.get('max_jobs', 10)}")
    
    # Test filtering step by step
    print(f"\n🔍 Step-by-step filtering analysis:")
    
    # Step 1: Score filtering
    score_threshold = alerts.alert_settings.get('min_score', 5.0)
    score_filtered = [job for job in jobs if job.get('ai_score', 0) >= score_threshold]
    print(f"  After score filtering (>= {score_threshold}): {len(score_filtered)} jobs")
    
    # Step 2: Exclude keywords filtering
    exclude_keywords = alerts.alert_settings.get('filtering', {}).get('exclude_keywords', [])
    keyword_filtered = []
    for job in score_filtered:
        title = job.get('title', '').lower()
        snippet = job.get('snippet', '').lower()
        text_content = f"{title} {snippet}"
        
        if any(keyword.lower() in text_content for keyword in exclude_keywords):
            print(f"    ❌ Filtered out: '{job.get('title', 'Unknown')}' due to exclude keywords")
            continue
        keyword_filtered.append(job)
    
    print(f"  After keyword filtering: {len(keyword_filtered)} jobs")
    
    # Step 3: Confidence filtering
    min_confidence = alerts.alert_settings.get('filtering', {}).get('min_confidence', 'low')
    confidence_filtered = []
    for job in keyword_filtered:
        confidence = job.get('confidence', '').lower()
        
        if min_confidence == 'high' and confidence not in ['high']:
            print(f"    ❌ Filtered out: '{job.get('title', 'Unknown')}' due to low confidence")
            continue
        elif min_confidence == 'medium' and confidence not in ['high', 'medium']:
            print(f"    ❌ Filtered out: '{job.get('title', 'Unknown')}' due to low confidence")
            continue
        
        confidence_filtered.append(job)
    
    print(f"  After confidence filtering: {len(confidence_filtered)} jobs")
    
    # Step 4: Recommendation filtering
    recommendation_filtered = []
    for job in confidence_filtered:
        recommendation = job.get('recommendation', '').lower()
        if recommendation in ['poor', 'avoid']:
            print(f"    ❌ Filtered out: '{job.get('title', 'Unknown')}' due to poor recommendation")
            continue
        recommendation_filtered.append(job)
    
    print(f"  After recommendation filtering: {len(recommendation_filtered)} jobs")
    
    # Show final results
    print(f"\n✅ Final filtered jobs ({len(recommendation_filtered)}):")
    for job in recommendation_filtered[:5]:  # Show first 5
        print(f"  - {job.get('title', 'Unknown')} (Score: {job.get('ai_score', 0)}, Confidence: {job.get('confidence', 'unknown')})")
    
    if len(recommendation_filtered) > 5:
        print(f"  ... and {len(recommendation_filtered) - 5} more")

if __name__ == "__main__":
    debug_filtering() 