# The System Is Improving. But Are People?

> A Detective Arc Investigation into Australia's Economic Reality  
> **AT3 Group 3 - UTS Data Visualisation & Narratives**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://group3-australia-economic-narrative.streamlit.app)

---

## Overview

This interactive dashboard investigates whether Australia's strong macro-economic growth is translating into real improvements in household living standards. Built for **Paula**, Senior Economic Policy Advisor at Federal Treasury, the dashboard follows a five-scene detective arc, moving from surface-level indicators to a defensible policy recommendation.

**Live Dashboard:** https://group3-australia-economic-narrative.streamlit.app  
**GitHub:** https://github.com/VivvekRai/DVN-AT3-Group3

---

## Narrative Structure

| Scene | Title | Key Finding |
|-------|-------|-------------|
| 1 | The Crime Scene | GDP grew +0.8% but per capita hit -0.2% in Jun-2024 |
| 2 | The Red Herring | +639k jobs added - but employment ≠ wage adequacy |
| 3 | The Culprit Revealed | Real wages turned -0.23% in Dec-2025 - first time ever |
| 4 | The Deeper Motive | Perth CPI highest nationally at 0.93% avg quarterly |
| 5 | The Verdict | Housing CPI rising 1.7× faster than overall CPI |

**Recommendation:** Target housing-specific interventions (supply, rent controls, mortgage relief) - not broad economic stimulus.

---

## Data Dictionary

All variables used in the dashboard and engineered features are documented below.

### Source Datasets

| Dataset | ABS Catalogue | File | Coverage |
|---------|--------------|------|----------|
| National Accounts | Cat. 5206 | `01b_GDP_quarterly_2020_2025.csv` | 2024-Q1 to 2025-Q4 |
| Labour Force | Cat. 6202 | `02_LabourForce_6202_T1_mar2026.xlsx` | Jan-2024 to Mar-2026 |
| Wage Price Index | Cat. 6345 | `03_WPI_6345_T1_dec2025.xlsx` | Mar-2024 to Dec-2025 |
| CPI Monthly | Cat. 6401 Table 1 | `04a_CPI_monthly_australia.xlsx` | Jan-2024 to Nov-2025 |
| CPI by City | Cat. 6401 Table 8 | `04b_CPI_by_city_quarterly.xlsx` | Mar-2024 to Dec-2025 |
| CPI Housing | Cat. 6401 Table 9 | `04c_CPI_housing_quarterly.xlsx` | Mar-2024 to Mar-2026 |

---

### Master File: `master_quarterly_enriched.csv`

| Variable | Type | Description | Source | ABS Series ID |
|----------|------|-------------|--------|---------------|
| `period` | string | Quarter label e.g. `2024-Q1` | Derived | - |
| `date` | datetime | Quarter end date | Derived | - |
| `gdp_growth_pct` | float | Quarterly GDP growth % (chain volume) | ABS 5206 | A2304418T |
| `gdp_per_capita_growth_pct` | float | GDP growth minus population growth % | Engineered | - |
| `employed_total_sa` | float | Total employed persons (000s), seasonally adjusted | ABS 6202 | A84423043C |
| `unemployment_rate_sa` | float | Unemployment rate %, seasonally adjusted | ABS 6202 | A84423050A |
| `participation_rate_sa` | float | Participation rate %, seasonally adjusted | ABS 6202 | A84423051C |
| `labour_force_sa` | float | Total labour force (000s), seasonally adjusted | ABS 6202 | A84423047L |
| `wpi_index_sa` | float | Wage Price Index (all sectors), seasonally adjusted | ABS 6345 | A2713849C |
| `wpi_pct_change_qoq_sa` | float | WPI quarter-on-quarter % change, SA | ABS 6345 | A83895395V |
| `wpi_pct_change_yoy_sa` | float | WPI year-on-year % change, SA | ABS 6345 | A83895396W |
| `cpi_index_australia` | float | CPI index number, all groups, Australia | ABS 6401 | - |
| `cpi_pct_australia` | float | CPI quarterly % change, all groups, Australia | ABS 6401 Table 1 | - |
| `cpi_pct_sydney` | float | CPI quarterly % change, Sydney | ABS 6401 Table 8 | - |
| `cpi_pct_melbourne` | float | CPI quarterly % change, Melbourne | ABS 6401 Table 8 | - |
| `cpi_pct_brisbane` | float | CPI quarterly % change, Brisbane | ABS 6401 Table 8 | - |
| `cpi_pct_adelaide` | float | CPI quarterly % change, Adelaide | ABS 6401 Table 8 | - |
| `cpi_pct_perth` | float | CPI quarterly % change, Perth | ABS 6401 Table 8 | - |
| `cpi_pct_hobart` | float | CPI quarterly % change, Hobart | ABS 6401 Table 8 | - |
| `cpi_pct_darwin` | float | CPI quarterly % change, Darwin | ABS 6401 Table 8 | - |
| `cpi_pct_canberra` | float | CPI quarterly % change, Canberra | ABS 6401 Table 8 | - |
| `housing_cpi_index` | float | Housing group CPI index, Australia | ABS 6401 Table 9 | A2325981V |
| `housing_cpi_pct_change` | float | Housing CPI quarterly % change | ABS 6401 Table 9 | - |
| `real_wage_growth` | float | **[Engineered]** WPI YoY % minus CPI YoY % | Engineered | - |
| `employment_growth_pct` | float | **[Engineered]** Month-on-month employed total % change | Engineered | - |
| `cpi_cumulative_pct` | float | **[Engineered]** Compounded CPI rise since Mar-2024 baseline | Engineered | - |
| `housing_vs_cpi_ratio` | float | **[Engineered]** Housing CPI pct / Overall CPI pct | Engineered | - |
| `housing_cpi_yoy` | float | **[Engineered]** Housing CPI annual % change (index-derived) | Engineered | - |
| `housing_vs_overall_yoy_gap` | float | **[Engineered]** Housing YoY minus Overall CPI YoY | Engineered | - |
| `cpi_yoy_quarterly` | float | **[Engineered]** CPI YoY derived from quarterly index | Engineered | - |

---

### Supplementary Files

#### `labour_cleaned.csv`
Monthly labour force data, Jan-2024 to Mar-2026.

| Variable | Type | Description |
|----------|------|-------------|
| `date` | datetime | Month end date |
| `employed_total_sa` | float | Total employed (000s), SA |
| `unemployment_rate_sa` | float | Unemployment rate %, SA |
| `participation_rate_sa` | float | Participation rate %, SA |
| `labour_force_sa` | float | Labour force total (000s), SA |

#### `cpi_by_city_cleaned.csv`
Quarterly CPI % change for 8 capital cities, Mar-2024 to Dec-2025.

| Variable | Type | Description |
|----------|------|-------------|
| `date` | datetime | Quarter end date |
| `cpi_pct_{city}` | float | Quarterly CPI % change for each capital city |
| `cpi_pct_australia` | float | National quarterly CPI % change |

#### `housing_cpi_yoy.csv`
Annual housing CPI % change, derived from quarterly index.

| Variable | Type | Description |
|----------|------|-------------|
| `date` | datetime | Quarter end date |
| `housing_cpi_yoy` | float | Housing CPI YoY % (index_t / index_t-4 - 1) × 100 |

#### `cpi_yoy_quarterly_australia.csv`
Annual CPI % change, derived from quarterly index.

| Variable | Type | Description |
|----------|------|-------------|
| `date` | datetime | Quarter end date |
| `cpi_yoy_quarterly` | float | CPI YoY % (index_t / index_t-4 - 1) × 100 |

#### `city_coordinates.csv`
Geographic coordinates for the interactive Australia map.

| Variable | Type | Description |
|----------|------|-------------|
| `city` | string | Capital city name |
| `latitude` | float | Latitude coordinate |
| `longitude` | float | Longitude coordinate |

---

### Engineered Features - Formulas

| Feature | Formula | Result (Latest) |
|---------|---------|-----------------|
| `real_wage_growth` | `WPI YoY % − CPI YoY %` | -0.23% (Dec-2025) |
| `employment_growth_pct` | `(employed_t − employed_t-1) / employed_t-1 × 100` | +0.3% (Mar-2026) |
| `cpi_cumulative_pct` | `[(1+r1)×(1+r2)×…×(1+rn) − 1] × 100` | +7.4% (Mar-2026) |
| `housing_vs_cpi_ratio` | `housing_cpi_pct_change / cpi_pct_australia` | 1.17× (avg) |
| `housing_cpi_yoy` | `(housing_index_t / housing_index_t-4 − 1) × 100` | +7.15% (Mar-2026) |
| `housing_vs_overall_yoy_gap` | `housing_cpi_yoy − cpi_yoy_quarterly` | +3.06pp (Mar-2026) |

---

### Known Limitations

| Issue | Detail |
|-------|--------|
| Mar-2026 WPI NaN | ABS had not released WPI for Mar-2026 at time of collection. Dashboard uses `dropna().iloc[-1]` to handle. |
| CPI YoY pre-mid-2025 NaN | Requires 4 quarters of history. Fixed via index-based derivation. |
| `housing_cpi_contribution` | This column (~22%) represents basket weight, NOT contribution to inflation change. Not used in dashboard metrics. |
| Seasonal adjustment | All labour force and WPI figures use ABS seasonally adjusted series for policy-appropriate trend analysis. |

---

## How to Run

```bash
# Clone the repo
git clone https://github.com/VivvekRai/DVN-AT3-Group3.git
cd DVN-AT3-Group3

# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run app.py
```

### Requirements
```
streamlit
plotly
pandas
numpy
```

---

## Folder Structure

```
DVN-AT3-Group3/
├── app.py                          # Main Streamlit dashboard
├── requirements.txt                # Python dependencies
├── master_quarterly_enriched.csv   # Main enriched dataset (31 cols)
├── labour_cleaned.csv              # Monthly labour force data
├── cpi_by_city_cleaned.csv         # Quarterly CPI by city
├── cpi_monthly_australia_cleaned.csv # Monthly CPI Australia
├── cpi_yoy_quarterly_australia.csv # Derived CPI YoY
├── housing_cpi_yoy.csv             # Derived housing CPI YoY
├── gdp_cleaned.csv                 # Cleaned GDP data
├── wpi_cleaned.csv                 # Cleaned WPI data
├── cpi_housing_cleaned.csv         # Housing CPI group data
└── city_coordinates.csv            # Lat/long for map
```

---

## Dashboard Features

| Feature | Description |
|---------|-------------|
| What-If Sliders | Model wage and CPI scenarios - projects real wage outcome live |
| City Map Filter | Click any capital city to filter Scene 4 CPI comparison |
| 5-Scene Detective Arc | Progressive narrative from crime to verdict |
| Dark/Light Mode | Fully adaptive to Streamlit theme |
| Mobile Responsive | Works on desktop and mobile |
| Paula's Instant Brief | 4 key economic KPIs always visible at top |

---

## Credits

### Group 3 - UTS Data Visualisation & Narratives (AT3)

| Name | Student ID | Role | Contribution |
|------|-----------|------|-------------|
| **Maximus Chandrasekaran** | 25614189 | Story Lead | Narrative arc design, detective storyline, scene framing |
| **Xin Yiing Loo** | 26178069 | Data Sourcing Lead | ABS dataset identification, download, and initial inventory |
| **Vivek Rai** | 25731011 | Data Engineering Lead | Data cleaning, feature engineering, dashboard deployment |
| **Keerthika Bottu** | 25177698 | Visual Design Lead | Colour palette, typography, layout design direction |
| **Jayesh Kumar** | 26024327 | Visualisation Builder | Scene construction, Plotly implementation |
| **Vishwesh Kalyam** | 25424211 | Research Lead | Economic context, policy framing, ABS verification |
| **Harsh Vikas Gupta** | 26181091 | Pitch Narrator | Presentation script, verbal delivery, stakeholder framing |

---

### Data Sources

All data sourced from the **Australian Bureau of Statistics (ABS)** - Australia's official national statistical agency.

| Dataset | Catalogue | URL |
|---------|-----------|-----|
| National Accounts - GDP | Cat. 5206 | https://www.abs.gov.au/statistics/economy/national-accounts/australian-national-accounts-national-income-expenditure-and-product |
| Labour Force | Cat. 6202 | https://www.abs.gov.au/statistics/labour/employment-and-unemployment/labour-force-australia |
| Wage Price Index | Cat. 6345 | https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/wage-price-index-australia |
| Consumer Price Index | Cat. 6401 | https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia |

---

### Tools & Technologies

| Tool | Purpose |
|------|---------|
| Python 3.12 | Data engineering and dashboard |
| Streamlit | Interactive web dashboard framework |
| Plotly | Interactive charts and visualisations |
| Pandas | Data cleaning, transformation, and analysis |
| NumPy | Numerical computations and feature engineering |
| GitHub | Version control and collaboration |
| Streamlit Cloud | Free hosting and deployment |

---

### Acknowledgements

- **Australian Bureau of Statistics** for publicly available, high-quality economic datasets
- **UTS Faculty of Engineering and IT** for the Data Visualisation & Narratives course framework
- **Streamlit** for the open-source dashboard framework

---

##  License

This project is for educational purposes as part of the UTS AT3 assessment. Data sourced from ABS is used under ABS data licensing terms.

---

*Built by Group 3 | Data Visualisation & Narratives | Autumn 2026*
