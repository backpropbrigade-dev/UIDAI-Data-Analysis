import os
import glob
import pandas as pd
from datetime import datetime

# 1. Setup directories - use current directory instead of sandbox
base_dir = os.getcwd()  # Current directory where the script is located
session_dir = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
out_dir = os.path.join(base_dir, "output", session_dir)
os.makedirs(out_dir, exist_ok=True)

print(f"Working directory: {base_dir}")
print(f"Output directory: {out_dir}")

# 2. Define category patterns and dtype maps
categories = {
    "biometric": "api_data_aadhar_biometric_*.csv",
    "enrolment": "api_data_aadhar_enrolment_*.csv",
    "demographic": "api_data_aadhar_demographic_*.csv",
}

dtype_maps = {
    "biometric": {
        "date": str, "state": str, "district": str, "pincode": str,
        "bio_age_5_17": "Int64", "bio_age_17_": "Int64"
    },
    "enrolment": {
        "date": str, "state": str, "district": str, "pincode": str,
        "age_0_5": "Int64", "age_5_17": "Int64", "age_18_greater": "Int64"
    },
    "demographic": {
        "date": str, "state": str, "district": str, "pincode": str,
        "demo_age_5_17": "Int64", "demo_age_17_": "Int64"
    }
}

# 3. Build manifest and load/concatenate
manifest_records = []
master_dfs = {}

print("\nProcessing datasets...")
print("=" * 80)

for cat, pattern in categories.items():
    print(f"\nCategory: {cat.upper()}")
    print("-" * 80)
    
    # discover files
    file_paths = sorted(glob.glob(os.path.join(base_dir, pattern)))
    
    if not file_paths:
        print(f"  ⚠ No files found for pattern: {pattern}")
        continue
    
    print(f"  Found {len(file_paths)} file(s):")
    
    dfs = []
    total_rows = 0
    
    for fp in file_paths:
        # Get file size
        file_size = os.path.getsize(fp)
        file_size_mb = file_size / (1024 * 1024)
        
        # count rows (minus header)
        with open(fp, 'r', encoding='utf-8') as f:
            row_count = sum(1 for _ in f) - 1
        
        print(f"    - {os.path.basename(fp)}: {row_count:,} rows, {file_size_mb:.2f} MB")
        
        manifest_records.append({
            "category": cat,
            "filename": os.path.basename(fp),
            "file_path": fp,
            "row_count": row_count,
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size_mb, 2)
        })
        total_rows += row_count
        
        # read chunk
        df_chunk = pd.read_csv(fp, dtype=dtype_maps[cat])
        dfs.append(df_chunk)
    
    # concatenate master DataFrame
    if dfs:
        df_master = pd.concat(dfs, ignore_index=True)
        actual_rows = len(df_master)
        
        # verify counts
        assert actual_rows == total_rows, (
            f"Row count mismatch for {cat}: expected {total_rows}, got {actual_rows}"
        )
        
        print(f"\n  ✓ Total rows for {cat}: {actual_rows:,}")
        print(f"  ✓ Columns: {', '.join(df_master.columns.tolist())}")
        
        # save master
        master_filename = f"{cat}_master.csv"
        master_path = os.path.join(out_dir, master_filename)
        df_master.to_csv(master_path, index=False)
        print(f"  ✓ Saved master file: {master_filename}")
        
        master_dfs[cat] = df_master

# 4. Save manifest
print("\n" + "=" * 80)
print("Creating manifest...")

if manifest_records:
    manifest_df = pd.DataFrame(manifest_records)
    manifest_path = os.path.join(out_dir, "manifest.csv")
    manifest_df.to_csv(manifest_path, index=False)
    
    # Print summary
    print(f"\n✓ Manifest created with {len(manifest_records)} file(s)")
    print(f"✓ Total categories processed: {len(master_dfs)}")
    print(f"\nSummary by category:")
    summary = manifest_df.groupby('category').agg({
        'row_count': 'sum',
        'file_size_mb': 'sum',
        'filename': 'count'
    }).rename(columns={'filename': 'file_count'})
    print(summary)
    
    print(f"\n✓ All files saved to: {out_dir}")
    print(f"  - Manifest: manifest.csv")
    for cat in master_dfs.keys():
        print(f"  - Master file: {cat}_master.csv")
else:
    print("⚠ No datasets found to process!")

print("\n" + "=" * 80)
print("✓ Processing complete!")
