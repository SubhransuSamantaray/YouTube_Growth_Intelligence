# System Architecture & Technical Specification

## YouTube Channel Growth Analysis and Intelligence Platform

### 1. High-Level Architectural Overview

The YouTube Channel Growth Analysis Platform is designed as an end-to-end data intelligence and predictive analytics platform. It bridges raw API extraction, statistical validation, non-linear audience retention modeling, leakage-free machine learning, and evidence-grounded recommendation engines.

```mermaid
flowchart TD
    subgraph Data Sources & Ingestion
        YT_API["YouTube Data API v3 & Analytics v2"]
        Mock_Gen["Statistical Mock Generator"]
        Rate_Limiter["Token & Quota Manager (10k units/day)"]
    end

    subgraph Data Validation & Compliance
        Comp_Daemon["30-Day TTL Sweeper (Policy III.E.4)"]
        Compat_Validator["Dimension Incompatibility Validator"]
        Norm_Layer["ViewerPercentage Group Normalizer"]
    end

    subgraph Storage & Feature Store
        SQL_WH[("SQLite / PostgreSQL Data Warehouse (22 Models)")]
        Feature_Store[("Strict t0 Feature Store (Zero Leakage)")]
    end

    subgraph Core Analytical & ML Engines
        Retention_Engine["Audience Retention Engine (Exponential Decay Fit)"]
        Analytics_Engine["Growth Analytics Engine (IQR Z-Score & 6 Pillars)"]
        Cohort_Engine["Winners vs Underperformers (Mann-Whitney U)"]
        ML_Engine["GradientBoosting Regressor vs Naive Baseline"]
        Rec_Engine["Evidence-Grounded Recommendation Engine"]
    end

    subgraph Serving & UI Layer
        FastAPI_Srv["FastAPI High-Performance REST API"]
        Web_Dash["Responsive Dark-Mode Web Dashboard"]
        Streamlit_Studio["Streamlit Data Science Studio"]
        PDF_Engine["ReportLab Executive PDF Generator"]
    end

    YT_API --> Rate_Limiter --> Compat_Validator
    Mock_Gen --> Compat_Validator
    Compat_Validator --> Norm_Layer --> SQL_WH
    SQL_WH <--> Comp_Daemon
    SQL_WH --> Feature_Store
    SQL_WH --> Retention_Engine
    SQL_WH --> Analytics_Engine
    SQL_WH --> Cohort_Engine
    Feature_Store --> ML_Engine
    Retention_Engine & Analytics_Engine & Cohort_Engine & ML_Engine --> Rec_Engine
    Rec_Engine --> FastAPI_Srv
    FastAPI_Srv --> Web_Dash
    FastAPI_Srv --> Streamlit_Studio
    Rec_Engine --> PDF_Engine
```

---

### 2. Database Schema (22 Relational Models)

The data model uses 22 tables with complete foreign key integrity, temporal indices, and compliance timestamps:
- **Core Entities:** `User`, `OAuthConnection`, `Channel`, `Video`, `ContentCategory`
- **Raw Telemetry (30-day TTL):** `VideoStatistics`, `VideoDailyAnalytics`, `ChannelDailyAnalytics`, `AudienceAnalytics`, `AudienceRetention`, `TrafficSources`, `Demographics`, `DeviceAnalytics`
- **Derived Analytics (Permanent Storage):** `DerivedVideoMetrics`, `DerivedContentCluster`
- **Machine Learning & Feature Store:** `FeatureStore`, `MLPrediction`, `ModelRun`
- **Actionable Intelligence:** `Recommendation`, `NextVideoOpportunity`, `ABExperiment`
- **Operational & Governance:** `DataIngestionRun`, `DataQualityReport`, `GeneratedReport`, `ComplianceLog`, `QuotaLedger`

---

### 3. Key Mathematical Models & Formulations

#### 3.1. Robust Virality Z-Score
YouTube view distributions are heavily skewed (power-law distribution). Mean and standard deviation are susceptible to extreme viral outliers. We utilize median and Interquartile Range ($IQR$):
$$Z_{\text{robust}} = \frac{x_i - \text{Median}(X)}{\text{IQR}(X) \times 0.7413}$$
where $\text{IQR} = Q_3 - Q_1$, and $0.7413$ scales the $IQR$ to an asymptotically unbiased estimator of standard deviation under normality.

#### 3.2. Exponential Audience Retention Decay
Retention decay over elapsed video ratio $t \in [0, 1]$ is modeled using non-linear least squares (`scipy.optimize.curve_fit`):
$$R(t) = R_0 \cdot e^{-\lambda t} + C$$
- $R_0$: Initial Hook Retention Amplitude
- $\lambda$: Decay rate parameter
- $C$: Baseline loyal core audience plateau
- **Model Gating:** Any video fit with $R^2 < 0.70$ is flagged for anomalous viewer behavior (e.g., massive internal chapter skipping).

#### 3.3. Recommendation Priority Formula
$$\text{Priority Score} = \text{Impact} \times \text{Confidence} \times \text{Opportunity} \times \text{Feasibility}$$
Where:
- $\text{Impact} \in [1, 10]$: Expected percentage uplift on core KPI
- $\text{Confidence} \in [0.1, 1.0]$: Derived from sample size $n$ and statistical significance ($p < 0.05$)
- $\text{Opportunity} \in [1, 10]$: Gap between current channel metric and top quartile benchmark
- $\text{Feasibility} \in [1, 10]$: Ease of operational execution by creator
