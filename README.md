# 🔍 Aadhaar Data Insights Analysis

> **Unlocking India's Digital Identity Patterns Through Data Science**  
> A comprehensive analysis of 260+ million Aadhaar enrollment and update transactions using machine learning and predictive analytics to optimize resource allocation and enhance citizen experience.

[![UIDAI Data Hackathon 2026](https://img.shields.io/badge/Hackathon-UIDAI%202026-blue)](https://uidai.gov.in)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Hackathon%20Submission-orange)](LICENSE)


Report:(https://aadhaar-data-hackathon.vercel.app)

---

## 🎯 Repository Description

**Short Description:**  
*Machine learning-powered analysis of Aadhaar enrollment patterns across 39 states, revealing strategic insights through demographic clustering, temporal forecasting, and geographic segmentation.*

**Detailed Description:**  
This project analyzes 260+ million Aadhaar transactions (enrollments, biometric updates, and demographic changes) from March-December 2025 to derive actionable insights for India's digital identity infrastructure. Using K-Means clustering, we discover distinct "enrollment archetypes" across states, while predictive models forecast demand patterns. The analysis spans 7 dimensions—from seasonal trends to age-cohort behaviors—delivering data-driven recommendations for policymakers and system administrators.

**Tags:** `aadhaar` `data-analysis` `machine-learning` `india` `uidai` `kmeans-clustering` `predictive-analytics` `jupyter-notebook` `plotly` `data-visualization`

---

## ✨ Project Highlights

🔬 **260M+ Transactions Analyzed** — Comprehensive analysis of enrollment, biometric, and demographic updates  
🎯 **K-Means Clustering** — Discovered 3 distinct enrollment archetypes across 39 states  
📈 **Predictive Modeling** — 85-90% accuracy in forecasting daily enrollment demand  
🗺️ **Geographic Segmentation** — Zone-based analysis revealing regional patterns  
📊 **13 Interactive Visualizations** — Plotly-powered HTML dashboards for insights  
⚡ **End-to-End Pipeline** — From raw data cleaning to actionable recommendations

---

## 📋 Problem Statement and Approach

### Problem Statement
Analyze Aadhaar enrollment and update data to extract actionable insights that can optimize resource allocation, improve service delivery, and enhance citizen experience across India's digital identity infrastructure.

### Analytical Approach
Our multi-dimensional analysis framework addresses three core objectives:

1. **Temporal Analysis**: Identify enrollment patterns, seasonal trends, and growth dynamics to forecast future demand
2. **Geographic Segmentation**: Profile state-level system maturity and classify regions based on enrollment behavior
3. **Predictive Modeling**: Build machine learning models to enable data-driven resource planning

**Key Innovation**: We apply unsupervised learning (K-Means clustering) to discover natural groupings of states based on child-to-adult enrollment ratios, revealing distinct "enrollment archetypes" that inform tailored policy interventions.

---

## 📊 Datasets Used

### Primary Datasets (UIDAI Provided)

#### 1. **Enrolment Dataset** (`enrolment_master.csv`)
Captures new Aadhaar registrations across India.

| Column | Description | Data Type |
|--------|-------------|-----------|
| `date` | Transaction date (DD-MM-YYYY) | String → DateTime |
| `state` | State/Union Territory name | String |
| `district` | District name | String |
| `pincode` | 6-digit area code | String |
| `age_0_5` | New enrollments age 0-5 years | String → Integer |
| `age_5_17` | New enrollments age 5-17 years | String → Integer |
| `age_18_greater` | New enrollments age 18+ years | String → Integer |

**Total Records**: ~5.4 million new enrollments  
**Time Period**: March - December 2025 (10 months)

#### 2. **Biometric Update Dataset** (`biometric_master.csv`)
Tracks fingerprint/iris re-capture activities (mandatory 10-year renewals).

| Column | Description | Data Type |
|--------|-------------|-----------|
| `date` | Update date (DD-MM-YYYY) | String → DateTime |
| `state` | State/Union Territory | String |
| `district` | District name | String |
| `pincode` | Area code | String |
| `bio_age_5_17` | Biometric updates age 5-17 | String → Integer |
| `bio_age_17_` | Biometric updates age 18+ | String → Integer |

**Total Records**: ~175 million biometric updates

#### 3. **Demographic Update Dataset** (`demographic_master.csv`)
Captures address, phone, and other non-biometric changes (often self-service).

| Column | Description | Data Type |
|--------|-------------|-----------|
| `date` | Update date | String → DateTime |
| `state` | State/Union Territory | String |
| `district` | District name | String |
| `pincode` | Area code | String |
| `demo_age_5_17` | Demographic updates age 5-17 | String → Integer |
| `demo_age_17_` | Demographic updates age 18+ | String → Integer |

**Total Records**: ~80 million demographic updates

### Dataset Characteristics
- **Geographic Coverage**: 39 states and union territories
- **Temporal Granularity**: Daily transaction-level data
- **Age Segmentation**: Three cohorts (0-5, 5-17, 18+)
- **Spatial Granularity**: State → District → Pincode hierarchy

---

## 🔧 Methodology

### 1. Data Cleaning and Preprocessing

#### Date Standardization
```python
df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
```
- Converted DD-MM-YYYY strings to datetime objects
- Handled malformed dates with coercion to NaT

#### Type Casting and Validation
```python
for col in ['age_0_5', 'age_5_17', 'age_18_greater']:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
```
- Numeric columns parsed from string format
- Invalid values coerced to NaN, then filled with 0
- Ensured integer data types for aggregation

#### Geographic Normalization
```python
df['state_clean'] = df['state'].str.strip().str.title()
```
- Removed leading/trailing whitespace
- Standardized capitalization for consistent grouping

### 2. Feature Engineering

#### Temporal Features
- **Monthly Aggregation**: `df['month'] = df['date'].dt.to_period('M').dt.to_timestamp()`
- **Quarterly Aggregation**: `df['quarter'] = df['date'].dt.to_period('Q').dt.to_timestamp()`
- **Day of Week**: `df['dow'] = df['date'].dt.dayofweek` (for forecasting models)

#### Derived Metrics
- **Total Enrollments**: `age_0_5 + age_5_17 + age_18_greater`
- **Maintenance Activity**: `biometric_updates + demographic_updates`
- **Maintenance/Growth Ratio**: `Maintenance ÷ Growth` (system maturity indicator)
- **Child/Adult Ratio**: `(age_0_5 + age_5_17) ÷ age_18_greater` (archetype classification)

#### Time-Series Features (for Predictions)
- **Lag Features**: `lag_1` (yesterday), `lag_7` (same day last week)
- **Rolling Statistics**: 7-day moving average
- **Seasonality**: One-hot encoded day-of-week

#### Geographic Zoning
Mapped 39 states/UTs into 6 geographic zones for regional analysis:
- **North**: J&K, HP, Punjab, Uttarakhand, Haryana, Delhi, Rajasthan, Chandigarh, Ladakh
- **South**: AP, Karnataka, Kerala, Tamil Nadu, Telangana, Puducherry, A&N, Lakshadweep
- **East**: West Bengal, Bihar, Sikkim, Odisha, Jharkhand
- **West**: Goa, Gujarat, Maharashtra, Dadra & Nagar Haveli, Daman & Diu
- **Central**: Madhya Pradesh, Chhattisgarh, Uttar Pradesh
- **Northeast**: Assam, Arunachal Pradesh, Manipur, Meghalaya, Mizoram, Nagaland, Tripura

### 3. Analytical Methods

#### 3.1 Descriptive Statistics
- Monthly/quarterly aggregation using `groupby()`
- Percentage change calculations for growth rates
- Top/bottom state identification via ranking

#### 3.2 Unsupervised Learning (K-Means Clustering)
```python
from sklearn.cluster import KMeans
X = df[['ratio']].values
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
df['cluster'] = kmeans.fit_predict(X)
```
- **Purpose**: Classify states into enrollment archetypes
- **Features**: Child-to-Adult enrollment ratio
- **Algorithm**: K-Means (k=3)
- **Output**: Adult-Heavy, Balanced, Child-Heavy categories

#### 3.3 Predictive Modeling (Linear Regression)
```python
from sklearn.linear_model import LinearRegression
model = LinearRegression()
model.fit(X_train, y_train)
```
- **Target**: Next-day enrollment volume
- **Features**: Lag variables, rolling averages, day-of-week
- **Performance**: R² ≈ 0.85-0.90

### 4. Data Transformation Pipeline

**Stage 1: Load** → Read CSVs with `dtype=str` for safety  
**Stage 2: Clean** → Date parsing, type casting, missing value handling  
**Stage 3: Aggregate** → Group by time/geography, compute totals  
**Stage 4: Engineer** → Create derived features and metrics  
**Stage 5: Analyze** → Apply statistical/ML methods  
**Stage 6: Visualize** → Generate interactive Plotly charts  

---

## 📈 Data Analysis and Visualisation

### Analysis Framework: 7 Dimensions

#### 1. **Monthly Enrollment Trends**
**Key Findings**:
- **Peak Month**: September 2025 (4.43M enrollments - 39% of Q3)
- **Growth Pattern**: Exponential acceleration Mar→Sep, followed by Q4 stabilization
- **Seasonal Driver**: School enrollment season + festival preparations

**Visualization**: [`enrolment_trends_monthly.html`](output/insights/enrolment_trends_monthly.html)
- Interactive line chart with markers
- Monthly totals and trend line
- Hover tooltips for precise values

#### 2. **Maintenance vs Growth Ratio (System Maturity)**
**Key Findings**:
- **National Average Ratio**: ~25-30 (mature system overall)
- **Most Saturated**: Daman & Diu (124.3), A&N Islands (58.5), Chandigarh (49.5)
- **Highest Growth**: Meghalaya (1.2), Assam (6.4), Nagaland (7.7)
- **Pattern**: UTs and Southern states saturated; Northeastern states expanding

**Visualization**: [`maintenance_growth_ratio.csv`](output/insights/maintenance_growth_ratio.csv)
- State-level ratios with components (maintenance, growth)
- Ranked by maturity indicator

**Interpretation**:
- Ratio > 40 → Focus on update efficiency
- Ratio < 5 → Prioritize new enrollment infrastructure

#### 3. **Top & Bottom States Deep Dive**
**Key Findings**:
- **Statistical Summary**: Mean ratio 25-30, high variance (σ large)
- **Size Effect**: Smaller states/UTs reach saturation faster
- **Geographic Influence**: Island/remote areas show distinct patterns

**Visualization**: Console output with formatted tables

#### 4. **Month-over-Month & Quarter-over-Quarter Trends**
**Key Findings**:
- **Highest MoM Growth**: April (+1,452%), July (+186%), September (+139%)
- **Regional Leaders**: Central Zone drives national trends (UP, MP dominant)
- **Zonal Patterns**: Northeast highest growth rates; South most stable

**Visualizations** (4 files):
1. [`monthly_enrolment_mom_national.html`](output/insights/monthly_enrolment_mom_national.html) - National MoM %
2. [`monthly_enrolment_mom_by_zone.html`](output/insights/monthly_enrolment_mom_by_zone.html) - Zone MoM comparison
3. [`quarterly_enrolment_qoq_national.html`](output/insights/quarterly_enrolment_qoq_national.html) - National QoQ %
4. [`quarterly_enrolment_qoq_by_zone.html`](output/insights/quarterly_enrolment_qoq_by_zone.html) - Zone QoQ comparison

#### 5. **Enrollment Archetypes (Machine Learning)**
**Method**: K-Means clustering (k=3) on child/adult enrollment ratio

**Key Findings**:
- **Adult-Heavy** (31 states, avg ratio 29.5): Kerala, Gujarat, Karnataka
  - Mature systems, focus on biometric renewals
  - Policy: Digital-first demographic updates
  
- **Balanced** (8 states, avg ratio 85.8): Andhra Pradesh, Haryana, Jharkhand
  - Demographic transition states
  - Policy: Hybrid service models
  
- **Child-Heavy** (4 states, avg ratio 180.5): Tamil Nadu, Odisha, Lakshadweep
  - Young populations, school-based drives
  - Policy: School partnerships, birth certificate integration

**Visualizations** (5 files):
1. [`state_child_adult_ratio_clusters.html`](output/insights/state_child_adult_ratio_clusters.html) - Bar chart by state
2. [`archetype_scatter_child_vs_adult.html`](output/insights/archetype_scatter_child_vs_adult.html) - Scatter plot with reference line
3. [`archetype_ratio_distribution.html`](output/insights/archetype_ratio_distribution.html) - Box plots by archetype
4. [`archetype_top_bottom_states.html`](output/insights/archetype_top_bottom_states.html) - Top/Bottom 10 comparison
5. [`archetype_summary_dashboard.html`](output/insights/archetype_summary_dashboard.html) - 4-panel overview

#### 6. **Update Intensity per Age Cohort**
**Key Findings**:
- **Children (5-17)**:
  - 91.5% biometric, 8.5% demographic (10.8:1 ratio)
  - Physical center-dependent, compliance-driven
  
- **Adults (18+)**:
  - 55.4% biometric, 44.6% demographic (1.24:1 ratio)
  - Self-service preference, digital literacy evident

**Strategic Insight**: Dual-track service model needed - physical infrastructure for children, digital-first for adults

#### 7. **Predictive Analytics**
**7.1 Daily Enrollment Forecasting**
- **Model**: Linear Regression with time-series features
- **Performance**: R² ≈ 0.85-0.90
- **Features**: lag_1, lag_7, rolling_mean_7, day_of_week
- **Business Value**: Optimize staffing, server capacity, appointment slots

**Operational Impact**:
- Proactive resource allocation
- Prevent queue build-up
- Reduce operational costs

### Visualization Suite Summary

**Total Output Files**: 13

| Category | Files |
|----------|-------|
| **Temporal Trends** | 5 HTML (monthly trend, 4 MoM/QoQ) |
| **Maturity Analysis** | 1 CSV (maintenance ratios) |
| **Archetypes** | 5 HTML + 1 CSV (clustering visualizations) |
| **Summary** | 1 MD (consolidated insights) |

**Technology Stack**:
- **Visualization**: Plotly (interactive HTML charts)
- **Analysis**: Pandas, NumPy, scikit-learn
- **Documentation**: Jupyter Notebook + Python scripts

---

## 🎯 Key Insights Summary

### Strategic Recommendations

#### Short-Term (0-6 months)
1. Document September success factors for replication
2. Investigate August data gap (quality assurance)
3. Pilot mobile biometric units in top 5 saturated states

#### Medium-Term (6-18 months)
1. Deploy zone-specific strategies leveraging regional patterns
2. Scale school-based enrollment in child-heavy states
3. Implement enrollment forecasting system nationwide

#### Long-Term (18+ months)
1. Develop proactive lifecycle management system
2. Digital-first update platform for adult-heavy states
3. Equity-focused acceleration in growth states

### Impact Delivered
- ✅ **Data-driven policy framework** for resource allocation
- ✅ **Predictive capabilities** for demand forecasting
- ✅ **Geographic segmentation** for targeted interventions
- ✅ **Behavioral insights** for service design optimization

---

## 📁 Project Structure

```plaintext
DataHackathon/
│
├── 📊 Data Processing Pipeline
│   ├── clean_datasets.py              # Initial data cleaning & validation
│   ├── impute_missing_data.py         # Missing value handling & imputation
│   ├── aggregate_and_engineer.py      # Feature engineering & aggregations
│   └── process_datasets.py            # Master workflow orchestrator
│
├── 🔬 Analysis Scripts
│   ├── insights.ipynb                 # Main analysis notebook (7 sections)
│   ├── run_insights.py                # Standalone Python script version
│   └── main.ipynb                     # Exploratory analysis notebook
│
├── 📈 Visualization & Reporting
│   ├── capture_visualizations.py      # Screenshot automation for reports
│   ├── report.tex                     # LaTeX report template
│   └── report.html                    # Rendered HTML report
│
├── 📂 Data & Outputs
│   ├── Datasets/                      # Raw data (gitignored)
│   │   ├── enrolment_master.csv
│   │   ├── biometric_master.csv
│   │   └── demographic_master.csv
│   │
│   └── output/
│       ├── master/                    # Cleaned master datasets
│       └── insights/                  # Analysis outputs (13 files)
│           ├── *.html                 # Interactive Plotly visualizations
│           ├── *.csv                  # Processed data tables
│           └── summary_report.md      # Consolidated insights
│
├── 📄 Documentation
│   ├── README.md                      # This file
│   ├── PDF_GENERATION_GUIDE.md        # LaTeX to PDF instructions
│   └── ADD_VISUALIZATIONS_GUIDE.md    # How to add new analyses
│
└── ⚙️ Configuration
    └── .gitignore                     # Version control configuration
```

### Key Files Description

| File | Purpose | Output |
|------|---------|--------|
| `insights.ipynb` | Complete 7-dimensional analysis | 13 visualization files |
| `run_insights.py` | Non-interactive version of analysis | Same as notebook |
| `aggregate_and_engineer.py` | Feature engineering pipeline | Enriched datasets |
| `report.tex` | Professional LaTeX report | PDF documentation |

---

## 🚀 Quick Start

### Prerequisites

Ensure you have Python 3.8+ installed, then install dependencies:

```bash
pip install pandas numpy plotly scikit-learn jupyter
```

### Option 1: Run Complete Analysis (Recommended)

**Using Jupyter Notebook:**
```bash
jupyter notebook insights.ipynb
```
Run cells sequentially. All outputs save to `output/insights/`.

**Using Python Script:**
```bash
python run_insights.py
```
Generates all 13 output files automatically in `output/insights/`.

### Option 2: Run Data Pipeline Only

Process raw datasets through the complete cleaning and feature engineering pipeline:

```bash
# Step 1: Clean raw data
python clean_datasets.py

# Step 2: Handle missing values
python impute_missing_data.py

# Step 3: Aggregate and engineer features
python aggregate_and_engineer.py
```

### Option 3: Generate Report

Create a professional PDF report from the LaTeX template (requires LaTeX installation):

```bash
# See detailed instructions in:
cat PDF_GENERATION_GUIDE.md
```

### Expected Outputs

After running the analysis, you'll find:
- **13 HTML files** in `output/insights/` (interactive visualizations)
- **2 CSV files** with cluster analysis results
- **1 markdown summary** with key findings

### Troubleshooting

**Issue**: Missing datasets  
**Solution**: Ensure `Datasets/` folder contains the three master CSV files from UIDAI

**Issue**: Import errors  
**Solution**: Verify all dependencies are installed: `pip list | grep -E "pandas|numpy|plotly|scikit"` (or `findstr` on Windows)

---

## 👥 Team & Acknowledgments

### Team Members

- **Glen Elric Fernandes** - Data Science & Machine Learning
- **Reoney Iral Madtha** - Data Engineering & Visualization

### Hackathon Details

| Detail | Value |
|--------|-------|
| **Event** | UIDAI Data Hackathon 2026 |
| **Dataset Provider** | Unique Identification Authority of India (UIDAI) |
| **Analysis Period** | March - December 2025 (10 months) |
| **Submission Date** | January 2026 |
| **Data Volume** | 260+ million transactions |

### Acknowledgments

We thank UIDAI for providing this invaluable dataset and organizing the hackathon to drive data-driven insights for India's digital identity infrastructure. This analysis aims to contribute meaningful recommendations for improving Aadhaar service delivery nationwide.

---

## 📄 License

This analysis is submitted as part of the UIDAI Data Hackathon 2026. All datasets remain property of UIDAI. Analysis code and insights are provided for evaluation purposes.

---

**For questions or further details, please refer to the comprehensive analysis in `insights.ipynb`.**
