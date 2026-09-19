# CycloneAI — IMD Best-Track Data Preparation

## Project Overview

CycloneAI is an AI/ML-based cyclone forecasting and decision-support project focused on the Indian region.

This repository currently contains the data reconstruction, cleaning, exploratory analysis, and cyclone-level analysis performed on IMD best-track data for 2024 and 2025.

The processed dataset is prepared for downstream ML development.

---

## Current Work Completed

### 1. IMD Best-Track Data Reconstruction

The original IMD source files were provided in a flattened PDF-to-CSV format.

The raw observations were reconstructed into structured records containing:

- Cyclone ID
- Year
- Timestamp
- Latitude
- Longitude
- CI number
- Estimated Central Pressure (ECP)
- Pressure Drop
- Maximum Sustained Wind (MSW)
- Category

Date handling, table boundaries, timestamps, and observation validation were handled during reconstruction.

### 2. Data Validation

The reconstructed dataset was checked for:

- Missing values
- Duplicate observations
- Duplicate cyclone/timestamp combinations
- Invalid latitude/longitude values
- Invalid pressure values
- Invalid MSW values
- Timestamp ordering
- Large gaps between observations

The final dataset contains:

- 522 observations
- 28 cyclones
- 13 cyclones from 2024
- 15 cyclones from 2025

### 3. Exploratory Analysis

The following analyses were performed:

- Category distribution
- MSW distribution
- Pressure distribution
- Cyclone tracks
- Intensity evolution
- Pressure evolution
- Normalized cyclone lifecycle
- Category transitions
- Cyclone-level summaries
- Duration vs intensity
- Maximum cyclone intensity

---

## Dataset Status

The primary downstream dataset is:

```text
data/processed/imd_best_track_2024_2025.csv