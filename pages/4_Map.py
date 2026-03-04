import streamlit as st
import pandas as pd
from utils.io import load_weather, load_wa_zip_geojson
from charts.charts import choropleth_design

# Common property names used in ZIP GeoJSON files
def detect_zip_prop(geo: dict, property_list: list) -> str:
    props = geo["features"][0]["properties"]
    for k in property_list:
        if k in props:
            return k
    raise KeyError(f"Could not find a ZIP property in {list(props.keys())}")

st.set_page_config(page_title="Choropleths with Altair", layout="wide")
st.title("Interactive Choropleth: Weather across Seattle ZIPs (Altair)")

df = load_weather()
wa_zip_geojson = load_wa_zip_geojson()


# Filter features to Seattle-like ZIPs: 981xx
ZIP_PROP_CANDIDATES = ["ZCTA5CE10", "ZCTA5CE20", "GEOID10", "GEOID"]
zip_prop = detect_zip_prop(wa_zip_geojson, ZIP_PROP_CANDIDATES)
seattle_features = [
    f for f in wa_zip_geojson["features"]
    if str(f["properties"].get(zip_prop, "")).startswith("981")
]

# Build a filtered GeoJSON FeatureCollection just for Seattle ZIPs
seattle_zip_geojson = {"type": "FeatureCollection", "features": seattle_features}
if len(seattle_features) == 0:
    st.error(
        f"No features matched ZIP prefix '981' using property '{zip_prop}'. "
        "Inspect the geojson property keys and adjust ZIP_PROP_CANDIDATES / filter."
    )
    st.stop()

st.title("Seattle Weather Map View")
st.write("Testing choropleth development on Streamlit.")

st.sidebar.header("Controls")
metric = st.sidebar.selectbox(
    "Weather metric to map",
    ["precipitation", "temp_max", "temp_min", "wind"],
    index=0
)

date_min = df["date"].min().date()
date_max = df["date"].max().date()
picked_date = st.sidebar.date_input(
    "Pick a date",
    value=date_min,
    min_value=date_min,
    max_value=date_max
)

picked_date = pd.to_datetime(picked_date)
row = df.loc[df["date"] == picked_date]
if row.empty:
    st.warning("No weather record for that date (unexpected for this dataset).")
    st.stop()
base_value = float(row.iloc[0][metric])

st.sidebar.caption(
    f"Dataset is a single Seattle time series. Base {metric} on {picked_date.date()}: {base_value:.3f}"
)

add_synthetic = st.sidebar.checkbox(
    "Add small synthetic ZIP-to-ZIP variation (for a more informative map)",
    value=True
)
synthetic_scale = st.sidebar.slider(
    "Synthetic variation scale",
    min_value=0.0,
    max_value=1.0,
    value=0.25,
    step=0.05
)

# Making a ZIP-level dataframe to join onto polygons
zip_list = sorted({str(f["properties"][zip_prop]) for f in seattle_features})
zip_df = pd.DataFrame({"zip": zip_list})
zip_df["base_metric"] = base_value

if add_synthetic:
    # Deterministic "noise" per ZIP (so the whole map isn't uniform when the dataset has no spatial signal)
    zip_int = zip_df["zip"].astype(int)
    zip_df["metric_value"] = zip_df["base_metric"] + synthetic_scale * ((zip_int % 10) - 4.5)
    zip_df["note"] = "base + synthetic ZIP effect (demo)"
else:
    zip_df["metric_value"] = zip_df["base_metric"]
    zip_df["note"] = "base only (no spatial variation)"

# Nice tooltip formatting
zip_df["metric_value"] = zip_df["metric_value"].astype(float)

st.altair_chart(choropleth_design(zip_df, seattle_zip_geojson, zip_prop, metric, picked_date), use_container_width=True)
st.markdown("**Notes:**")
st.write("- The purpose of this code was to demonstrate the integrate of altair choropleths on Streamlit.")
st.write("- The Seattle weather dataset has one measurement per day for the entire city, not per ZIP code or neighborhood. " \
            "Hence we artificially add spatial variation.")