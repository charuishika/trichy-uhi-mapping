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

### 4. Relative UHI Analysis

Relative UHI is calculated by comparing each pixel's surface temperature with the mean surface temperature of the selected study area.

\[
Relative\ UHI = Pixel\ LST - Mean\ LST
\]

- Positive values indicate warmer-than-average areas.
- Negative values indicate cooler-than-average areas.

### 5. Heat Hotspot Identification

Areas with relative UHI values greater than **+2°C** are identified as potential heat hotspots.

### 6. Mitigation Zone Identification

The system identifies preliminary mitigation zones using the following criteria:

| Mitigation Type | Screening Criteria |
|---|---|
| Tree Planting | Relative UHI > +1°C and NDVI < 0.30 |
| Cool Roof | Relative UHI > +1°C and NDBI > 0 |

These criteria are used for preliminary screening and require further local validation.

---

## 🔄 Project Workflow

```text
Landsat 8 & Landsat 9 Data
            ↓
Google Earth Engine
            ↓
Data Filtering & Preprocessing
            ↓
Cloud Masking & Median Composite
            ↓
LST, NDVI & NDBI Calculation
            ↓
Relative UHI Analysis
            ↓
Hotspot Identification
            ↓
Mitigation Zone Identification
            ↓
Interactive Streamlit Dashboard
```

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application development and data analysis |
| Google Earth Engine | Satellite data retrieval and processing |
| Landsat 8 & 9 | Satellite data source |
| Streamlit | Interactive web dashboard |
| Pandas | Data analysis and manipulation |
| Matplotlib | Data visualization |
| Folium | Interactive map visualization |

---


## 🚀 Installation & Setup

### Prerequisites

- Python 3.9 or above
- Git
- Google Earth Engine account and access, if required by the application

### 1. Clone the Repository

```bash
git clone <repository-url>
```

### 2. Navigate to the Project Directory

```bash
cd <project-folder>
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows**

```bash
venv\Scripts\activate
```

**Linux/macOS**

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Google Earth Engine

Configure Google Earth Engine authentication if the application requires access to Earth Engine during execution.

**Never upload private credentials, authentication tokens, or secret configuration files to GitHub.**

### 6. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser.

> Replace `app.py` with the actual Streamlit entry-point filename if your project uses a different file.

---

## 📈 Results

The application provides visual and analytical outputs including:

- Spatial distribution of land surface temperature.
- Vegetation distribution across the study area.
- Built-up characteristics.
- Relative temperature variations.
- Potential heat hotspot locations.
- Potential tree-planting zones.
- Potential cool-roof zones.
- Correlation analysis between LST, NDVI, and NDBI.

---

## ⚠️ Limitations

- Satellite-derived LST represents land surface temperature, not air temperature.
- Analysis is limited to the selected study area and date range.
- Cloud cover and satellite data availability may affect the analysis.
- Relative UHI values depend on the mean temperature of the selected area.
- Correlation does not establish causation.
- Mitigation zones are preliminary recommendations and require field verification.

---

## 🔮 Future Scope

- Extend the analysis to additional cities and larger geographical regions.
- Incorporate ground-level temperature measurements for validation.
- Include population density and land-use information.
- Improve mitigation recommendations using local environmental observations.
- Explore machine learning techniques for temperature prediction.
- Deploy the application for public access.

---

## 👩‍💻 Project Team

**Charuishika S**  
B.Tech – Computer Science and Engineering

**Sanjitha Sivarajan**  
B.Tech – Electronics and Instrumentation Engineering

**Institution:** SASTRA Deemed to be University  
**Course:** IDP401M – Minor Project  
**Academic Year:** 2026–2027

---

## 📚 References

1. A. Galodha and S. K. Gupta, “Land Surface Temperature as an Indicator of Urban Heat Island Effect: A Google Earth Engine Based Web-App,” *The International Archives of the Photogrammetry, Remote Sensing and Spatial Information Sciences*, 2021.
2. U.S. Geological Survey, Landsat Collection 2 Surface Temperature.
3. Google Earth Engine, Landsat 8 Collection 2 Tier 1 Level 2 Dataset.
4. U.S. Geological Survey, Landsat Collection 2 Surface Reflectance.
5. Research literature on Land Surface Temperature, NDVI, NDBI, and Urban Heat Island analysis.

---

## 📄 License

This project was developed as part of an academic minor project at SASTRA Deemed to be University. 
