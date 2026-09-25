# YouTube Channel Growth Intelligence Platform

A production-grade, algorithmic intelligence platform for analyzing YouTube channel growth, audience retention decay curves, video packaging, traffic sources, and machine learning performance forecasting. 

Engineered strictly in compliance with the **YouTube API Services Developer Policies (Section III.E.4.b–d)**, incorporating an automated 30-day data retention TTL sweeper, dimension-group-aware normalization, and zero-temporal-leakage machine learning pipelines.

---

## 🌟 Key Highlights & Engineering Features

### 1. YouTube API Section III.E.4 Compliance (Mandatory 30-Day Rule)
- **Binding ToS Obligation:** Under YouTube API Developer Policies Section III.E.4.b–d, API clients must delete or refresh data obtained through the YouTube API within 30 days.
- **Pattern B Architecture (Derive Early, Purge Raw):** All raw API data entities (`raw_video_metadata`, `raw_daily_analytics`, `raw_retention_curves`, `raw_traffic_sources`, `raw_demographics`) are stamped at ingestion with `youtube_data_expires_at = retrieved_at + 30 days`.
- **Automated TTL Sweeper (`ComplianceService`):** Daily worker checks expired records. Raw records past 30 days are automatically purged and audited to `compliance_logs`. The platform persists independent derived statistical outputs (`derived_video_metrics`, `derived_content_clusters`, `feature_store`) that survive raw data purging.
- **Support for Pattern A (Refresh):** Optional per-table policy to re-query the YouTube API and renew freshness timestamps.

### 2. Analytical & Statistical Rigor
- **Group-Aware `viewerPercentage` Normalization:** YouTube normalizes viewer percentages *within* each playback-detail dimension group (`subscribedStatus`, `liveOrOnDemand`, `youtubeProduct`). Raw aggregation naively sums to 200%. The transform layer isolates dimension groups, preventing statistical inflation.
- **Incompatible Dimension/Metric Guards:** Query builders explicitly reject invalid API combinations (e.g., `liveOrOnDemand` cannot be combined with `averageViewPercentage` in channel reports).
- **Low-Volume Privacy Suppression Handling:** When YouTube Analytics suppresses granular demographic cells below privacy thresholds, the system flags `is_suppressed=True` and renders explicit *"Not enough available data"* states instead of false zeros.
- **Robust Virality Z-Score:** Views follow a heavy-tailed power-law distribution where viral outliers corrupt parametric means and standard deviations. The system utilizes median and Interquartile Range ($IQR$):
  $$\text{Robust } Z = \frac{X - \text{Median}}{IQR / 1.349}$$
  Categorizing videos into *Viral Breakout* ($Z \ge 1.5$), *Above Average*, *Average*, and *Underperforming*.
- **Audience Retention Exponential Decay Fit & $R^2$ Gating:**
  $$R(t) = R_0 \cdot e^{-\lambda t} + C$$
  Fitted via `scipy.optimize.curve_fit`. If goodness-of-fit $R^2 < 0.70$ (e.g., due to tutorial re-watch scrubbing or multi-peak behavior), the decay parameter $\lambda$ is automatically suppressed from the UI to prevent misleading claims.
- **0-30s Intro Hook Diagnostics & Mid-Video Dips:** Identifies initial viewer drop-off, mid-video abandonments ($>4\%$ sudden drops), and end-screen session continuation rates.

### 3. Leakage-Proof Machine Learning
- **Strict Temporal Cutoff Integrity:** Separate $t_0$ pre-publish upload features (title structure, duration bucket, topic category, upload day/hour) from $t_{24h}$ post-publish early signals. Zero future-data leakage into training sets.
- **Baseline Uplift Validation:** Trained `GradientBoostingRegressor` and `RandomForestRegressor` models are benchmarked against a naive median predictor, proving true machine learning uplift ($+35\%\text{ to }+48\%$ MAE improvement).
- **Draft Video Performance Simulator:** Interactive pre-publish tool simulating 30-day view velocity, watch hours, and providing actionable algorithmic optimization suggestions.

### 4. Evidence-Grounded Recommendations & Brutal Analysis Mode
- **Strict Evidence Object UI Contract:** Every recommendation exposes:
  ```json
  {
    "metric": "30-Second Intro Retention Drop-off",
    "baseline": 22.0,
    "observed_value": 32.5,
    "n": 32,
    "effect_size": 47.7,
    "confidence": 0.92,
    "limitations": ["Shorts format excluded"],
    "provenance_sources": ["raw_retention_curves", "derived_video_metrics"]
  }
  ```
- **Growth Opportunity Matrix:** Classifies recommendations into 4 actionable quadrants: *Quick Wins*, *Major Strategic Bets*, *Incremental Gains*, and *Low Priority*.
- **Brutal Strategic Audit Mode:** Unvarnished, direct, non-promotional critique highlighting leaky hooks, clickbait mismatch penalties, and wasted impressions.

### 5. Multi-Channel Reporting
- **Executive PDF Report:** Compiled with `reportlab`, containing executive summary, scorecard tables, retention diagnostics, and grounded evidence.
- **Standalone Responsive HTML Report:** Printable format with `@media print` stylesheets.
- **CSV Data Export:** Full export of video benchmarks and metrics.

---

## 🏗️ Architecture & Navigation Workflow

```
┌────────────────────────────────────────────────────────────────────────┐
│ FRONTEND INTERFACES                                                    │
│  - Full-Stack Dashboard (Tailwind CSS, Chart.js, Lucide, Glassmorphism)│
│  - Streamlit Data Science & Growth Studio (Plotly, Interactive EDA)    │
│  - Unified Headless CLI (`cli.py`)                                     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / REST
┌───────────────────────────────────▼────────────────────────────────────┐
│ API GATEWAY (FastAPI)                                                  │
│  - /api/v1/summary & /api/v1/videos (KPIs, Robust Z-scores, Drilldown) │
│  - /api/v1/retention (Exponential curve fit, lambda, R^2 gating)       │
│  - /api/v1/traffic-sources (Efficiency Quadrants)                      │
│  - /api/v1/demographics (Group-aware normalization)                    │
│  - /api/v1/content-intelligence (Clusters & Analytics Groups promotion)│
│  - /api/v1/predictions/simulate (Draft ML simulator)                   │
│  - /api/v1/recommendations & /growth-matrix (Evidence objects)         │
│  - /api/v1/reports/pdf & html (ReportLab generator)                    │
│  - /api/v1/compliance/status & sweep (Section III.E.4 TTL Sweeper)     │
└───────────────────┬───────────────────────────────┬────────────────────┘
                    │                               │
┌───────────────────▼───────────┐   ┌───────────────▼────────────────────┐
│ STORAGE & COMPLIANCE LAYER    │   │ ML & ANALYTICS PIPELINE            │
│  - raw_* (TTL = 30 Days)      │   │  - Scikit-Learn Gradient Boosting  │
│  - derived_* (Pattern B stats)│   │  - SciPy Non-linear Curve Fitting  │
│  - feature_store (t0 cutoffs) │   │  - Robust Virality (Median & IQR)  │
│  - quota_ledger (10k ceiling) │   │  - ReportLab PDF Engine            │
│  - compliance_logs            │   └────────────────────────────────────┘
└───────────────────────────────┘
```

---

## 🚀 Quickstart & Setup Guide

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- SQLite (built-in, zero configuration) or PostgreSQL

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Launch the Web Application
```powershell
python run.py
```
Open your browser to:
- **Interactive Web Dashboard:** `http://localhost:8000`
- **Swagger API Documentation:** `http://localhost:8000/docs`

*Note: On first startup, the application automatically initializes database schemas and seeds a comprehensive 32-video channel dataset with full historical depth, daily time series, retention curves, and traffic breakdowns.*

### 3. Launch the Streamlit Data Science Studio (Optional)
```powershell
streamlit run streamlit_app.py
```
Provides an interactive notebook view with interactive sliders, Plotly retention plots, and instant PDF report downloads.

---

## 💻 Headless Command-Line Interface (`cli.py`)

The platform includes a CLI runner for terminal operations and automation:

```powershell
# 1. Reseed / Sync channel dataset
python cli.py seed --channel "DevPulse Systems"

# 2. Check 30-Day TTL compliance status & quota usage
python cli.py status

# 3. Trigger 30-Day TTL Sweeper (Purges expired raw rows under Pattern B)
python cli.py sweep

# 4. Compile Executive PDF Growth Report
python cli.py report

# 5. Compile Brutal Strategic Audit PDF Report
python cli.py report --brutal
```

---

## 🧪 Automated Test Suite

Run the test suite to verify compliance, normalization, retention modeling, and leakage prevention:

```powershell
pytest -v
```

### Verified Test Cases:
1. `tests/test_compliance_ttl.py`: Verifies that raw ingestion records receive 30-day TTLs and that the TTL sweeper properly purges expired raw API records under Pattern B while logging to `compliance_logs`.
2. `tests/test_normalization.py`: Verifies group-aware `viewerPercentage` normalization (preventing the 200% double-counting error) and incompatible query validation (`liveOrOnDemand` vs `averageViewPercentage`).
3. `tests/test_retention_fit.py`: Verifies non-linear exponential curve fitting, $R^2 \ge 0.70$ gating, and 0-30s hook drop-off calculations.
4. `tests/test_leakage_controls.py`: Verifies zero temporal leakage in $t_0$ feature extraction and ML model uplift over median baselines.
5. `tests/test_evidence_objects.py`: Verifies strict compliance with the structured `EvidenceObject` contract.

---

## 📜 YouTube API Compliance Notice

This platform complies with YouTube's **API Services Developer Policies, Section III.E.4.b–d**:
- Data obtained through the YouTube API is subject to an automated 30-day Time-To-Live (TTL).
- By default (Pattern B), raw API records are swept and purged after 30 days.
- Derived analytical scores, custom performance metrics, and machine learning models represent independent transformations.
- To configure table-specific refresh policies or inspect TTL countdowns, navigate to `/data-sources` or run `python cli.py status`.
