import streamlit as st
import ee
import folium
import pandas as pd
from streamlit_folium import st_folium
from datetime import date, timedelta

# ============================================================
# 1. PAGE CONFIGURATION & PROFESSIONAL THEME
# ============================================================
st.set_page_config(
    page_title="Trichy UHI | Geospatial Analysis",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.7rem; padding-bottom: 2.5rem;}
    [data-testid="stMetric"] {
        background: rgba(100,116,139,.10);
        border: 1px solid rgba(148,163,184,.22);
        padding: 15px 18px;
        border-radius: 12px;
    }
    .kicker {
        text-transform: uppercase; letter-spacing: .12em;
        font-size: .76rem; font-weight: 700; color: #14b8a6;
    }
    .legend-item {display:flex; align-items:center; gap:9px; margin:6px 0;}
    .swatch {width:15px; height:15px; border-radius:3px; display:inline-block; border:1px solid #64748b;}
    </style>
    """,
    unsafe_allow_html=True,
)

PROJECT_ID = "trichy-uhi-project"

# ============================================================
# 2. HEADER
# ============================================================
st.markdown(
    '<div class="kicker">Geospatial climate analytics · Tamil Nadu, India</div>',
    unsafe_allow_html=True,
)
st.title("Urban Heat Island Mapping & Mitigation System")
st.write(
    "Satellite-based land surface temperature, vegetation and built-up indices, "
    "relative heat hotspots, and preliminary mitigation screening."
)
st.caption(
    "Study area: Trichy, Tamil Nadu · Data source: Landsat 8/9 Collection 2 Level 2"
)

# ============================================================
# 3. EARTH ENGINE INITIALIZATION
# ============================================================
@st.cache_resource
def initialize_earth_engine():
    ee.Initialize(project=PROJECT_ID)
    return True

try:
    initialize_earth_engine()
    st.sidebar.success("Earth Engine connected")
except Exception as exc:
    st.error("Earth Engine initialization failed. Check your authentication and project ID.")
    with st.expander("Technical details"):
        st.exception(exc)
    st.stop()

# ============================================================
# 4. AREA OF INTEREST
# ============================================================
aoi = ee.Geometry.Rectangle([78.65, 10.75, 78.80, 10.85])

# ============================================================
# 5. SIDEBAR CONTROLS
# ============================================================
st.sidebar.header("Analysis settings")
start_date = st.sidebar.date_input("Start date", value=date(2026, 1, 1))
end_date = st.sidebar.date_input("End date", value=date(2026, 3, 31))

st.sidebar.markdown("---")
st.sidebar.subheader("Compare another period")
compare_enabled = st.sidebar.checkbox("Enable date/season comparison", value=True)
compare_start = st.sidebar.date_input(
    "Comparison start date", value=date(2025, 1, 1), key="compare_start_date"
)
compare_end = st.sidebar.date_input(
    "Comparison end date", value=date(2025, 3, 31), key="compare_end_date"
)

layer_options = [
    "LST",
    "NDVI",
    "NDBI",
    "Relative UHI",
    "Hotspots",
    "Heat-risk classification",
    "Tree-planting screening",
    "Cool-roof screening",
]
selected_layer = st.sidebar.selectbox("Map layer", layer_options)

st.sidebar.markdown("---")
st.sidebar.markdown("**Study-area bounds**")
st.sidebar.code("78.65°E–78.80°E\n10.75°N–10.85°N")
st.sidebar.caption(
    "Satellite-derived results for the selected period; not live air-temperature readings."
)
run_analysis = st.sidebar.button(
    "Run UHI analysis", type="primary", use_container_width=True
)

if start_date > end_date:
    st.error("Start date must be before or equal to end date.")
    st.stop()

if compare_enabled and compare_start > compare_end:
    st.error("Comparison start date must be before or equal to comparison end date.")
    st.stop()

# ============================================================
# 6. IMAGE PROCESSING FUNCTIONS
# ============================================================
def mask_landsat(image):
    """Mask fill, dilated cloud, cirrus, cloud, and cloud-shadow pixels."""
    qa = image.select("QA_PIXEL")
    mask = (
        qa.bitwiseAnd(1 << 0).eq(0)
        .And(qa.bitwiseAnd(1 << 1).eq(0))
        .And(qa.bitwiseAnd(1 << 2).eq(0))
        .And(qa.bitwiseAnd(1 << 3).eq(0))
        .And(qa.bitwiseAnd(1 << 4).eq(0))
    )
    return image.updateMask(mask)


def add_indices(image):
    """Add land surface temperature (Celsius), NDVI, and NDBI bands."""
    lst = (
        image.select("ST_B10")
        .multiply(0.00341802)
        .add(149.0)
        .subtract(273.15)
        .rename("LST")
    )
    ndvi = image.normalizedDifference(["SR_B5", "SR_B4"]).rename("NDVI")
    ndbi = image.normalizedDifference(["SR_B6", "SR_B5"]).rename("NDBI")
    return image.addBands([lst, ndvi, ndbi])


def add_ee_layer(map_object, image, vis_params, name):
    """Add an Earth Engine image as a tile layer to Folium."""
    map_id = ee.Image(image).getMapId(vis_params)
    folium.TileLayer(
        tiles=map_id["tile_fetcher"].url_format,
        attr="Google Earth Engine",
        name=name,
        overlay=True,
        control=True,
    ).add_to(map_object)


def calculate_area_hectares(mask_image, region):
    """Calculate area of unmasked pixels in hectares at 30 m nominal scale."""
    area_image = ee.Image.pixelArea().updateMask(mask_image)
    area_result = area_image.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=region,
        scale=30,
        maxPixels=1e9,
        bestEffort=True,
        tileScale=4,
    ).getInfo()
    area_m2 = area_result.get("area")
    if area_m2 is None:
        return 0.0
    return float(area_m2) / 10000.0


def summarize_period(region, period_start, period_end):
    """Calculate comparable Landsat 8/9 metrics for one date period."""
    landsat8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
    landsat9 = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")
    collection = (
        landsat8.merge(landsat9)
        .filterBounds(region)
        .filterDate(str(period_start), str(period_end + timedelta(days=1)))
        .map(mask_landsat)
        .map(add_indices)
    )

    scene_count = collection.size().getInfo()
    if scene_count == 0:
        return None

    composite_period = collection.median().clip(region)
    means = composite_period.select(["LST", "NDVI", "NDBI"]).reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=region,
        scale=30,
        maxPixels=1e9,
        bestEffort=True,
        tileScale=4,
    ).getInfo()

    mean_lst_period = means.get("LST")
    if mean_lst_period is None:
        return None

    relative_uhi_period = (
        composite_period.select("LST").subtract(mean_lst_period).rename("UHI")
    )
    hotspots_period = relative_uhi_period.gt(2).selfMask()
    hotspot_area_period = calculate_area_hectares(hotspots_period, region)

    return {
        "scene_count": scene_count,
        "mean_lst": float(mean_lst_period),
        "mean_ndvi": float(means["NDVI"]) if means.get("NDVI") is not None else None,
        "mean_ndbi": float(means["NDBI"]) if means.get("NDBI") is not None else None,
        "hotspot_area_ha": float(hotspot_area_period),
    }


# ============================================================
# 7. RUN ANALYSIS
# ============================================================
if run_analysis:
    with st.spinner("Processing Landsat imagery and calculating indicators…"):
        try:
            landsat8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
            landsat9 = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")

            collection = (
                landsat8.merge(landsat9)
                .filterBounds(aoi)
                .filterDate(str(start_date), str(end_date + timedelta(days=1)))
                .map(mask_landsat)
                .map(add_indices)
            )

            image_count = collection.size().getInfo()
            if image_count == 0:
                st.warning("No Landsat scenes were found for this date range. Try another period.")
                st.stop()

            composite = collection.median().clip(aoi)

            mean_result = composite.select("LST").reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=aoi,
                scale=30,
                maxPixels=1e9,
                bestEffort=True,
            ).getInfo()
            mean_lst = mean_result.get("LST")

            if mean_lst is None:
                st.warning("No valid LST pixels were found. Try another date range.")
                st.stop()

            # Relative surface-heat indicator, not a direct urban/rural comparison.
            uhi = composite.select("LST").subtract(mean_lst).rename("UHI")
            hotspots = uhi.gt(2).selfMask().rename("Hotspots")

            # Class 0: at/below AOI mean; 1: (0, 1]; 2: (1, 2]; 3: > 2 C.
            heat_risk = (
                ee.Image(0)
                .where(uhi.gt(0), 1)
                .where(uhi.gt(1), 2)
                .where(uhi.gt(2), 3)
                .rename("HeatRisk")
                .clip(aoi)
            )

            # Exploratory screening criteria. These do not confirm real-world suitability.
            tree_priority = (
                uhi.gt(1)
                .And(composite.select("NDVI").lt(0.30))
                .selfMask()
                .rename("TreePlantingScreen")
            )
            cool_roof_priority = (
                uhi.gt(1)
                .And(composite.select("NDBI").gt(0))
                .selfMask()
                .rename("CoolRoofScreen")
            )

            # ====================================================
            # 8. METRIC CARDS
            # ====================================================
            st.subheader("Analysis overview")
            st.caption(
                f"Composite period: {start_date:%d %b %Y} – {end_date:%d %b %Y} "
                "· Median of cloud-masked scenes"
            )
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Landsat scenes", f"{image_count:,}")
            m2.metric("Mean LST", f"{mean_lst:.2f} °C")
            m3.metric("Hotspot threshold", "+2.00 °C")
            m4.metric("Study area", "Trichy")

            # ====================================================
            # 9. MAP LAYERS
            # ====================================================
            layer_settings = {
                "LST": (
                    composite.select("LST"),
                    {
                        "min": 20, "max": 45,
                        "palette": ["313695", "74add1", "ffffbf", "fdae61", "d73027"],
                    },
                ),
                "NDVI": (
                    composite.select("NDVI"),
                    {
                        "min": -0.2, "max": 0.8,
                        "palette": ["8c510a", "dfc27d", "f6e8c3", "80cdc1", "01665e"],
                    },
                ),
                "NDBI": (
                    composite.select("NDBI"),
                    {
                        "min": -0.5, "max": 0.5,
                        "palette": ["2166ac", "f7f7f7", "f4a582", "b2182b"],
                    },
                ),
                "Relative UHI": (
                    uhi,
                    {
                        "min": -5, "max": 5,
                        "palette": ["2166ac", "67a9cf", "f7f7f7", "fdae61", "b2182b"],
                    },
                ),
                "Hotspots": (hotspots, {"min": 1, "max": 1, "palette": ["d7191c"]}),
                "Heat-risk classification": (
                    heat_risk,
                    {
                        "min": 0, "max": 3,
                        "palette": ["2c7bb6", "ffffbf", "fdae61", "d7191c"],
                    },
                ),
                "Tree-planting screening": (
                    tree_priority, {"min": 1, "max": 1, "palette": ["1a9850"]}
                ),
                "Cool-roof screening": (
                    cool_roof_priority, {"min": 1, "max": 1, "palette": ["762a83"]}
                ),
            }

            st.subheader(f"Spatial view · {selected_layer}")
            st.caption(
                "Use the zoom controls to explore the map. The outline marks the study-area boundary."
            )
            map_view = folium.Map(
                location=[10.80, 78.725],
                zoom_start=11,
                tiles="OpenStreetMap",
                control_scale=True,
            )
            add_ee_layer(
                map_view,
                layer_settings[selected_layer][0],
                layer_settings[selected_layer][1],
                selected_layer,
            )
            folium.Rectangle(
                bounds=[[10.75, 78.65], [10.85, 78.80]],
                color="#111827",
                weight=2,
                fill=False,
                tooltip="Trichy study area",
            ).add_to(map_view)
            folium.LayerControl(collapsed=False).add_to(map_view)
            st_folium(
                map_view,
                height=570,
                use_container_width=True,
                returned_objects=[],
            )

            # A clear legend for the heat-risk classification layer.
            if selected_layer == "Heat-risk classification":
                st.markdown("#### Heat-risk legend")
                legend_cols = st.columns(4)
                legend_items = [
                    ("#2c7bb6", "Class 0", "At/below AOI mean"),
                    ("#ffffbf", "Class 1", "Above mean to +1 °C"),
                    ("#fdae61", "Class 2", "Above +1 to +2 °C"),
                    ("#d7191c", "Class 3", "Above +2 °C"),
                ]
                for col, (color, label, description) in zip(legend_cols, legend_items):
                    with col:
                        st.markdown(
                            f'<div class="legend-item"><span class="swatch" style="background:{color}"></span>'
                            f'<b>{label}</b></div><div>{description}</div>',
                            unsafe_allow_html=True,
                        )
                st.caption(
                    "Classes represent relative land-surface temperature compared with the study-area mean; "
                    "they are not medical heat-risk categories."
                )

            if selected_layer == "Relative UHI":
                st.markdown("#### Relative UHI legend")
                st.markdown(
                    "Blue = cooler than the AOI mean · White = near the mean · "
                    "Orange/red = warmer than the AOI mean."
                )
            elif selected_layer == "Hotspots":
                st.markdown("#### Hotspot legend")
                st.markdown("Red pixels indicate LST more than 2 °C above the AOI mean.")
            elif selected_layer == "Tree-planting screening":
                st.markdown("#### Tree-planting screening legend")
                st.markdown("Green pixels meet the exploratory rule: relative UHI > +1 °C and NDVI < 0.30.")
            elif selected_layer == "Cool-roof screening":
                st.markdown("#### Cool-roof screening legend")
                st.markdown("Purple pixels meet the exploratory rule: relative UHI > +1 °C and NDBI > 0.")

            # ====================================================
            # 10. ENVIRONMENTAL STATISTICS
            # ====================================================
            st.subheader("Environmental indicators")
            summary = composite.select(["LST", "NDVI", "NDBI"]).reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=aoi,
                scale=30,
                maxPixels=1e9,
                bestEffort=True,
            ).getInfo()

            stats_df = pd.DataFrame(
                [
                    {
                        "Indicator": "Mean land surface temperature",
                        "Band": "LST",
                        "Mean": summary.get("LST"),
                        "Unit": "°C",
                    },
                    {
                        "Indicator": "Mean vegetation index",
                        "Band": "NDVI",
                        "Mean": summary.get("NDVI"),
                        "Unit": "Index",
                    },
                    {
                        "Indicator": "Mean built-up index",
                        "Band": "NDBI",
                        "Mean": summary.get("NDBI"),
                        "Unit": "Index",
                    },
                    {
                        "Indicator": "Mean relative UHI",
                        "Band": "UHI",
                        "Mean": 0.0,
                        "Unit": "°C from AOI mean",
                    },
                ]
            )
            stats_df["Mean"] = pd.to_numeric(stats_df["Mean"], errors="coerce").round(4)
            st.dataframe(stats_df, use_container_width=True, hide_index=True)

            # ====================================================
            # 11. SAMPLE-BASED CORRELATIONS
            # ====================================================
            st.subheader("Indicator relationships")
            st.caption(
                "Correlations are calculated from sampled composite pixels. They describe association, not causation. "
                "Relative UHI is LST minus the AOI mean LST."
            )
            sampled = composite.select(["LST", "NDVI", "NDBI"]).sample(
                region=aoi,
                scale=120,
                numPixels=1200,
                seed=42,
                geometries=False,
                dropNulls=True,
                tileScale=4,
            ).getInfo()
            sample_rows = [
                feature.get("properties", {})
                for feature in sampled.get("features", [])
            ]
            sample_df = pd.DataFrame(sample_rows)

            if not sample_df.empty and all(
                col in sample_df.columns for col in ["LST", "NDVI", "NDBI"]
            ):
                sample_df = (
                    sample_df[["LST", "NDVI", "NDBI"]]
                    .apply(pd.to_numeric, errors="coerce")
                    .dropna()
                )
            else:
                sample_df = pd.DataFrame(columns=["LST", "NDVI", "NDBI"])

            if len(sample_df) >= 3:
                corr_df = sample_df.corr(numeric_only=True)
                left, right = st.columns(2)
                with left:
                    st.markdown("**Sample correlation matrix**")
                    st.dataframe(corr_df.round(3), use_container_width=True)
                with right:
                    st.markdown("**LST vs vegetation (NDVI)**")
                    st.scatter_chart(sample_df, x="NDVI", y="LST", height=280)
                st.markdown("**LST vs built-up index (NDBI)**")
                st.scatter_chart(sample_df, x="NDBI", y="LST", height=280)
            else:
                st.info("Not enough valid sample pixels were returned to calculate correlations.")

            # ====================================================
            # 12. MITIGATION AREA ESTIMATES
            # ====================================================
            st.subheader("Mitigation opportunity screening")
            st.caption(
                "Area estimates are based on 30 m nominal pixel area and exploratory screening rules. "
                "They are not confirmed project sites; validate with planning data and field observations."
            )

            tree_area_ha = calculate_area_hectares(tree_priority, aoi)
            cool_roof_area_ha = calculate_area_hectares(cool_roof_priority, aoi)
            hotspot_area_ha = calculate_area_hectares(hotspots, aoi)

            area1, area2, area3 = st.columns(3)
            area1.metric("Hotspot area", f"{hotspot_area_ha:,.1f} ha")
            area2.metric("Tree-planting screening area", f"{tree_area_ha:,.1f} ha")
            area3.metric("Cool-roof screening area", f"{cool_roof_area_ha:,.1f} ha")

            # ====================================================
            # DATE / SEASON COMPARISON
            # ====================================================
            if compare_enabled:
                st.subheader("Date / season comparison")
                st.caption(
                    "Both periods use the same study area and Landsat 8/9 processing workflow. "
                    "Differences are satellite-derived surface indicators; they do not prove that "
                    "season alone caused a change."
                )

                if compare_start == start_date and compare_end == end_date:
                    st.info("Choose a different comparison period to compare changes.")
                else:
                    with st.spinner("Processing the comparison period…"):
                        comparison = summarize_period(aoi, compare_start, compare_end)

                    if comparison is None:
                        st.warning(
                            "No valid Landsat observations were found for the comparison period. "
                            "Try a different date range."
                        )
                    else:
                        primary_lst = summary.get("LST")
                        primary_ndvi = summary.get("NDVI")
                        primary_ndbi = summary.get("NDBI")

                        delta_lst = (
                            float(primary_lst) - comparison["mean_lst"]
                            if primary_lst is not None else None
                        )
                        delta_ndvi = (
                            float(primary_ndvi) - comparison["mean_ndvi"]
                            if primary_ndvi is not None and comparison["mean_ndvi"] is not None else None
                        )
                        delta_ndbi = (
                            float(primary_ndbi) - comparison["mean_ndbi"]
                            if primary_ndbi is not None and comparison["mean_ndbi"] is not None else None
                        )
                        delta_hotspot = hotspot_area_ha - comparison["hotspot_area_ha"]

                        cmp1, cmp2, cmp3, cmp4 = st.columns(4)
                        cmp1.metric(
                            "Mean LST difference",
                            "N/A" if delta_lst is None else f"{delta_lst:+.2f} °C",
                            help="Primary period mean LST minus comparison period mean LST."
                        )
                        cmp2.metric(
                            "Mean NDVI difference",
                            "N/A" if delta_ndvi is None else f"{delta_ndvi:+.3f}"
                        )
                        cmp3.metric(
                            "Mean NDBI difference",
                            "N/A" if delta_ndbi is None else f"{delta_ndbi:+.3f}"
                        )
                        cmp4.metric(
                            "Hotspot area difference",
                            f"{delta_hotspot:+.1f} ha",
                            help="Primary period hotspot area minus comparison period hotspot area."
                        )

                        comparison_df = pd.DataFrame([
                            {
                                "Metric": "Mean LST (°C)",
                                "Primary period": primary_lst,
                                "Comparison period": comparison["mean_lst"],
                                "Difference (primary − comparison)": delta_lst,
                            },
                            {
                                "Metric": "Mean NDVI",
                                "Primary period": primary_ndvi,
                                "Comparison period": comparison["mean_ndvi"],
                                "Difference (primary − comparison)": delta_ndvi,
                            },
                            {
                                "Metric": "Mean NDBI",
                                "Primary period": primary_ndbi,
                                "Comparison period": comparison["mean_ndbi"],
                                "Difference (primary − comparison)": delta_ndbi,
                            },
                            {
                                "Metric": "Hotspot area (ha)",
                                "Primary period": hotspot_area_ha,
                                "Comparison period": comparison["hotspot_area_ha"],
                                "Difference (primary − comparison)": delta_hotspot,
                            },
                            {
                                "Metric": "Landsat scene count",
                                "Primary period": image_count,
                                "Comparison period": comparison["scene_count"],
                                "Difference (primary − comparison)": image_count - comparison["scene_count"],
                            },
                        ])
                        st.dataframe(
                            comparison_df.round(3),
                            use_container_width=True,
                            hide_index=True
                        )

                        lst_chart = pd.DataFrame({
                            "Period": [
                                f"Primary ({start_date:%d %b %Y}–{end_date:%d %b %Y})",
                                f"Comparison ({compare_start:%d %b %Y}–{compare_end:%d %b %Y})",
                            ],
                            "Mean LST (°C)": [primary_lst, comparison["mean_lst"]],
                        }).set_index("Period")
                        st.markdown("#### Mean land-surface temperature by period")
                        st.bar_chart(lst_chart)

            rec_left, rec_right = st.columns(2)
            with rec_left:
                st.markdown("#### Tree-planting candidates")
                st.write(
                    "Pixels with relative UHI above +1 °C and NDVI below 0.30 may indicate warmer "
                    "areas with limited vegetation. Verify land availability, soil, water access, "
                    "native species suitability, and existing land use before proposing planting."
                )
                st.markdown("**Map layer:** Tree-planting screening (green)")
            with rec_right:
                st.markdown("#### Cool-roof candidates")
                st.write(
                    "Pixels with relative UHI above +1 °C and NDBI above 0 are broad built-up "
                    "candidates. This does not identify individual roofs; use building footprints "
                    "and local surveys before recommending specific roofs."
                )
                st.markdown("**Map layer:** Cool-roof screening (purple)")

            # ====================================================
            # 13. DOWNLOADS
            # ====================================================
            st.subheader("Export results")
            area_df = pd.DataFrame(
                [
                    {"Screening category": "Hotspots", "Estimated area (hectares)": round(hotspot_area_ha, 2)},
                    {"Screening category": "Tree-planting candidates", "Estimated area (hectares)": round(tree_area_ha, 2)},
                    {"Screening category": "Cool-roof candidates", "Estimated area (hectares)": round(cool_roof_area_ha, 2)},
                ]
            )
            d1, d2, d3 = st.columns(3)
            with d1:
                st.download_button(
                    "Download indicator summary (CSV)",
                    data=stats_df.to_csv(index=False).encode("utf-8"),
                    file_name="trichy_uhi_indicator_summary.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with d2:
                st.download_button(
                    "Download area estimates (CSV)",
                    data=area_df.to_csv(index=False).encode("utf-8"),
                    file_name="trichy_uhi_area_estimates.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with d3:
                if not sample_df.empty:
                    st.download_button(
                        "Download sampled pixels (CSV)",
                        data=sample_df.to_csv(index=False).encode("utf-8"),
                        file_name="trichy_uhi_sampled_pixels.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )
                else:
                    st.caption("Sample export unavailable: no valid sample pixels.")

            with st.expander("Methodology and interpretation"):
                st.markdown(
                    """
- **Cloud masking:** Landsat `QA_PIXEL` bits for fill, dilated cloud, cirrus, cloud, and cloud shadow.
- **LST:** Landsat Collection 2 Level 2 `ST_B10` scale/offset conversion, then Kelvin to Celsius.
- **NDVI:** Normalized difference of `SR_B5` and `SR_B4`.
- **NDBI:** Normalized difference of `SR_B6` and `SR_B5`.
- **Composite:** Median of cloud-masked Landsat 8 and 9 scenes within the selected dates.
- **Relative UHI:** Pixel LST minus AOI mean LST; this is a relative surface-heat indicator, not an urban-versus-rural comparison.
- **Hotspots:** Relative UHI greater than +2 °C.
- **Heat-risk classes:** 0 = at/below AOI mean; 1 = above mean to +1 °C; 2 = above +1 to +2 °C; 3 = above +2 °C.
- **Tree-planting screening:** Relative UHI > +1 °C and NDVI < 0.30.
- **Cool-roof screening:** Relative UHI > +1 °C and NDBI > 0.
- **Area estimation:** Sum of Earth Engine pixel-area values for pixels that pass each screening mask, reported in hectares. Values are approximate and depend on projection, scale, masking, and best-effort reduction settings.
                    """
                )
            st.caption(
                "Satellite land surface temperature differs from near-surface air temperature. "
                "Results depend on image availability, cloud masking, season, and selected date range."
            )

        except Exception as exc:
            st.error("The analysis did not complete. Expand technical details and share the error if you need help.")
            with st.expander("Technical details"):
                st.exception(exc)

else:
    st.info("Choose a date range and map layer in the sidebar, then select **Run UHI analysis**.")
    c1, c2, c3 = st.columns(3)
    c1.markdown("**01 · Select dates**\n\nChoose the satellite observation period.")
    c2.markdown("**02 · Explore layers**\n\nView surface temperature, vegetation, built-up, UHI, and screening masks.")
    c3.markdown("**03 · Interpret & export**\n\nReview statistics, area estimates, sampled correlations, and CSV outputs.")
