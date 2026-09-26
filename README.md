# CycloneAI 🌪️

An AI/ML-based cyclone forecasting and decision-support system focused on the Indian region.

CycloneAI combines historical cyclone observations with numerical weather prediction, satellite observations, and environmental data to build an India-focused forecasting pipeline.

> **Current stage:** Data preparation and validation  
> **Primary datasets:** IMD Best-Track + WeatherNext  
> **Target:** India-focused cyclone track and intensity forecasting

---

## 📌 Project Overview

Accurate cyclone forecasting requires reliable historical observations and well-structured forecast data.

CycloneAI is being developed as a pipeline that will use:

- **IMD Best-Track data** as historical cyclone observations and reference data
- **WeatherNext** as a numerical weather forecasting baseline
- **Satellite observations** for cyclone detection and classification
- **Environmental data** for additional atmospheric and oceanic information
- **Machine learning** for India-specific forecast correction
- **Uncertainty estimation** for communicating forecast confidence
- **Geospatial analysis** for landfall and district-level risk assessment

The repository is currently focused on building and validating the data foundation required for the ML pipeline.

---

# 📂 Repository Structure

```text
CycloneAI/
│
├── data/
│   ├── raw/
│   │   ├── imd/
│   │   ├── environmental/
│   │   └── weathernext/
│   │
│   └── processed/
│       ├── imd_best_track_2024_2025.csv
│       └── weathernext_cleaned.csv
│
├── src/
│   ├── IMD reconstruction & validation
│   ├── Cyclone analysis
│   ├── WeatherNext cleaning
│   └── WeatherNext matching & overlap diagnostics
│
├── .gitattributes
├── .gitignore
└── README.md
🛰️ Data Pipeline

The current data workflow is:

IMD Raw Data
     │
     ▼
Reconstruction
     │
     ▼
Validation & Cleaning
     │
     ▼
IMD Best-Track Dataset
     │
     ├──────────────┐
     │              │
     ▼              ▼
Cyclone Analysis   WeatherNext
                      │
                      ▼
                 Data Validation
                      │
                      ▼
              Forecast Baseline
                      │
                      ▼
              IMD ↔ WeatherNext
                  Matching
                      │
                      ▼
             ML Correction Models
🌪️ IMD Best-Track Data
1. Data Reconstruction

The original IMD source files were provided in a flattened PDF-to-CSV format.

The observations were reconstructed into structured cyclone records containing:

Field	Description
cyclone_id	Identifier assigned to the reconstructed cyclone
year	Observation year
timestamp_utc	Observation timestamp
latitude	Cyclone center latitude
longitude	Cyclone center longitude
ci_no	Current Intensity number
ecp_hpa	Estimated Central Pressure
pressure_drop_hpa	Pressure drop
msw_kt	Maximum Sustained Wind
category	Cyclone intensity category

The reconstruction process handled table boundaries, timestamps, date information, and observation validation.

2. IMD Data Validation

The reconstructed dataset was checked for:

Missing values
Duplicate observations
Duplicate cyclone/timestamp combinations
Invalid latitude/longitude values
Invalid pressure values
Invalid MSW values
Timestamp consistency
Observation ordering
Large gaps between observations
Invalid cyclone categories
Dataset Summary
Metric	Value
Observations	522
Cyclones	28
Cyclones — 2024	13
Cyclones — 2025	15
Maximum observation gap	6 hours

The validated dataset is stored at:

data/processed/imd_best_track_2024_2025.csv
📊 IMD Exploratory Analysis

The repository contains analysis scripts covering:

Cyclone Tracks
Spatial cyclone trajectories
Individual cyclone track visualization
Geographic movement patterns
Intensity
Maximum sustained wind analysis
Intensity evolution
Maximum cyclone intensity
Pressure
Central pressure distribution
Pressure evolution throughout cyclone lifecycles
Lifecycle
Cyclone duration
Normalized lifecycle analysis
Intensity changes across cyclone stages
Category
Category distribution
Category transitions
Cyclone intensity classification
Cyclone-Level Analysis
Cyclone summaries
Duration vs. maximum intensity
Individual cyclone statistics
🌦️ WeatherNext Dataset

WeatherNext is being used as the forecast baseline for the downstream ML pipeline.

The raw WeatherNext dataset contains forecast information including:

Initialization time
Cyclone/track identifier
Ensemble member
Valid time
Forecast lead time
Latitude
Longitude
Minimum sea-level pressure
Maximum sustained wind
Radius of maximum winds
Wind radii

The dataset contains 64 ensemble members at initialization and forecasts extending to 360 hours.

WeatherNext Data Validation

The WeatherNext dataset was audited for:

Duplicate rows
Duplicate forecast keys
Invalid coordinates
Invalid timestamps
Invalid lead times
Invalid ensemble member values
Missing meteorological values
Ensemble completeness
Numerical range violations
Wind-radius consistency
Forecast time consistency
Important Data Handling

No rows were removed simply because they were unusual or difficult.

The cleaning process preserves valid observations, including:

Outliers
Large forecast errors
Unusual cyclone tracks
Large ensemble spread
Incomplete future ensemble groups

Rows are removed only when they are demonstrably invalid or corrupted.

The cleaned dataset is stored at:

data/processed/weathernext_cleaned.csv

Because this dataset is approximately 303 MB, it is stored using Git LFS.

🔬 Current Analysis & Validation Scripts

The src/ directory currently contains scripts for:

IMD
imd_reconstruction.py
imd_quality_check.py
imd_eda.py
cyclone_summary.py
cyclone_summary_visualization.py
cyclone_lifecycle_analysis.py
category_transition_analysis.py
intensity_analysis.py
track_analysis.py
plot_cyclone_tracks.py
WeatherNext
clean_weathernext.py
weathernext_episode_check.py
weathernext_episode_matching_diagnostic.py
weathernext_overlap_check.py
weathernext_spatial_overlap.py

These scripts are used for reconstruction, validation, exploratory analysis, and preparation for the IMD–WeatherNext integration stage.

🧠 Planned ML Pipeline

The next stage is to connect WeatherNext forecasts with IMD observations and evaluate the baseline forecast.

The planned pipeline is:

IMD Best-Track
       │
       │
       ├───────────────┐
       │               │
       ▼               ▼
Historical         WeatherNext
Ground Truth        Forecast
       │               │
       └───────┬───────┘
               ▼
        Forecast Matching
               │
               ▼
        Baseline Evaluation
               │
               ▼
       ML Track Correction
               │
               ▼
     Intensity Correction
               │
               ▼
       Uncertainty Model
               │
               ▼
      Landfall / Risk Engine
               │
               ▼
        Decision Support

The initial ML objective is to learn India-specific corrections to the WeatherNext baseline rather than attempting to train a new global weather forecasting model from scratch.

🎯 Planned ML Objectives
1. Track Correction

Estimate the difference between the WeatherNext forecast position and the observed IMD cyclone position.

The correction can be represented using:

North–south position error
East–west position error

Performance will be evaluated using forecast lead times such as:

24h
48h
72h

and additional lead times where sufficient data is available.

2. Intensity Correction

Estimate corrections to WeatherNext intensity forecasts using observed IMD values.

Potential targets include:

Maximum sustained wind
Central pressure
3. Uncertainty Estimation

WeatherNext ensemble forecasts provide multiple possible forecast trajectories.

The project will investigate:

Ensemble spread
Forecast error distribution
Historical residuals
Uncertainty calibration

The goal is to provide forecast confidence alongside the predicted track and intensity.

4. Risk Assessment

The final system is intended to combine:

Corrected Cyclone Track
          +
Intensity
          +
Forecast Uncertainty
          +
Geospatial Information
          +
Exposure Data
          ↓
Landfall / District Risk

This layer is intended for decision support rather than replacing official warnings.

📈 Evaluation Strategy

Model performance will be evaluated against the original WeatherNext forecast baseline.

For track forecasting, improvement will be measured using forecast position error:

Improvement (%) =
(Baseline Error - Corrected Error)
---------------------------------- × 100
          Baseline Error

Evaluation will use cyclone-level train/validation/test splits rather than randomly splitting individual observations.

This helps prevent observations from the same cyclone appearing in both training and evaluation data.

⚠️ Current Status
Completed
 IMD 2024/2025 raw data reconstruction
 IMD data validation
 IMD exploratory analysis
 Cyclone-level analysis
 WeatherNext data inspection
 WeatherNext quality validation
 WeatherNext cleaning pipeline
 WeatherNext ensemble analysis
 WeatherNext temporal/spatial overlap diagnostics
 Processed datasets generated
 Large WeatherNext dataset configured with Git LFS
In Progress
 IMD ↔ WeatherNext forecast matching
 Baseline WeatherNext track-error evaluation
 Feature engineering
 Track-correction model
 Intensity-correction model
 Uncertainty calibration
 Satellite-based cyclone information
 Landfall and district-level risk engine
 API and dashboard integration
🛠️ Technology Stack
Data & Analysis
Python
Pandas
NumPy
Matplotlib
CSV-based data pipelines
Machine Learning
PyTorch
XGBoost
Scikit-learn
Geospatial
GeoPandas
Shapely
PostGIS
GeoJSON
Backend
FastAPI
Redis
PostgreSQL
Frontend & Visualization
React
Mapbox GL JS
Turf.js
Deployment
Google Cloud Storage
Vercel
Render / Railway
GitHub Actions
📌 Data Philosophy

CycloneAI follows a conservative data-cleaning approach.

Valid but unusual observations should not be removed simply because they make a model harder to train.

The project therefore aims to:

Preserve genuine extreme events
Preserve unusual cyclone tracks
Preserve large forecast errors
Preserve ensemble spread
Remove only demonstrably corrupted records
Keep unmatched observations available for analysis
Exclude unsuitable records from training when necessary rather than deleting them from the underlying dataset

This is particularly important for cyclone forecasting because rare and extreme events are often the most important cases for evaluation.

🚧 Development Status

CycloneAI is currently in the data preparation and baseline development stage.

The immediate technical priority is:

IMD ↔ WeatherNext Matching
             ↓
      Baseline Evaluation
             ↓
      Feature Engineering
             ↓
       Track Correction

Model performance claims will only be reported after evaluation on previously unseen cyclone cases.

📜 License

License information will be added as the project is prepared for wider distribution.
