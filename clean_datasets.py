import os
import pandas as pd
import numpy as np
from datetime import datetime

# ============================
# CONFIGURATION
# ============================

# Comprehensive geographic mapping for known variants
geo_mapping = {
    # State mappings
    "Dadra & Nagar Haveli": "Dadra and Nagar Haveli",
    "Dadra & Nager Haveli": "Dadra and Nagar Haveli",
    "NCT Of Delhi": "Delhi",
    "Nct Of Delhi": "Delhi",
    "National Capital Territory Of Delhi": "Delhi",
    "Andaman & Nicobar Islands": "Andaman and Nicobar Islands",
    "Jammu & Kashmir": "Jammu and Kashmir",
    "Daman & Diu": "Daman and Diu",
    "Chhattisgarh": "Chhattisgarh",
    "Chattisgarh": "Chhattisgarh",
}

# ============================
# HELPER FUNCTIONS
# ============================

def parse_dates(df, date_col="date"):
    """
    Parse date column from dd-mm-yyyy format and validate.
    Returns DataFrame with parsed dates and prints validation info.
    """
    print(f"\n  📅 Parsing dates...")
    
    # Parse dates
    df[date_col] = pd.to_datetime(df[date_col], format="%d-%m-%Y", errors="coerce")
    
    # Track invalid dates
    invalid_dates = df[date_col].isna().sum()
    if invalid_dates > 0:
        print(f"    ⚠ Found {invalid_dates:,} invalid date(s)")
    
    # Validate date range
    min_date = df[date_col].min()
    max_date = df[date_col].max()
    date_span_days = (max_date - min_date).days
    date_span_years = date_span_days / 365.25
    
    print(f"    ✓ Date range: {min_date.date()} to {max_date.date()}")
    print(f"    ✓ Span: {date_span_days} days ({date_span_years:.1f} years)")
    
    # Count unique months and years
    unique_months = df[date_col].dt.to_period('M').nunique()
    unique_years = df[date_col].dt.year.nunique()
    print(f"    ✓ Unique months: {unique_months}, Unique years: {unique_years}")
    
    return df

def standardize_geography(df, geo_cols=["state", "district"], mapping=geo_mapping):
    """
    Standardize geographic columns: strip whitespace, title case, apply mappings.
    """
    print(f"\n  🗺️  Standardizing geography...")
    
    for col in geo_cols:
        if col not in df.columns:
            continue
            
        before_unique = df[col].nunique()
        
        # Strip and title case
        df[col] = df[col].astype(str).str.strip().str.title()
        
        # Apply mappings
        df[col] = df[col].replace(mapping)
        
        after_unique = df[col].nunique()
        
        print(f"    ✓ {col.title()}: {before_unique} → {after_unique} unique values")
        
        # Show top 5 values
        top_values = df[col].value_counts().head(5)
        print(f"      Top values: {', '.join(top_values.index.tolist()[:3])}")
    
    return df

def validate_pincode(df, pincode_col="pincode"):
    """
    Validate and standardize pincodes:
    - Convert to zero-padded 6-digit strings
    - Flag/drop invalid formats
    """
    print(f"\n  📍 Validating pincodes...")
    
    initial_count = len(df)
    
    # Convert to string and strip
    df[pincode_col] = df[pincode_col].astype(str).str.strip()
    
    # Pad with zeros to 6 digits
    df[pincode_col] = df[pincode_col].str.zfill(6)
    
    # Validate format (exactly 6 digits)
    valid_mask = df[pincode_col].str.match(r"^\d{6}$", na=False)
    invalid_count = (~valid_mask).sum()
    
    if invalid_count > 0:
        print(f"    ⚠ Found {invalid_count:,} invalid pincode(s) ({invalid_count/initial_count*100:.2f}%)")
        
        # Show sample invalid pincodes
        invalid_samples = df.loc[~valid_mask, pincode_col].unique()[:5]
        print(f"      Samples: {', '.join(map(str, invalid_samples))}")
        
        # Drop invalid rows
        df = df[valid_mask].copy()
        print(f"    ✓ Dropped invalid rows, remaining: {len(df):,}")
    else:
        print(f"    ✓ All pincodes valid")
    
    # Validate pincode ranges (Indian pincodes: 110001-855120)
    df_numeric = pd.to_numeric(df[pincode_col], errors='coerce')
    min_pin = df_numeric.min()
    max_pin = df_numeric.max()
    print(f"    ✓ Pincode range: {int(min_pin):06d} to {int(max_pin):06d}")
    
    return df

def cast_count_columns(df, exclude_cols={"date", "state", "district", "pincode"}):
    """
    Cast all count columns to nullable integers (Int64).
    Coerce non-numeric values to NaN.
    """
    print(f"\n  🔢 Casting count columns...")
    
    count_cols = [c for c in df.columns if c not in exclude_cols]
    
    for col in count_cols:
        before_nulls = df[col].isna().sum()
        
        # Convert to numeric (coerce errors to NaN)
        df[col] = pd.to_numeric(df[col], errors="coerce")
        
        after_nulls = df[col].isna().sum()
        new_nulls = after_nulls - before_nulls
        
        if new_nulls > 0:
            print(f"    ⚠ {col}: {new_nulls} non-numeric value(s) coerced to NaN")
        
        # Cast to nullable integer
        df[col] = df[col].astype("Int64")
    
    print(f"    ✓ Converted {len(count_cols)} column(s) to Int64")
    print(f"      Columns: {', '.join(count_cols)}")
    
    return df

def generate_data_quality_report(df, category, output_path):
    """
    Generate a data quality report for the cleaned dataset.
    """
    report = []
    report.append(f"Data Quality Report: {category.upper()}")
    report.append("=" * 80)
    report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\n📊 Dataset Overview")
    report.append(f"  Rows: {len(df):,}")
    report.append(f"  Columns: {len(df.columns)}")
    report.append(f"\n📋 Column Data Types")
    
    for col in df.columns:
        dtype = df[col].dtype
        null_count = df[col].isna().sum()
        null_pct = (null_count / len(df)) * 100
        report.append(f"  {col}: {dtype} (nulls: {null_count:,}, {null_pct:.2f}%)")
    
    report.append(f"\n📅 Date Statistics")
    if 'date' in df.columns:
        report.append(f"  Min: {df['date'].min()}")
        report.append(f"  Max: {df['date'].max()}")
        report.append(f"  Unique dates: {df['date'].nunique():,}")
    
    report.append(f"\n🗺️  Geographic Coverage")
    if 'state' in df.columns:
        report.append(f"  Unique states: {df['state'].nunique()}")
        report.append(f"  Top 5 states:")
        for state, count in df['state'].value_counts().head(5).items():
            report.append(f"    - {state}: {count:,} records")
    
    if 'district' in df.columns:
        report.append(f"  Unique districts: {df['district'].nunique()}")
    
    if 'pincode' in df.columns:
        report.append(f"  Unique pincodes: {df['pincode'].nunique()}")
    
    # Count columns statistics
    count_cols = [c for c in df.columns if c not in {'date', 'state', 'district', 'pincode'}]
    if count_cols:
        report.append(f"\n📈 Count Columns Summary")
        for col in count_cols:
            total = df[col].sum()
            mean = df[col].mean()
            report.append(f"  {col}: Total={total:,}, Mean={mean:.1f}")
    
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
    
    # Find most recent session directory
    session_dirs = [d for d in os.listdir(output_base) if os.path.isdir(os.path.join(output_base, d))]
    if not session_dirs:
        print("❌ No output directories found. Please run process_datasets.py first.")
        return
    
    latest_session = sorted(session_dirs)[-1]
    out_dir = os.path.join(output_base, latest_session)
    
    print(f"📂 Processing files from: {out_dir}")
    print("=" * 80)
    
    # Create cleaned subdirectory
    cleaned_dir = os.path.join(out_dir, "cleaned")
    os.makedirs(cleaned_dir, exist_ok=True)
    
    # Process each category
    categories = ["biometric", "enrolment", "demographic"]
    cleaned_files = []
    
    for category in categories:
        print(f"\n{'='*80}")
        print(f"🔄 Processing: {category.upper()}")
        print('='*80)
        
        # Find master file
        master_file = os.path.join(out_dir, f"{category}_master.csv")
        
        if not os.path.exists(master_file):
            print(f"  ⚠ Master file not found: {master_file}")
            continue
        
        # Load data (read all as strings initially)
        print(f"  📥 Loading {category} data...")
        df = pd.read_csv(master_file, dtype=str, low_memory=False)
        print(f"    Initial rows: {len(df):,}")
        
        # Apply cleaning steps
        df = parse_dates(df)
        df = standardize_geography(df)
        df = validate_pincode(df)
        df = cast_count_columns(df)
        
        # Save cleaned file
        output_filename = f"{category}_cleaned.csv"
        output_path = os.path.join(cleaned_dir, output_filename)
        
        print(f"\n  💾 Saving cleaned data...")
        df.to_csv(output_path, index=False)
        print(f"    ✓ Saved: {output_filename}")
        print(f"    ✓ Final rows: {len(df):,}")
        
        cleaned_files.append(output_filename)
        
        # Generate data quality report
        report_filename = f"{category}_quality_report.txt"
        report_path = os.path.join(cleaned_dir, report_filename)
        report = generate_data_quality_report(df, category, report_path)
        print(f"\n  📋 Quality report saved: {report_filename}")
    
    # Final summary
    print("\n" + "=" * 80)
    print("✅ CLEANING COMPLETE")
    print("=" * 80)
    print(f"\n📁 Cleaned files saved to: {cleaned_dir}")
    print(f"\nFiles created:")
    for filename in cleaned_files:
        file_path = os.path.join(cleaned_dir, filename)
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        print(f"  ✓ {filename} ({file_size_mb:.2f} MB)")
    
    print(f"\n📊 Quality reports:")
    for category in categories:
        report_file = f"{category}_quality_report.txt"
        if os.path.exists(os.path.join(cleaned_dir, report_file)):
            print(f"  ✓ {report_file}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
