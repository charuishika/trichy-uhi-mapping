# 🌡️ Urban Heat Island (UHI) Mapping & Mitigation System

## 📌 Project Overview

The **Urban Heat Island (UHI) Mapping & Mitigation System** is a geospatial application developed to analyse urban surface temperature variations and identify heat hotspots in Tiruchirappalli, Tamil Nadu.

The system uses Landsat 8 and Landsat 9 satellite data to calculate Land Surface Temperature (LST), Normalized Difference Vegetation Index (NDVI), and Normalized Difference Built-up Index (NDBI). Based on these parameters, it identifies relatively hotter areas and suggests potential mitigation zones such as tree planting and cool roofs.

An interactive dashboard is developed using Streamlit to visualize satellite-derived information, temperature patterns, hotspots, and mitigation areas.

---

## 🎯 Objectives

- Analyse urban temperature variations using satellite data.
- Calculate Land Surface Temperature (LST).
- Analyse vegetation using NDVI.
- Analyse built-up areas using NDBI.
- Identify Urban Heat Island hotspots.
- Identify potential tree-planting and cool-roof zones.
- Visualize results through an interactive dashboard.

---

## 🗺️ Study Area

**Location:** Tiruchirappalli (Trichy), Tamil Nadu, India

**Area of Interest (AOI):**
- Latitude: 10.75°N – 10.85°N
- Longitude: 78.65°E – 78.80°E

**Study Period:** 01 January 2026 – 31 March 2026

---

## ✨ Features

- Interactive study-area map
- Land Surface Temperature (LST) visualization
- NDVI vegetation analysis
- NDBI built-up area analysis
- Relative UHI analysis
- Heat hotspot identification
- Tree-planting zone identification
- Cool-roof zone identification
- Statistical analysis and correlation visualization
- Interactive dashboard for exploring results

---

## 🛰️ Data Sources

| Data | Source | Purpose |
|---|---|---|
| Landsat 8 | Google Earth Engine | Satellite imagery and analysis |
| Landsat 9 | Google Earth Engine | Satellite imagery and analysis |
| Surface Temperature | Landsat Collection 2 Level 2 | LST calculation |
| Red Band | Landsat Surface Reflectance | NDVI calculation |
| Near Infrared (NIR) | Landsat Surface Reflectance | NDVI and NDBI calculation |
| Shortwave Infrared (SWIR) | Landsat Surface Reflectance | NDBI calculation |

---

## 🧮 Analysis Performed

### 1. Land Surface Temperature (LST)

Land Surface Temperature is calculated from Landsat thermal data to understand the surface temperature distribution across the selected urban region.

### 2. Normalized Difference Vegetation Index (NDVI)

NDVI is used to analyse vegetation density.

\[
NDVI = \frac{NIR - Red}{NIR + Red}
\]

Higher NDVI values generally indicate more vegetation.

### 3. Normalized Difference Built-up Index (NDBI)

NDBI is used to identify built-up characteristics.

\[
NDBI = \frac{SWIR - NIR}{SWIR + NIR}
\]

Higher positive NDBI values generally indicate built-up surfaces.

### 4
