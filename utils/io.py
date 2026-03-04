import streamlit as st
import pandas as pd
import json
from vega_datasets import data
from urllib.request import urlopen

@st.cache_data
def load_weather() -> pd.DataFrame:
    """
    Loads Seattle Weather Data.
    """
    df = data.seattle_weather()
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%b")
    return df

"""
# First load WA ZIP GeoJSON, we will then filter out Seattle ZIPs (981xx)
# Source: OpenDataDE State-zip-code-GeoJSON repo
"""

WA_ZIP_GEOJSON_URL = (
    "https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master/wa_washington_zip_codes_geo.min.json"
)

@st.cache_data
def load_wa_zip_geojson() -> dict:
    with urlopen(WA_ZIP_GEOJSON_URL) as wazip:
        return json.load(wazip)