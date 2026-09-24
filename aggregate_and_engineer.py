import os
import pandas as pd
import numpy as np
from datetime import datetime

# ============================
# CONFIGURATION
# ============================

# Count columns for each category
COUNT_COLUMNS = {
    "biometric": ["bio_age_5_17", "bio_age_17_"],
    "enrolment": ["age_0_5", "age_5_17", "age_18_greater"],
    "demographic": ["demo_age_5_17", "demo_age_17_"]
}

# ============================
# AGGREGATION FUNCTIONS
# ============================

def verify_aggregation(original_df, aggregated_df, count_cols, agg_type):
    """
    Verify that aggregation preserves totals.
    Returns True if verification passes, False otherwise.
    """
    print(f"\n  🔍 Verifying {agg_type} aggregation...")
    
    all_verified = True
    for col in count_cols:
        if col in original_df.columns and col in aggregated_df.columns:
            original_sum = original_df[col].sum()
            aggregated_sum = aggregated_df[col].sum()
            
            diff = abs(original_sum - aggregated_sum)
            match = diff < 0.01  # Allow for tiny floating point errors
            
            status = "✓" if match else "✗"
            print(f"    {status} {col}: Original={original_sum:,}, Aggregated={aggregated_sum:,}")
            
            if not match:
                all_verified = False
                print(f"      ⚠ Difference: {diff:,}")
    
    return all_verified

def aggregate_monthly(df, count_cols, category):
    """
    Aggregate daily data to monthly level.
    Groups by (year, month, state, district, pincode) and sums counts.
    """
    print(f"\n  📅 Aggregating to monthly level...")
    
    # Create year and month columns
    df_agg = df.copy()
    df_agg['year'] = df_agg['date'].dt.year
    df_agg['month'] = df_agg['date'].dt.month
    
    # Group and aggregate
    group_cols = ['year', 'month', 'state', 'district', 'pincode']
    agg_dict = {col: 'sum' for col in count_cols if col in df.columns}
    
    monthly = df_agg.groupby(group_cols, as_index=False).agg(agg_dict)
    
    # Create a date column (first day of month)
    monthly['date'] = pd.to_datetime(monthly[['year', 'month']].assign(day=1))
    
    print(f"    Rows: {len(df):,} → {len(monthly):,} ({len(monthly)/len(df)*100:.1f}%)")
    
    # Verify
    verify_aggregation(df, monthly, count_cols, "monthly")
    
    return monthly

def aggregate_yearly(df, count_cols, category):
    """
    Aggregate daily data to yearly level.
    Groups by (year, state, district, pincode) and sums counts.
    """
    print(f"\n  📅 Aggregating to yearly level...")
    
    # Create year column
    df_agg = df.copy()
    df_agg['year'] = df_agg['date'].dt.year
    
    # Group and aggregate
    group_cols = ['year', 'state', 'district', 'pincode']
    agg_dict = {col: 'sum' for col in count_cols if col in df.columns}
    
    yearly = df_agg.groupby(group_cols, as_index=False).agg(agg_dict)
    
    # Create a date column (first day of year)
    yearly['date'] = pd.to_datetime(yearly['year'].astype(str) + '-01-01')
    
    print(f"    Rows: {len(df):,} → {len(yearly):,} ({len(yearly)/len(df)*100:.1f}%)")
    
    # Verify
    verify_aggregation(df, yearly, count_cols, "yearly")
    
    return yearly

def aggregate_district(df, count_cols, category):
    """
    Aggregate pincode-level data to district level.
    Groups by (state, district, date) and sums counts.
    """
    print(f"\n  🗺️  Aggregating to district level...")
    
    # Group and aggregate
    group_cols = ['state', 'district', 'date']
    agg_dict = {col: 'sum' for col in count_cols if col in df.columns}
    
    district = df.groupby(group_cols, as_index=False).agg(agg_dict)
    
    print(f"    Rows: {len(df):,} → {len(district):,} ({len(district)/len(df)*100:.1f}%)")
    print(f"    Unique districts: {district['district'].nunique():,}")
    
    # Verify
    verify_aggregation(df, district, count_cols, "district")
    
    return district

def aggregate_state(df, count_cols, category):
    """
    Aggregate district-level data to state level.
    Groups by (state, date) and sums counts.
    """
    print(f"\n  🗺️  Aggregating to state level...")
    
    # Group and aggregate
    group_cols = ['state', 'date']
    agg_dict = {col: 'sum' for col in count_cols if col in df.columns}
    
    state = df.groupby(group_cols, as_index=False).agg(agg_dict)
    
    print(f"    Rows: {len(df):,} → {len(state):,} ({len(state)/len(df)*100:.1f}%)")
    print(f"    Unique states: {state['state'].nunique():,}")
    
    # Verify
    verify_aggregation(df, state, count_cols, "state")
    
    return state

# ============================
# FEATURE ENGINEERING FUNCTIONS
# ============================

def add_totals(df, category):
    """
    Add total count column for each category.
    """
    print(f"\n  ➕ Adding total counts...")
    
    if category == "biometric":
        df['Total_Biometrics'] = df['bio_age_5_17'] + df['bio_age_17_']
        print(f"    Created: Total_Biometrics")
        
    elif category == "enrolment":
        df['Total_Enrolments'] = df['age_0_5'] + df['age_5_17'] + df['age_18_greater']
        print(f"    Created: Total_Enrolments")
        
    elif category == "demographic":
        df['Total_Demographics'] = df['demo_age_5_17'] + df['demo_age_17_']
        print(f"    Created: Total_Demographics")
    
    return df

def add_shares(df, category):
    """
    Add share/rate columns showing proportion of each age group.
    """
    print(f"\n  📊 Adding shares and rates...")
    
    if category == "biometric":
        total = df['Total_Biometrics']
        df['share_bio_5_17'] = (df['bio_age_5_17'] / total * 100).round(2)
        df['share_bio_17_'] = (df['bio_age_17_'] / total * 100).round(2)
        print(f"    Created: share_bio_5_17, share_bio_17_")
        
    elif category == "enrolment":
        total = df['Total_Enrolments']
        df['share_age_0_5'] = (df['age_0_5'] / total * 100).round(2)
        df['share_age_5_17'] = (df['age_5_17'] / total * 100).round(2)
        df['share_age_18_greater'] = (df['age_18_greater'] / total * 100).round(2)
        print(f"    Created: share_age_0_5, share_age_5_17, share_age_18_greater")
        
    elif category == "demographic":
        total = df['Total_Demographics']
        df['share_demo_5_17'] = (df['demo_age_5_17'] / total * 100).round(2)
        df['share_demo_17_'] = (df['demo_age_17_'] / total * 100).round(2)
        print(f"    Created: share_demo_5_17, share_demo_17_")
    
    # Replace inf and NaN with 0 (division by zero cases)
    share_cols = [col for col in df.columns if col.startswith('share_')]
    df[share_cols] = df[share_cols].replace([np.inf, -np.inf, np.nan], 0)
    
    return df

def add_temporal_features(df, count_cols, category):
    """
    Add temporal features: rolling averages and growth rates.
    Features are calculated at the pincode level.
    """
    print(f"\n  ⏱️  Adding temporal features...")
    
    # Sort by pincode and date
    df = df.sort_values(['pincode', 'date']).reset_index(drop=True)
    
    # Add rolling averages (7-day and 30-day)
    print(f"    Computing rolling averages...")
    for col in count_cols:
        if col in df.columns:
            # 7-day rolling average
            df[f'{col}_7d_avg'] = df.groupby('pincode')[col].transform(
                lambda x: x.rolling(window=7, min_periods=1).mean().round(2)
            )
            
            # 30-day rolling average
            df[f'{col}_30d_avg'] = df.groupby('pincode')[col].transform(
                lambda x: x.rolling(window=30, min_periods=1).mean().round(2)
            )
    
    print(f"      ✓ Created 7-day and 30-day rolling averages")
    
    # Add month-over-month growth
    print(f"    Computing month-over-month growth...")
    df['year_month'] = df['date'].dt.to_period('M')
    
    for col in count_cols:
        if col in df.columns:
            # Aggregate to monthly first
            monthly_pincode = df.groupby(['pincode', 'year_month'])[col].sum().reset_index()
            
            # Calculate MoM growth
            monthly_pincode[f'{col}_mom_growth'] = monthly_pincode.groupby('pincode')[col].pct_change() * 100
            monthly_pincode[f'{col}_mom_growth'] = monthly_pincode[f'{col}_mom_growth'].round(2)
            
            # Merge back
            df = df.merge(
                monthly_pincode[['pincode', 'year_month', f'{col}_mom_growth']],
                on=['pincode', 'year_month'],
                how='left'
            )
    
    print(f"      ✓ Created month-over-month growth rates")
    
    # Clean up temporary columns
    df = df.drop(['year_month', 'year', 'day_of_year'], axis=1, errors='ignore')
    
    # Replace inf and NaN in growth rates with 0
    growth_cols = [col for col in df.columns if 'growth' in col or 'avg' in col]
    df[growth_cols] = df[growth_cols].replace([np.inf, -np.inf, np.nan], 0)
    
    return df

# ============================
# CROSS-CATEGORY INTEGRATION
# ============================

def integrate_categories(bio_df, enrol_df, demo_df, output_dir):
    """
    Outer join the three category datasets and create combined metrics.
    """
    print(f"\n{'='*90}")
    print(f"🔗 CROSS-CATEGORY INTEGRATION")
    print('='*90)
    
    # Prepare dataframes - select relevant columns
    print(f"\n  📋 Preparing datasets for integration...")
    
    # Keep only essential columns for joining
    join_cols = ['date', 'state', 'district', 'pincode']
    
    bio_cols = join_cols + [col for col in bio_df.columns if col.startswith(('bio_', 'Total_Biometrics', 'share_bio'))]
    enrol_cols = join_cols + [col for col in enrol_df.columns if col.startswith(('age_', 'Total_Enrolments', 'share_age'))]
    demo_cols = join_cols + [col for col in demo_df.columns if col.startswith(('demo_', 'Total_Demographics', 'share_demo'))]
    
    bio_subset = bio_df[bio_cols].copy()
    enrol_subset = enrol_df[enrol_cols].copy()
    demo_subset = demo_df[demo_cols].copy()
    
    print(f"    Biometric columns: {len(bio_cols)}")
    print(f"    Enrolment columns: {len(enrol_cols)}")
    print(f"    Demographic columns: {len(demo_cols)}")
    
    # Perform outer joins
    print(f"\n  🔗 Performing outer joins...")
    
    # First join: biometric + enrolment
    integrated = bio_subset.merge(
        enrol_subset,
        on=join_cols,
        how='outer',
        indicator='_merge_1'
    )
    print(f"    After bio + enrol: {len(integrated):,} rows")
    
    # Second join: add demographic
    integrated = integrated.merge(
        demo_subset,
        on=join_cols,
        how='outer',
        indicator='_merge_2'
    )
    print(f"    After adding demo: {len(integrated):,} rows")
    
    # Drop merge indicators
    integrated = integrated.drop(['_merge_1', '_merge_2'], axis=1, errors='ignore')
    
    # Fill NaN with 0 for count columns (preserve NaN for shares/rates)
    print(f"\n  🔢 Handling missing values...")
    count_cols_to_fill = [col for col in integrated.columns 
                          if any(x in col for x in ['bio_', 'age_', 'demo_', 'Total_']) 
                          and 'share_' not in col and 'growth' not in col and 'avg' not in col]
    
    integrated[count_cols_to_fill] = integrated[count_cols_to_fill].fillna(0)
    print(f"    Filled {len(count_cols_to_fill)} count columns with 0")
    
    # Recalculate totals after filling
    print(f"\n  ➕ Computing combined metrics...")
    
    if 'Total_Biometrics' in integrated.columns:
        integrated['Total_Biometrics'] = integrated['Total_Biometrics'].fillna(0)
    else:
        integrated['Total_Biometrics'] = 0
        
    if 'Total_Enrolments' in integrated.columns:
        integrated['Total_Enrolments'] = integrated['Total_Enrolments'].fillna(0)
    else:
        integrated['Total_Enrolments'] = 0
        
    if 'Total_Demographics' in integrated.columns:
        integrated['Total_Demographics'] = integrated['Total_Demographics'].fillna(0)
    else:
        integrated['Total_Demographics'] = 0
    
    # Create combined activity metric
    integrated['Total_Activity'] = (
        integrated['Total_Biometrics'] + 
        integrated['Total_Enrolments'] + 
        integrated['Total_Demographics']
    )
    
    print(f"    Created: Total_Activity")
    
    # Spot checks
    print(f"\n  ✅ Spot-checking alignment...")
    
    # Check a few random dates and states
    sample_dates = integrated['date'].dropna().sample(min(3, len(integrated['date'].dropna())))
    for sample_date in sample_dates:
        date_data = integrated[integrated['date'] == sample_date]
        if len(date_data) > 0:
            sample = date_data.iloc[0]
            print(f"    Date: {sample['date']}, State: {sample['state']}, District: {sample['district']}")
            print(f"      Pincode: {sample['pincode']}")
            print(f"      Biometric: {sample.get('Total_Biometrics', 0):,.0f}, " +
                  f"Enrolment: {sample.get('Total_Enrolments', 0):,.0f}, " +
                  f"Demographic: {sample.get('Total_Demographics', 0):,.0f}, " +
                  f"Total: {sample['Total_Activity']:,.0f}")
    
    # Save integrated dataset
    output_path = os.path.join(output_dir, "integrated_all_categories.csv")
    integrated.to_csv(output_path, index=False)
    
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n  💾 Saved integrated dataset: integrated_all_categories.csv ({file_size_mb:.2f} MB)")
    print(f"    Total rows: {len(integrated):,}")
    print(f"    Total columns: {len(integrated.columns)}")
    
    return integrated

# ============================
# MAIN PROCESSING
# ============================

def main():
    # Get the imputed directory
    base_dir = os.getcwd()
    imputed_dir = os.path.join(base_dir, "output", "imputed")
    
    if not os.path.exists(imputed_dir):
        # Try the alternate nested structure
        output_base = os.path.join(base_dir, "output")
        session_dirs = [d for d in os.listdir(output_base) 
                       if os.path.isdir(os.path.join(output_base, d)) and d[0].isdigit()]
        
        if session_dirs:
            latest_session = sorted(session_dirs)[-1]
            imputed_dir = os.path.join(output_base, latest_session, "cleaned", "imputed")
    
    if not os.path.exists(imputed_dir):
        print(f"❌ Imputed directory not found. Please run impute_missing_data.py first.")
        print(f"   Checked: {imputed_dir}")
        return
    
    print(f"📂 Processing files from: {imputed_dir}")
    print("=" * 90)
    
    # Create aggregated and features subdirectory
    features_dir = os.path.join(imputed_dir, "features")
    os.makedirs(features_dir, exist_ok=True)
    
    # Track all dataframes for integration
    category_dfs = {}
    
    # Process each category
    for category in ["biometric", "enrolment", "demographic"]:
        print(f"\n{'='*90}")
        print(f"🔄 Processing: {category.upper()}")
        print('='*90)
        
        # Load imputed data
        imputed_file = os.path.join(imputed_dir, f"{category}_imputed.csv")
        
        if not os.path.exists(imputed_file):
            print(f"  ⚠ Imputed file not found: {imputed_file}")
            continue
        
        print(f"  📥 Loading data...")
        df = pd.read_csv(imputed_file, parse_dates=['date'])
        print(f"    Rows: {len(df):,}")
        
        count_cols = COUNT_COLUMNS[category]
        
        # === AGGREGATIONS ===
        print(f"\n  📊 TEMPORAL AGGREGATIONS")
        
        # Monthly aggregation
        monthly = aggregate_monthly(df, count_cols, category)
        monthly_path = os.path.join(features_dir, f"{category}_monthly.csv")
        monthly.to_csv(monthly_path, index=False)
        print(f"    💾 Saved: {category}_monthly.csv")
        
        # Yearly aggregation
        yearly = aggregate_yearly(df, count_cols, category)
        yearly_path = os.path.join(features_dir, f"{category}_yearly.csv")
        yearly.to_csv(yearly_path, index=False)
        print(f"    💾 Saved: {category}_yearly.csv")
        
        print(f"\n  📊 SPATIAL AGGREGATIONS")
        
        # District aggregation
        district = aggregate_district(df, count_cols, category)
        district_path = os.path.join(features_dir, f"{category}_district.csv")
        district.to_csv(district_path, index=False)
        print(f"    💾 Saved: {category}_district.csv")
        
        # State aggregation
        state = aggregate_state(district, count_cols, category)
        state_path = os.path.join(features_dir, f"{category}_state.csv")
        state.to_csv(state_path, index=False)
        print(f"    💾 Saved: {category}_state.csv")
        
        # === FEATURE ENGINEERING ===
        print(f"\n  🔧 FEATURE ENGINEERING")
        
        df = add_totals(df, category)
        df = add_shares(df, category)
        df = add_temporal_features(df, count_cols, category)
        
        # Save enriched dataset
        enriched_path = os.path.join(features_dir, f"{category}_enriched.csv")
        df.to_csv(enriched_path, index=False)
        file_size_mb = os.path.getsize(enriched_path) / (1024 * 1024)
        print(f"\n  💾 Saved enriched dataset: {category}_enriched.csv ({file_size_mb:.2f} MB)")
        print(f"    Total columns: {len(df.columns)}")
        
        # Store for integration
        category_dfs[category] = df
    
    # === CROSS-CATEGORY INTEGRATION ===
    if len(category_dfs) == 3:
        integrated = integrate_categories(
            category_dfs['biometric'],
            category_dfs['enrolment'],
            category_dfs['demographic'],
            features_dir
        )
    
    # Final summary
    print("\n" + "=" * 90)
    print("✅ AGGREGATION & FEATURE ENGINEERING COMPLETE")
    print("=" * 90)
    print(f"\n📁 All files saved to: {features_dir}")
    
    # List all created files
    if os.path.exists(features_dir):
        files = sorted(os.listdir(features_dir))
        
        print(f"\n📊 Files created ({len(files)} total):")
        for filename in files:
            file_path = os.path.join(features_dir, filename)
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            print(f"  ✓ {filename} ({file_size_mb:.2f} MB)")
    
    print("\n" + "=" * 90)

if __name__ == "__main__":
    main()
