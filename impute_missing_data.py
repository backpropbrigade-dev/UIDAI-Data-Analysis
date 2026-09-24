import os
import pandas as pd
import numpy as np
from datetime import datetime

# ============================
# CONFIGURATION
# ============================

# Maximum gap size (in days) for which imputation is warranted
MAX_GAP_DAYS = 30  # Only impute if gap is <= 30 days

# Minimum observations required for a pincode to perform imputation
MIN_OBSERVATIONS = 3

# ============================
# HELPER FUNCTIONS
# ============================

def analyze_missing_patterns(df, count_cols, category):
    """
    Analyze missing data patterns before imputation.
    Returns statistics about missing values.
    """
    print(f"\n  🔍 Analyzing missing patterns for {category}...")
    
    stats = {
        'category': category,
        'total_rows': len(df),
        'columns_analyzed': []
    }
    
    for col in count_cols:
        missing_count = df[col].isna().sum()
        missing_pct = (missing_count / len(df)) * 100
        zero_count = (df[col] == 0).sum()
        zero_pct = (zero_count / len(df)) * 100
        
        stats['columns_analyzed'].append({
            'column': col,
            'missing_count': missing_count,
            'missing_pct': missing_pct,
            'zero_count': zero_count,
            'zero_pct': zero_pct
        })
        
        print(f"    {col}:")
        print(f"      Missing (NaN): {missing_count:,} ({missing_pct:.2f}%)")
        print(f"      True Zeros: {zero_count:,} ({zero_pct:.2f}%)")
    
    return stats

def impute_pincode_level(group, count_cols, max_gap_days=MAX_GAP_DAYS):
    """
    Impute missing values at the pincode level using forward/backward fill.
    Only imputes if:
    1. The gap is within max_gap_days
    2. There are sufficient observations for that pincode
    
    Returns the group with imputed values and a tracking flag.
    """
    # Sort by date to ensure proper forward/backward fill
    group = group.sort_values('date').copy()
    
    # Skip if too few observations
    if len(group) < MIN_OBSERVATIONS:
        return group
    
    # Add tracking columns for each count column
    for col in count_cols:
        tracking_col = f"{col}_imputed"
        group[tracking_col] = False
        
        # Identify missing values
        missing_mask = group[col].isna()
        
        if missing_mask.any():
            # Calculate time gaps between consecutive observations
            group['date_diff'] = group['date'].diff()
            
            # Forward fill with condition
            ffill_values = group[col].ffill()
            
            # Backward fill with condition
            bfill_values = group[col].bfill()
            
            # For each missing value, check if gap is small enough
            for idx in group[missing_mask].index:
                # Get position in group
                pos = group.index.get_loc(idx)
                
                # Check forward gap
                if pos > 0:
                    prev_idx = group.index[pos - 1]
                    date_gap = (group.loc[idx, 'date'] - group.loc[prev_idx, 'date']).days
                    
                    if date_gap <= max_gap_days and pd.notna(ffill_values.loc[idx]):
                        group.loc[idx, col] = ffill_values.loc[idx]
                        group.loc[idx, tracking_col] = True
                        continue
                
                # Check backward gap
                if pos < len(group) - 1:
                    next_idx = group.index[pos + 1]
                    date_gap = (group.loc[next_idx, 'date'] - group.loc[idx, 'date']).days
                    
                    if date_gap <= max_gap_days and pd.notna(bfill_values.loc[idx]):
                        group.loc[idx, col] = bfill_values.loc[idx]
                        group.loc[idx, tracking_col] = True
            
            # Clean up temporary column
            group = group.drop('date_diff', axis=1, errors='ignore')
    
    return group

def create_is_missing_flag(df, count_cols):
    """
    Create a consolidated 'is_missing' flag indicating if ANY imputation was performed on the row.
    """
    tracking_cols = [f"{col}_imputed" for col in count_cols]
    
    # Create is_missing flag (True if any column was imputed)
    df['is_missing'] = False
    for tracking_col in tracking_cols:
        if tracking_col in df.columns:
            df['is_missing'] = df['is_missing'] | df[tracking_col]
    
    return df

def generate_imputation_report(df, count_cols, category, pre_impute_stats, output_path):
    """
    Generate a comprehensive imputation report showing:
    - Pre/post imputation statistics
    - Proportion of filled vs actual data
    - Imputation logic documentation
    """
    report = []
    report.append(f"Missing Data Imputation Report: {category.upper()}")
    report.append("=" * 90)
    report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    report.append(f"\n📋 IMPUTATION CONFIGURATION")
    report.append(f"  Maximum gap for imputation: {MAX_GAP_DAYS} days")
    report.append(f"  Minimum observations per pincode: {MIN_OBSERVATIONS}")
    report.append(f"  Imputation method: Forward/Backward fill at pincode level")
    
    report.append(f"\n📊 DATASET OVERVIEW")
    report.append(f"  Total rows: {len(df):,}")
    report.append(f"  Total pincodes: {df['pincode'].nunique():,}")
    report.append(f"  Date range: {df['date'].min()} to {df['date'].max()}")
    
    # Overall imputation statistics
    if 'is_missing' in df.columns:
        imputed_rows = df['is_missing'].sum()
        imputed_pct = (imputed_rows / len(df)) * 100
        report.append(f"\n🔧 IMPUTATION SUMMARY")
        report.append(f"  Rows with any imputation: {imputed_rows:,} ({imputed_pct:.2f}%)")
        report.append(f"  Rows with actual data: {len(df) - imputed_rows:,} ({100 - imputed_pct:.2f}%)")
    
    # Column-level statistics
    report.append(f"\n📈 COLUMN-LEVEL ANALYSIS")
    report.append("")
    
    for col in count_cols:
        tracking_col = f"{col}_imputed"
        
        # Pre-imputation stats
        pre_stats = next((s for s in pre_impute_stats['columns_analyzed'] if s['column'] == col), None)
        
        # Post-imputation stats
        if tracking_col in df.columns:
            imputed_count = df[tracking_col].sum()
            imputed_pct = (imputed_count / len(df)) * 100
            
            still_missing = df[col].isna().sum()
            still_missing_pct = (still_missing / len(df)) * 100
        else:
            imputed_count = 0
            imputed_pct = 0.0
            still_missing = df[col].isna().sum()
            still_missing_pct = (still_missing / len(df)) * 100
        
        zero_count = (df[col] == 0).sum()
        zero_pct = (zero_count / len(df)) * 100
        
        report.append(f"  {col}:")
        if pre_stats:
            report.append(f"    Before imputation:")
            report.append(f"      Missing (NaN): {pre_stats['missing_count']:,} ({pre_stats['missing_pct']:.2f}%)")
            report.append(f"      True Zeros: {pre_stats['zero_count']:,} ({pre_stats['zero_pct']:.2f}%)")
        
        report.append(f"    After imputation:")
        report.append(f"      Values imputed: {imputed_count:,} ({imputed_pct:.2f}%)")
        report.append(f"      Still missing: {still_missing:,} ({still_missing_pct:.2f}%)")
        report.append(f"      True Zeros: {zero_count:,} ({zero_pct:.2f}%)")
        
        if pre_stats:
            filled_pct = (imputed_count / pre_stats['missing_count'] * 100) if pre_stats['missing_count'] > 0 else 0
            report.append(f"      Fill rate: {filled_pct:.2f}% of original missing values")
        
        report.append("")
    
    # Imputation by pincode
    report.append(f"📍 IMPUTATION BY PINCODE")
    if 'is_missing' in df.columns:
        pincode_stats = df.groupby('pincode').agg({
            'is_missing': ['sum', 'count']
        }).reset_index()
        pincode_stats.columns = ['pincode', 'imputed_count', 'total_count']
        pincode_stats['imputed_pct'] = (pincode_stats['imputed_count'] / pincode_stats['total_count']) * 100
        
        pincodes_with_imputation = (pincode_stats['imputed_count'] > 0).sum()
        total_pincodes = len(pincode_stats)
        
        report.append(f"  Pincodes with any imputation: {pincodes_with_imputation:,} / {total_pincodes:,}")
        report.append(f"\n  Top 10 pincodes by imputation count:")
        
        top_pincodes = pincode_stats.nlargest(10, 'imputed_count')
        for _, row in top_pincodes.iterrows():
            report.append(f"    {row['pincode']}: {int(row['imputed_count'])} / {int(row['total_count'])} ({row['imputed_pct']:.1f}%)")
    
    # Imputation logic documentation
    report.append(f"\n📝 IMPUTATION LOGIC")
    report.append(f"  Strategy: Pincode-level temporal imputation")
    report.append(f"  Method:")
    report.append(f"    1. Group data by pincode")
    report.append(f"    2. Sort chronologically by date")
    report.append(f"    3. For each missing value:")
    report.append(f"       - Check gap to previous observation")
    report.append(f"       - If gap ≤ {MAX_GAP_DAYS} days, forward fill")
    report.append(f"       - Otherwise, check gap to next observation")
    report.append(f"       - If gap ≤ {MAX_GAP_DAYS} days, backward fill")
    report.append(f"       - Otherwise, leave as NaN")
    report.append(f"    4. Skip pincodes with < {MIN_OBSERVATIONS} observations")
    report.append(f"\n  Rationale:")
    report.append(f"    - Preserves true zeros (no events) vs missing reporting (NaN)")
    report.append(f"    - Only fills intermittent gaps within reasonable timeframes")
    report.append(f"    - Maintains temporal consistency within each pincode")
    report.append(f"    - Flags all imputed values for transparency")
    
    # Save report
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    return '\n'.join(report)

# ============================
# MAIN PROCESSING
# ============================

def main():
    # Get the most recent output directory
    base_dir = os.getcwd()
    output_base = os.path.join(base_dir, "output")
    
    # Find most recent session directory (timestamped format: YYYY-MM-DD_HH-MM-SS)
    session_dirs = [d for d in os.listdir(output_base) 
                   if os.path.isdir(os.path.join(output_base, d)) and 
                   (d[0].isdigit() or '-' in d)]  # Filter for timestamped directories
    
    if not session_dirs:
        print("❌ No output directories found. Please run previous scripts first.")
        return
    
    latest_session = sorted(session_dirs)[-1]
    cleaned_dir = os.path.join(output_base, latest_session, "cleaned")
    
    if not os.path.exists(cleaned_dir):
        print(f"❌ Cleaned directory not found at: {cleaned_dir}")
        print("   Please run clean_datasets.py first.")
        return
    
    print(f"📂 Processing files from: {cleaned_dir}")
    print("=" * 90)
    
    # Create imputed subdirectory
    imputed_dir = os.path.join(cleaned_dir, "imputed")
    os.makedirs(imputed_dir, exist_ok=True)
    
    # Process each category
    categories = ["biometric", "enrolment", "demographic"]
    
    # Define count columns for each category
    count_columns = {
        "biometric": ["bio_age_5_17", "bio_age_17_"],
        "enrolment": ["age_0_5", "age_5_17", "age_18_greater"],
        "demographic": ["demo_age_5_17", "demo_age_17_"]
    }
    
    for category in categories:
        print(f"\n{'='*90}")
        print(f"🔄 Processing: {category.upper()}")
        print('='*90)
        
        # Find cleaned file
        cleaned_file = os.path.join(cleaned_dir, f"{category}_cleaned.csv")
        
        if not os.path.exists(cleaned_file):
            print(f"  ⚠ Cleaned file not found: {cleaned_file}")
            continue
        
        # Load data
        print(f"  📥 Loading {category} data...")
        df = pd.read_csv(cleaned_file, parse_dates=['date'])
        print(f"    Rows: {len(df):,}")
        
        # Get count columns for this category
        count_cols = count_columns.get(category, [])
        count_cols = [col for col in count_cols if col in df.columns]
        
        if not count_cols:
            print(f"  ⚠ No count columns found for {category}")
            continue
        
        # Analyze missing patterns (before imputation)
        pre_impute_stats = analyze_missing_patterns(df, count_cols, category)
        
        # Perform imputation at pincode level
        print(f"\n  🔧 Performing pincode-level imputation...")
        print(f"    Count columns: {', '.join(count_cols)}")
        
        df_imputed = df.groupby('pincode', group_keys=False).apply(
            lambda x: impute_pincode_level(x, count_cols, MAX_GAP_DAYS)
        )
        
        # Create consolidated is_missing flag
        print(f"\n  🏷️  Creating imputation tracking flags...")
        df_imputed = create_is_missing_flag(df_imputed, count_cols)
        
        # Count imputation results
        total_imputed = df_imputed['is_missing'].sum()
        imputed_pct = (total_imputed / len(df_imputed)) * 100
        print(f"    ✓ Rows with imputation: {total_imputed:,} ({imputed_pct:.2f}%)")
        
        # Save imputed file
        output_filename = f"{category}_imputed.csv"
        output_path = os.path.join(imputed_dir, output_filename)
        
        print(f"\n  💾 Saving imputed data...")
        df_imputed.to_csv(output_path, index=False)
        print(f"    ✓ Saved: {output_filename}")
        
        # Generate imputation report
        report_filename = f"{category}_imputation_report.txt"
        report_path = os.path.join(imputed_dir, report_filename)
        report = generate_imputation_report(df_imputed, count_cols, category, pre_impute_stats, report_path)
        print(f"\n  📋 Imputation report saved: {report_filename}")
    
    # Final summary
    print("\n" + "=" * 90)
    print("✅ IMPUTATION COMPLETE")
    print("=" * 90)
    print(f"\n📁 Imputed files saved to: {imputed_dir}")
    
    # List created files
    if os.path.exists(imputed_dir):
        files = os.listdir(imputed_dir)
        csv_files = [f for f in files if f.endswith('.csv')]
        report_files = [f for f in files if f.endswith('.txt')]
        
        print(f"\n📊 Files created:")
        for filename in csv_files:
            file_path = os.path.join(imputed_dir, filename)
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            print(f"  ✓ {filename} ({file_size_mb:.2f} MB)")
        
        print(f"\n📋 Reports created:")
        for filename in report_files:
            print(f"  ✓ {filename}")
    
    print("\n" + "=" * 90)

if __name__ == "__main__":
    main()
