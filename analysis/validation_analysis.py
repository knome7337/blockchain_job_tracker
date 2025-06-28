"""
Data Analysis & Validation Parameter Tuning
Analyze Module 0.5 results and identify noise/issues
"""

import pandas as pd
import csv
from collections import Counter
import json

def analyze_validation_results():
    """Analyze the validation results and identify issues"""
    
    try:
        # Read the accelerators data
        df = pd.read_csv('data/accelerators_list.csv')
        
        print("🔍 VALIDATION RESULTS ANALYSIS")
        print("=" * 50)
        
        print(f"\n📊 BASIC STATS:")
        print(f"Total accelerators: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        
        # Status distribution
        if 'Status' in df.columns:
            print(f"\n📈 STATUS DISTRIBUTION:")
            status_counts = df['Status'].value_counts()
            for status, count in status_counts.items():
                percentage = (count / len(df)) * 100
                print(f"  {status}: {count} ({percentage:.1f}%)")
        
        # Activity score distribution
        if 'Activity_Score' in df.columns:
            print(f"\n⭐ ACTIVITY SCORE DISTRIBUTION:")
            score_stats = df['Activity_Score'].describe()
            print(f"  Average: {score_stats['mean']:.1f}")
            print(f"  Median: {score_stats['50%']:.1f}")
            print(f"  Range: {score_stats['min']:.0f} - {score_stats['max']:.0f}")
            
            # Score bins
            bins = [0, 3, 6, 8, 10]
            labels = ['Low (0-3)', 'Medium (4-6)', 'Good (7-8)', 'High (9-10)']
            df['Score_Bin'] = pd.cut(df['Activity_Score'], bins=bins, labels=labels, include_lowest=True)
            print(f"\n  Score Distribution:")
            for bin_name, count in df['Score_Bin'].value_counts().items():
                print(f"    {bin_name}: {count}")
        
        # Priority distribution
        if 'Scrape_Priority' in df.columns:
            print(f"\n🎯 SCRAPE PRIORITY:")
            priority_counts = df['Scrape_Priority'].value_counts()
            for priority, count in priority_counts.items():
                print(f"  {priority}: {count}")
        
        # Country analysis
        if 'Country' in df.columns:
            print(f"\n🌍 COUNTRY DISTRIBUTION:")
            country_counts = df['Country'].value_counts().head(10)
            for country, count in country_counts.items():
                print(f"  {country}: {count}")
        
        # Focus tags analysis
        if 'Focus_Tags' in df.columns:
            print(f"\n🏷️ FOCUS TAGS ANALYSIS:")
            all_tags = []
            for tags in df['Focus_Tags'].dropna():
                all_tags.extend([tag.strip() for tag in str(tags).split(',')])
            tag_counts = Counter(all_tags)
            for tag, count in tag_counts.most_common(10):
                print(f"  {tag}: {count}")
        
        # Website accessibility
        if 'Website_Accessible' in df.columns:
            accessible_count = df['Website_Accessible'].sum() if df['Website_Accessible'].dtype == bool else df[df['Website_Accessible'] == True].shape[0]
            total = len(df)
            print(f"\n🌐 WEBSITE ACCESSIBILITY:")
            print(f"  Accessible: {accessible_count}/{total} ({(accessible_count/total)*100:.1f}%)")
        
        # Job detection
        if 'Has_Jobs' in df.columns:
            jobs_count = df['Has_Jobs'].sum() if df['Has_Jobs'].dtype == bool else df[df['Has_Jobs'] == True].shape[0]
            total = len(df)
            print(f"\n💼 JOB DETECTION:")
            print(f"  Has jobs: {jobs_count}/{total} ({(jobs_count/total)*100:.1f}%)")
        
        return df
        
    except FileNotFoundError:
        print("❌ accelerators_list.csv not found. Run Module 0.5 first.")
        return None
    except Exception as e:
        print(f"❌ Error analyzing data: {e}")
        return None

def identify_noise_patterns(df):
    """Identify potential noise and false positives"""
    
    if df is None:
        return
    
    print("\n\n🔍 NOISE ANALYSIS")
    print("=" * 50)
    
    # High scores but suspicious patterns
    if 'Activity_Score' in df.columns and 'Validation_Notes' in df.columns:
        high_scores = df[df['Activity_Score'] >= 7]
        
        print(f"\n🚨 HIGH SCORE ENTRIES TO REVIEW ({len(high_scores)}):")
        for idx, row in high_scores.iterrows():
            print(f"\n  {row.get('Name', 'Unknown')}")
            print(f"    Score: {row.get('Activity_Score', 'N/A')}")
            print(f"    Country: {row.get('Country', 'N/A')}")
            print(f"    Website: {row.get('Website', 'N/A')}")
            print(f"    Notes: {row.get('Validation_Notes', 'N/A')}")
            print(f"    Focus: {row.get('Focus_Tags', 'N/A')}")
    
    # Low scores but might be real
    if 'Activity_Score' in df.columns:
        low_scores = df[df['Activity_Score'] <= 3]
        blockchain_low = low_scores[low_scores['Focus_Tags'].str.contains('blockchain', na=False)]
        
        print(f"\n⚠️ LOW SCORE BLOCKCHAIN ENTRIES ({len(blockchain_low)}):")
        for idx, row in blockchain_low.head(5).iterrows():
            print(f"  {row.get('Name', 'Unknown')} (Score: {row.get('Activity_Score', 'N/A')})")
    
    # Entries with errors
    if 'Status' in df.columns:
        errors = df[df['Status'] == 'error']
        print(f"\n❌ ERROR ENTRIES ({len(errors)}):")
        for idx, row in errors.head(5).iterrows():
            print(f"  {row.get('Name', 'Unknown')}: {row.get('Validation_Notes', 'N/A')}")

def manual_review_candidates(df):
    """Suggest entries for manual review"""
    
    if df is None:
        return
    
    print("\n\n👀 MANUAL REVIEW CANDIDATES")
    print("=" * 50)
    
    # Active status for manual verification
    if 'Status' in df.columns:
        active_entries = df[df['Status'] == 'active']
        
        print(f"\n🎯 TOP ACTIVE ACCELERATORS TO MANUALLY CHECK:")
        if 'Activity_Score' in df.columns:
            top_active = active_entries.nlargest(5, 'Activity_Score')
        else:
            top_active = active_entries.head(5)
        
        for idx, row in top_active.iterrows():
            print(f"\n  {row.get('Name', 'Unknown')}")
            print(f"    Website: {row.get('Website', 'N/A')}")
            print(f"    Careers: {row.get('Careers_URL', 'N/A')}")
            print(f"    Score: {row.get('Activity_Score', 'N/A')}")
            print(f"    Country: {row.get('Country', 'N/A')}")
            print(f"    Focus: {row.get('Focus_Tags', 'N/A')}")

def suggest_parameter_tuning(df):
    """Suggest parameter adjustments based on analysis"""
    
    if df is None:
        return
    
    print("\n\n⚙️ PARAMETER TUNING SUGGESTIONS")
    print("=" * 50)
    
    suggestions = []
    
    # Check if too many actives
    if 'Status' in df.columns:
        active_pct = (df['Status'] == 'active').sum() / len(df) * 100
        if active_pct > 50:
            suggestions.append(f"❗ {active_pct:.1f}% marked as 'active' - consider raising activity score threshold")
        elif active_pct < 10:
            suggestions.append(f"❗ Only {active_pct:.1f}% marked as 'active' - consider lowering activity score threshold")
    
    # Check average scores
    if 'Activity_Score' in df.columns:
        avg_score = df['Activity_Score'].mean()
        if avg_score > 7:
            suggestions.append(f"❗ Average score is {avg_score:.1f} - validation might be too lenient")
        elif avg_score < 3:
            suggestions.append(f"❗ Average score is {avg_score:.1f} - validation might be too strict")
    
    # Check error rate
    if 'Status' in df.columns:
        error_pct = (df['Status'] == 'error').sum() / len(df) * 100
        if error_pct > 30:
            suggestions.append(f"❗ {error_pct:.1f}% validation errors - check timeout/connection settings")
    
    # Check job detection
    if 'Has_Jobs' in df.columns:
        jobs_pct = df['Has_Jobs'].sum() / len(df) * 100
        if jobs_pct < 20:
            suggestions.append(f"❗ Only {jobs_pct:.1f}% have jobs detected - improve job detection patterns")
    
    print("\n🔧 RECOMMENDED ADJUSTMENTS:")
    if suggestions:
        for suggestion in suggestions:
            print(f"  {suggestion}")
    else:
        print("  ✅ Validation parameters look reasonable")
    
    # Specific tuning parameters
    print(f"\n📝 CURRENT THRESHOLDS TO REVIEW:")
    print(f"  Active status: activity_score >= 7")
    print(f"  Monitor status: 4 <= activity_score < 7") 
    print(f"  Inactive status: activity_score < 4")
    print(f"  Request timeout: 10 seconds")
    print(f"  Rate limiting: 1 second between requests")

def export_for_manual_review(df):
    """Export subsets for manual review"""
    
    if df is None:
        return
    
    try:
        # Export top active candidates
        if 'Status' in df.columns and 'Activity_Score' in df.columns:
            active_entries = df[df['Status'] == 'active'].nlargest(10, 'Activity_Score')
            active_entries[['Name', 'Website', 'Careers_URL', 'Country', 'Activity_Score', 'Focus_Tags']].to_csv(
                'data/manual_review_active.csv', index=False
            )
            print(f"\n💾 Exported top 10 active accelerators to: data/manual_review_active.csv")
        
        # Export suspicious high scores
        if 'Activity_Score' in df.columns:
            high_scores = df[df['Activity_Score'] >= 8]
            high_scores[['Name', 'Website', 'Activity_Score', 'Validation_Notes', 'Focus_Tags']].to_csv(
                'data/manual_review_high_scores.csv', index=False
            )
            print(f"💾 Exported high-score entries to: data/manual_review_high_scores.csv")
            
    except Exception as e:
        print(f"❌ Export failed: {e}")

def main():
    """Run complete analysis"""
    print("🚀 Starting validation results analysis...\n")
    
    # Load and analyze data
    df = analyze_validation_results()
    
    # Identify noise patterns
    identify_noise_patterns(df)
    
    # Suggest manual review candidates
    manual_review_candidates(df)
    
    # Suggest parameter tuning
    suggest_parameter_tuning(df)
    
    # Export for manual review
    export_for_manual_review(df)
    
    print(f"\n\n✅ Analysis complete!")
    print(f"Next steps:")
    print(f"1. Review exported CSV files")
    print(f"2. Manually check 3-5 'active' accelerators")
    print(f"3. Adjust validation parameters if needed")
    print(f"4. Re-run Module 0.5 with tuned parameters")

if __name__ == "__main__":
    main()