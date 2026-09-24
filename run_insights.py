"""
Aadhaar Data Insights Analysis
This script analyzes Aadhaar enrolment, biometric, and demographic data to extract meaningful insights.
"""

import os
import pandas as pd
import plotly.express as px
from pathlib import Path

print("="*80)
print("AADHAAR DATA INSIGHTS ANALYSIS")
print("="*80)

# ============================================================================
# 1. Monthly Enrolment Trends
# ============================================================================
print("\n" + "="*80)
print("SECTION 1: MONTHLY ENROLMENT TRENDS")
print("="*80)

# 1. Setup paths - using local directory structure
base_dir = Path(os.getcwd())
master_dir = base_dir / "output" / "master"
output_dir = base_dir / "output" / "insights"
output_dir.mkdir(exist_ok=True, parents=True)

print(f"\nWorking directory: {base_dir}")
print(f"Master data directory: {master_dir}")
print(f"Output directory: {output_dir}")

# 2. Load the enrolment master file
enrol_master = master_dir / "enrolment_master.csv"
print(f"\nLoading enrolment data from: {enrol_master}")
df = pd.read_csv(enrol_master, dtype=str)
print(f"Loaded {len(df):,} records")

# 3. Parse date and numeric fields
print("\nParsing date and numeric fields...")
df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
for col in ["age_0_5", "age_5_17", "age_18_greater"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

# 4. Compute total enrolments
df["Total_Enrolments"] = df["age_0_5"] + df["age_5_17"] + df["age_18_greater"]
print(f"Total enrolments across all records: {df['Total_Enrolments'].sum():,}")

# 5. Aggregate by month
df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
monthly = df.groupby("month", as_index=False)["Total_Enrolments"].sum().sort_values("month")

print("\n=== Monthly Enrolment Summary ===")
print(monthly.to_string(index=False))

# 6. Plot monthly trend
print("\nGenerating monthly trend visualization...")
fig = px.line(
    monthly,
    x="month",
    y="Total_Enrolments",
    title="Monthly Aadhaar New-Enrolment Trends",
    markers=True
)
fig.update_layout(
    xaxis_title="Month",
    yaxis_title="Total Enrolments",
    template="plotly_white",
    hovermode="x unified"
)

# 7. Save interactive chart
output_html = output_dir / "enrolment_trends_monthly.html"
fig.write_html(output_html)
print(f"✓ Monthly enrolment trend chart saved to: {output_html}")

# ============================================================================
# 2. Maintenance vs. Growth Ratio by State
# ============================================================================
print("\n" + "="*80)
print("SECTION 2: MAINTENANCE VS. GROWTH RATIO BY STATE")
print("="*80)

print("\nLoading and processing datasets...\n")

# 2. Load and prepare Biometric dataset
print("[1/3] Processing Biometric data...")
bf = pd.read_csv(master_dir / "biometric_master.csv", dtype=str)
bf["bio_age_5_17"] = pd.to_numeric(bf["bio_age_5_17"], errors="coerce").fillna(0).astype(int)
bf["bio_age_17_"] = pd.to_numeric(bf["bio_age_17_"], errors="coerce").fillna(0).astype(int)
bf["Total_Biometrics"] = bf["bio_age_5_17"] + bf["bio_age_17_"]
print(f"  Total biometric updates: {bf['Total_Biometrics'].sum():,}")

# 3. Load and prepare Demographic dataset
print("[2/3] Processing Demographic data...")
df_demo = pd.read_csv(master_dir / "demographic_master.csv", dtype=str)
df_demo["demo_age_5_17"] = pd.to_numeric(df_demo["demo_age_5_17"], errors="coerce").fillna(0).astype(int)
df_demo["demo_age_17_"] = pd.to_numeric(df_demo["demo_age_17_"], errors="coerce").fillna(0).astype(int)
df_demo["Total_Demographics"] = df_demo["demo_age_5_17"] + df_demo["demo_age_17_"]
print(f"  Total demographic updates: {df_demo['Total_Demographics'].sum():,}")

# 4. Load and prepare Enrolment dataset (reuse from above)
print("[3/3] Processing Enrolment data...")
ef = pd.read_csv(master_dir / "enrolment_master.csv", dtype=str)
ef["age_0_5"] = pd.to_numeric(ef["age_0_5"], errors="coerce").fillna(0).astype(int)
ef["age_5_17"] = pd.to_numeric(ef["age_5_17"], errors="coerce").fillna(0).astype(int)
ef["age_18_greater"] = pd.to_numeric(ef["age_18_greater"], errors="coerce").fillna(0).astype(int)
ef["Total_Enrolments"] = ef["age_0_5"] + ef["age_5_17"] + ef["age_18_greater"]
print(f"  Total new enrolments: {ef['Total_Enrolments'].sum():,}")

# 5. Aggregate by state
print("\nAggregating by state...")
bio_state = bf.groupby("state", as_index=False)["Total_Biometrics"].sum()
demo_state = df_demo.groupby("state", as_index=False)["Total_Demographics"].sum()
enrol_state = ef.groupby("state", as_index=False)["Total_Enrolments"].sum()

# 6. Merge and compute ratios
print("Computing maintenance vs. growth ratios...")
df_merge = bio_state.merge(demo_state, on="state", how="outer") \
                    .merge(enrol_state, on="state", how="outer") \
                    .fillna(0)

df_merge["Maintenance"] = df_merge["Total_Biometrics"] + df_merge["Total_Demographics"]
df_merge["Growth"] = df_merge["Total_Enrolments"]

# Compute ratio (avoid division by zero)
df_merge["Maintenance_vs_Growth_Ratio"] = df_merge.apply(
    lambda row: row["Maintenance"] / row["Growth"] if row["Growth"] > 0 else None,
    axis=1
)

# 7. Sort and save
df_result = df_merge.sort_values("Maintenance_vs_Growth_Ratio", ascending=False)
output_csv = output_dir / "maintenance_growth_ratio.csv"
df_result.to_csv(output_csv, index=False)

print(f"\n✓ Results saved to: {output_csv}")
print(f"\nTotal states/territories analyzed: {len(df_result)}")
print(f"States with defined ratios: {df_result['Maintenance_vs_Growth_Ratio'].notna().sum()}")

# Display top 10 states
print("\n=== Top 10 States by Maintenance/Growth Ratio ===")
top_10 = df_result[df_result['Maintenance_vs_Growth_Ratio'].notna()].head(10)
display_cols = ['state', 'Maintenance', 'Growth', 'Maintenance_vs_Growth_Ratio']
print(top_10[display_cols].to_string(index=False))

# ============================================================================
# 3. Detailed Analysis: Top and Bottom States
# ============================================================================
print("\n" + "="*80)
print("SECTION 3: DETAILED ANALYSIS - TOP AND BOTTOM STATES")
print("="*80)

# Load the maintenance vs. growth CSV
file_path = output_dir / "maintenance_growth_ratio.csv"
print(f"\nLoading data from: {file_path}\n")
df = pd.read_csv(file_path)

# Drop undefined ratios (where Growth=0 or ratio is NaN)
df_clean = df.dropna(subset=["Maintenance_vs_Growth_Ratio"])

# Sort by ratio
df_sorted = df_clean.sort_values("Maintenance_vs_Growth_Ratio", ascending=False)

# Top five states (highest ratios - most saturated)
top5 = df_sorted.head(5)[["state", "Maintenance", "Growth", "Maintenance_vs_Growth_Ratio"]]

# Bottom five states (lowest non-zero ratios - most growth-oriented)
bottom5 = df_sorted.tail(5)[["state", "Maintenance", "Growth", "Maintenance_vs_Growth_Ratio"]]

print("="*80)
print("TOP 5 STATES BY MAINTENANCE VS. GROWTH RATIO")
print("(Highest ratios = Most saturated, maintenance-heavy states)")
print("="*80)
print(top5.to_string(index=False))

print("\n" + "="*80)
print("BOTTOM 5 STATES BY MAINTENANCE VS. GROWTH RATIO")
print("(Lowest ratios = Most growth-oriented states)")
print("="*80)
print(bottom5.to_string(index=False))

# Additional statistics
print("\n" + "="*80)
print("SUMMARY STATISTICS")
print("="*80)
print(f"Total states analyzed: {len(df_clean)}")
print(f"Mean ratio: {df_clean['Maintenance_vs_Growth_Ratio'].mean():.2f}")
print(f"Median ratio: {df_clean['Maintenance_vs_Growth_Ratio'].median():.2f}")
print(f"\nTotal Maintenance activities: {df_clean['Maintenance'].sum():,.0f}")
print(f"Total Growth (new enrolments): {df_clean['Growth'].sum():,.0f}")
print(f"Overall ratio: {df_clean['Maintenance'].sum() / df_clean['Growth'].sum():.2f}")

# ============================================================================
# 4. Month-over-Month and Quarter-over-Quarter Trend Analysis
# ============================================================================
print("\n" + "="*80)
print("SECTION 4: MONTH-OVER-MONTH AND QUARTER-OVER-QUARTER TREND ANALYSIS")
print("="*80)

# Reload enrolment data for this analysis
print(f"\nLoading data from: {master_dir / 'enrolment_master.csv'}")
df_trend = pd.read_csv(master_dir / "enrolment_master.csv", dtype=str)
df_trend["date"] = pd.to_datetime(df_trend["date"], format="%d-%m-%Y", errors="coerce")
for c in ["age_0_5","age_5_17","age_18_greater"]:
    df_trend[c] = pd.to_numeric(df_trend[c], errors="coerce").fillna(0).astype(int)
df_trend["Total_Enrolments"] = df_trend[["age_0_5","age_5_17","age_18_greater"]].sum(axis=1)

# Add month and quarter periods
print("Computing monthly and quarterly aggregations...")
df_trend["month"] = df_trend["date"].dt.to_period("M").dt.to_timestamp()
df_trend["quarter"] = df_trend["date"].dt.to_period("Q").dt.to_timestamp()

# National aggregations
monthly_trend = df_trend.groupby("month", as_index=False)["Total_Enrolments"].sum().sort_values("month")
monthly_trend["MoM_pct"] = monthly_trend["Total_Enrolments"].pct_change()

quarterly_trend = df_trend.groupby("quarter", as_index=False)["Total_Enrolments"].sum().sort_values("quarter")
quarterly_trend["QoQ_pct"] = quarterly_trend["Total_Enrolments"].pct_change()

print("\n=== National Monthly Growth Rates ===")
print(monthly_trend[["month", "Total_Enrolments", "MoM_pct"]].to_string(index=False))

print("\n=== National Quarterly Growth Rates ===")
print(quarterly_trend[["quarter", "Total_Enrolments", "QoQ_pct"]].to_string(index=False))

# Zone mapping
print("\nMapping states to geographic zones...")
zone_map = {
    "Jammu & Kashmir":"North","Himachal Pradesh":"North","Punjab":"North","Uttarakhand":"North",
    "Haryana":"North","Delhi":"North","Rajasthan":"North","Chandigarh":"North","Ladakh":"North",
    "Andhra Pradesh":"South","Karnataka":"South","Kerala":"South","Tamil Nadu":"South",
    "Telangana":"South","Puducherry":"South","Andaman And Nicobar Islands":"South","Lakshadweep":"South",
    "West Bengal":"East","Bihar":"East","Sikkim":"East","Odisha":"East","Jharkhand":"East",
    "Goa":"West","Gujarat":"West","Maharashtra":"West",
    "Dadra And Nagar Haveli":"West","Daman And Diu":"West","Dadra And Nagar Haveli And Daman And Diu":"West",
    "Madhya Pradesh":"Central","Chhattisgarh":"Central","Uttar Pradesh":"Central",
    "Assam":"Northeast","Arunachal Pradesh":"Northeast","Manipur":"Northeast",
    "Meghalaya":"Northeast","Mizoram":"Northeast","Nagaland":"Northeast","Tripura":"Northeast"
}
df_trend["state_clean"] = df_trend["state"].str.strip().str.title()
df_trend["zone"] = df_trend["state_clean"].map(zone_map).fillna("Other")

# Zone-level aggregations
zone_monthly = df_trend.groupby(["zone","month"], as_index=False)["Total_Enrolments"].sum().sort_values(["zone","month"])
zone_monthly["MoM_pct"] = zone_monthly.groupby("zone")["Total_Enrolments"].pct_change()

zone_quarterly = df_trend.groupby(["zone","quarter"], as_index=False)["Total_Enrolments"].sum().sort_values(["zone","quarter"])
zone_quarterly["QoQ_pct"] = zone_quarterly.groupby("zone")["Total_Enrolments"].pct_change()

# Generate and save interactive charts
print("\nGenerating visualizations...")

# National MoM
fig_mom_nat = px.line(monthly_trend, x="month", y="MoM_pct", 
                      title="National Month-over-Month % Change in Enrolments", 
                      markers=True)
fig_mom_nat.update_layout(yaxis_tickformat=".1%", template="plotly_white", hovermode="x unified")
mom_nat_html = output_dir / "monthly_enrolment_mom_national.html"
fig_mom_nat.write_html(mom_nat_html)
print(f"  ✓ Saved: {mom_nat_html.name}")

# Zone MoM
fig_mom_zone = px.line(zone_monthly, x="month", y="MoM_pct", color="zone",
                       title="Zone-wise Month-over-Month % Change", markers=True)
fig_mom_zone.update_layout(yaxis_tickformat=".1%", template="plotly_white", hovermode="x unified")
mom_zone_html = output_dir / "monthly_enrolment_mom_by_zone.html"
fig_mom_zone.write_html(mom_zone_html)
print(f"  ✓ Saved: {mom_zone_html.name}")

# National QoQ
fig_qoq_nat = px.line(quarterly_trend, x="quarter", y="QoQ_pct", 
                      title="National Quarter-over-Quarter % Change", markers=True)
fig_qoq_nat.update_layout(yaxis_tickformat=".1%", template="plotly_white", hovermode="x unified")
qoq_nat_html = output_dir / "quarterly_enrolment_qoq_national.html"
fig_qoq_nat.write_html(qoq_nat_html)
print(f"  ✓ Saved: {qoq_nat_html.name}")

# Zone QoQ
fig_qoq_zone = px.line(zone_quarterly, x="quarter", y="QoQ_pct", color="zone",
                       title="Zone-wise Quarter-over-Quarter % Change", markers=True)
fig_qoq_zone.update_layout(yaxis_tickformat=".1%", template="plotly_white", hovermode="x unified")
qoq_zone_html = output_dir / "quarterly_enrolment_qoq_by_zone.html"
fig_qoq_zone.write_html(qoq_zone_html)
print(f"  ✓ Saved: {qoq_zone_html.name}")

print("\n✓ Monthly and quarterly MoM/QoQ analysis complete!")

# ============================================================================
# 5. Enrollment Archetypes Clustering
# ============================================================================
print("\n" + "="*80)
print("SECTION 5: ENROLLMENT ARCHETYPES CLUSTERING")
print("="*80)

# Load enrolment data
enrol_master_arch = master_dir / "enrolment_master.csv"
print(f"\nLoading data from: {enrol_master_arch}")

# Read in chunks for memory efficiency
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go

chunk_iter = pd.read_csv(
    enrol_master_arch,
    usecols=["state","age_0_5","age_5_17","age_18_greater"],
    dtype=str,
    chunksize=200_000
)

# Aggregate child vs. adult by state
print("Aggregating child vs. adult enrolments by state...")
agg = {}
for chunk in chunk_iter:
    # Convert to numeric
    for c in ["age_0_5","age_5_17","age_18_greater"]:
        chunk[c] = pd.to_numeric(chunk[c], errors="coerce").fillna(0).astype(int)
    chunk["child"] = chunk["age_0_5"] + chunk["age_5_17"]
    chunk["adult"] = chunk["age_18_greater"]
    grp = chunk.groupby(chunk["state"].str.strip().str.title())[["child","adult"]].sum()
    for st, row in grp.iterrows():
        if st not in agg:
            agg[st] = {"child":0, "adult":0}
        agg[st]["child"] += int(row["child"])
        agg[st]["adult"] += int(row["adult"])

# Build DataFrame and compute ratio
df_arch = pd.DataFrame([
    {"state": st, "child": v["child"], "adult": v["adult"]}
    for st, v in agg.items()
])
df_arch["ratio"] = df_arch["child"] / df_arch["adult"].replace({0: np.nan})
df_arch = df_arch.dropna(subset=["ratio"]).reset_index(drop=True)

print(f"Computed child/adult ratios for {len(df_arch)} states")

# Cluster into 3 archetypes using KMeans
print("\nClustering states into enrollment archetypes...")
from sklearn.cluster import KMeans

X = df_arch[["ratio"]].values
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10).fit(X)
df_arch["cluster"] = kmeans.labels_

# Rename clusters by mean ratio order
means = df_arch.groupby("cluster")["ratio"].mean().sort_values()
mapping = {
    means.index[0]:"Adult-Heavy",
    means.index[1]:"Balanced",
    means.index[2]:"Child-Heavy"
}
df_arch["archetype"] = df_arch["cluster"].map(mapping)

# Define color scheme
color_map = {
    "Adult-Heavy": "#3498db",
    "Balanced": "#2ecc71",
    "Child-Heavy": "#e74c3c"
}

# Save results
csv_path_arch = output_dir / "state_archetypes.csv"
df_arch.to_csv(csv_path_arch, index=False)
print(f"\n✓ Saved archetype data to: {csv_path_arch}")

# Display archetype summary
print("\n=== Enrollment Archetypes Summary ===")
for arch in ["Adult-Heavy", "Balanced", "Child-Heavy"]:
    states = df_arch[df_arch["archetype"] == arch]["state"].tolist()
    avg_ratio = df_arch[df_arch["archetype"] == arch]["ratio"].mean()
    print(f"\n{arch} ({len(states)} states, avg ratio: {avg_ratio:.2f}):")
    print("  " + ", ".join(states[:5]) + ("..." if len(states) > 5 else ""))

print("\nGenerating visualizations...")

# ========== VISUALIZATION 1: Bar Chart (Original) ==========
fig_arch1 = px.bar(
    df_arch.sort_values("ratio"),
    x="state", y="ratio", color="archetype",
    title="Child-to-Adult Enrolment Ratio by State (Archetypes)",
    labels={"ratio":"Child/Adult Ratio", "state":"State"},
    color_discrete_map=color_map
)
fig_arch1.update_layout(xaxis_tickangle=45, template="plotly_white", hovermode="x unified")
html_path_arch1 = output_dir / "state_child_adult_ratio_clusters.html"
fig_arch1.write_html(html_path_arch1)
print(f"  ✓ Saved: {html_path_arch1.name}")

# ========== VISUALIZATION 2: Scatter Plot (Child vs Adult) ==========
fig_arch2 = px.scatter(
    df_arch,
    x="adult", y="child", color="archetype",
    size="ratio",
    hover_data=["state", "ratio"],
    title="Child vs Adult Enrolments by State (Archetype Clustering)",
    labels={"child":"Child Enrolments (0-17)", "adult":"Adult Enrolments (18+)"},
    color_discrete_map=color_map,
    size_max=20
)
fig_arch2.update_layout(template="plotly_white")
# Add diagonal line for reference (equal child/adult)
max_val = max(df_arch['adult'].max(), df_arch['child'].max())
fig_arch2.add_trace(go.Scatter(
    x=[0, max_val], y=[0, max_val],
    mode='lines', line=dict(dash='dash', color='gray'),
    name='Equal Ratio', showlegend=True
))
html_path_arch2 = output_dir / "archetype_scatter_child_vs_adult.html"
fig_arch2.write_html(html_path_arch2)
print(f"  ✓ Saved: {html_path_arch2.name}")

# ========== VISUALIZATION 3: Box Plot (Ratio Distribution) ==========
fig_arch3 = px.box(
    df_arch,
    x="archetype", y="ratio",
    color="archetype",
    title="Distribution of Child-to-Adult Ratios by Archetype",
    labels={"ratio":"Child/Adult Ratio", "archetype":"Enrollment Archetype"},
    color_discrete_map=color_map,
    points="all",  # Show all points
    hover_data=["state"]
)
fig_arch3.update_layout(template="plotly_white", showlegend=False)
html_path_arch3 = output_dir / "archetype_ratio_distribution.html"
fig_arch3.write_html(html_path_arch3)
print(f"  ✓ Saved: {html_path_arch3.name}")

# ========== VISUALIZATION 4: Top/Bottom States Horizontal Bar ==========
top10 = df_arch.nlargest(10, 'ratio')
bottom10 = df_arch.nsmallest(10, 'ratio')
combined = pd.concat([bottom10, top10]).reset_index(drop=True)

fig_arch4 = px.bar(
    combined,
    y="state", x="ratio",
    color="archetype",
    orientation='h',
    title="Top 10 & Bottom 10 States by Child-to-Adult Ratio",
    labels={"ratio":"Child/Adult Ratio", "state":"State"},
    color_discrete_map=color_map
)
fig_arch4.update_layout(template="plotly_white", height=600, yaxis={'categoryorder':'total ascending'})
html_path_arch4 = output_dir / "archetype_top_bottom_states.html"
fig_arch4.write_html(html_path_arch4)
print(f"  ✓ Saved: {html_path_arch4.name}")

# ========== VISUALIZATION 5: Multi-panel Summary Dashboard ==========
fig_arch5 = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        "Archetype Counts",
        "Ratio Distribution",
        "Total Enrolments by Archetype",
        "Child vs Adult Scatter"
    ),
    specs=[[{"type": "bar"}, {"type": "box"}],
           [{"type": "bar"}, {"type": "scatter"}]]
)

# Panel 1: Count of states per archetype
archetype_counts = df_arch['archetype'].value_counts().reset_index()
archetype_counts.columns = ['archetype', 'count']
for idx, row in archetype_counts.iterrows():
    fig_arch5.add_trace(
        go.Bar(x=[row['archetype']], y=[row['count']], name=row['archetype'],
               marker_color=color_map[row['archetype']], showlegend=False),
        row=1, col=1
    )

# Panel 2: Box plot of ratios
for arch in ["Adult-Heavy", "Balanced", "Child-Heavy"]:
    data = df_arch[df_arch['archetype'] == arch]['ratio']
    fig_arch5.add_trace(
        go.Box(y=data, name=arch, marker_color=color_map[arch], showlegend=False),
        row=1, col=2
    )

# Panel 3: Total enrolments by archetype
total_enrol = df_arch.groupby('archetype')[['child', 'adult']].sum().reset_index()
for arch in ["Adult-Heavy", "Balanced", "Child-Heavy"]:
    data = total_enrol[total_enrol['archetype'] == arch]
    if len(data) > 0:
        fig_arch5.add_trace(
            go.Bar(x=[arch], y=[data['child'].values[0] + data['adult'].values[0]],
                   name=arch, marker_color=color_map[arch], showlegend=False),
            row=2, col=1
        )

# Panel 4: Scatter plot
for arch in ["Adult-Heavy", "Balanced", "Child-Heavy"]:
    data = df_arch[df_arch['archetype'] == arch]
    fig_arch5.add_trace(
        go.Scatter(x=data['adult'], y=data['child'], mode='markers',
                   name=arch, marker=dict(color=color_map[arch], size=8)),
        row=2, col=2
    )

fig_arch5.update_layout(height=800, title_text="Enrollment Archetypes - Summary Dashboard", template="plotly_white")
fig_arch5.update_xaxes(title_text="Archetype", row=1, col=1)
fig_arch5.update_yaxes(title_text="Number of States", row=1, col=1)
fig_arch5.update_yaxes(title_text="Child/Adult Ratio", row=1, col=2)
fig_arch5.update_xaxes(title_text="Archetype", row=2, col=1)
fig_arch5.update_yaxes(title_text="Total Enrolments", row=2, col=1)
fig_arch5.update_xaxes(title_text="Adult Enrolments", row=2, col=2)
fig_arch5.update_yaxes(title_text="Child Enrolments", row=2, col=2)

html_path_arch5 = output_dir / "archetype_summary_dashboard.html"
fig_arch5.write_html(html_path_arch5)
print(f"  ✓ Saved: {html_path_arch5.name}")

print(f"\n✓ Enrollment archetypes analysis complete!")
print(f"Generated 5 interactive visualizations in: {output_dir}")

# ============================================================================
# Final Summary
# ============================================================================
print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
print(f"\n✓ All analyses completed successfully!")
print(f"\nOutput files saved in: {output_dir}")
print("  - enrolment_trends_monthly.html (interactive chart)")
print("  - maintenance_growth_ratio.csv (detailed data)")
print("  - monthly_enrolment_mom_national.html (MoM trends)")
print("  - monthly_enrolment_mom_by_zone.html (MoM by zone)")
print("  - quarterly_enrolment_qoq_national.html (QoQ trends)")
print("  - quarterly_enrolment_qoq_by_zone.html (QoQ by zone)")
print("  - state_archetypes.csv (enrollment archetype classifications)")
print("  - state_child_adult_ratio_clusters.html (archetype bar chart)")
print("  - archetype_scatter_child_vs_adult.html (scatter plot)")
print("  - archetype_ratio_distribution.html (box plot)")
print("  - archetype_top_bottom_states.html (top/bottom states)")
print("  - archetype_summary_dashboard.html (multi-panel dashboard)")
print("\n" + "="*80)
