# streamlit_app.py

import streamlit as st
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import plotly.express as px

# ---------------------
# Database Connection
# ---------------------
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "food_waste_db"
DB_USER = "postgres"
DB_PASS = "anuradha24"  # your password

@st.cache_data
def load_data():
    try:
        engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        
        # Load tables
        food_df = pd.read_sql("SELECT * FROM food_listings;", engine)
        providers_df = pd.read_sql("SELECT * FROM providers;", engine)
        receivers_df = pd.read_sql("SELECT * FROM receivers;", engine)
        claims_df = pd.read_sql("SELECT * FROM claims;", engine)
        
        # Standardize column names
        food_df.columns = food_df.columns.str.strip().str.lower()
        providers_df.columns = providers_df.columns.str.strip().str.lower()
        receivers_df.columns = receivers_df.columns.str.strip().str.lower()
        claims_df.columns = claims_df.columns.str.strip().str.lower()
        
        return food_df, providers_df, receivers_df, claims_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# ---------------------
# Streamlit Page Setup
# ---------------------
st.set_page_config(page_title="Local Food Wastage Dashboard", layout="wide")
st.title("🍏 Local Food Wastage Management System")

# Load Data
food_df, providers_df, receivers_df, claims_df = load_data()
if food_df.empty:
    st.warning("No data loaded. Please check your database connection and table.")
    st.stop()

# ---------------------
# Data Overview
# ---------------------
st.subheader("Data Preview")
st.dataframe(food_df.head())

col1, col2, col3 = st.columns(3)
col1.metric("Total Listings", len(food_df))
col2.metric("Total Quantity", food_df["quantity"].sum())
col3.metric("Unique Food Types", food_df["food_type"].nunique())

# ---------------------
# Filters
# ---------------------
st.sidebar.header("Filters")
category_filter = st.sidebar.multiselect(
    "Select Food Type",
    options=food_df["food_type"].unique(),
    default=None
)
location_filter = st.sidebar.multiselect(
    "Select Location",
    options=food_df["location"].unique(),
    default=None
)
meal_filter = st.sidebar.multiselect(
    "Select Meal Type",
    options=food_df["meal_type"].unique(),
    default=None
)

filtered_food = food_df.copy()
if category_filter:
    filtered_food = filtered_food[filtered_food["food_type"].isin(category_filter)]
if location_filter:
    filtered_food = filtered_food[filtered_food["location"].isin(location_filter)]
if meal_filter:
    filtered_food = filtered_food[filtered_food["meal_type"].isin(meal_filter)]

# ---------------------
# Charts
# ---------------------
st.subheader("📊 Food Data Visualizations")

if "food_type" in filtered_food.columns:
    fig_type = px.histogram(filtered_food, x="food_type", title="Food Listings by Type", color="food_type")
    st.plotly_chart(fig_type, use_container_width=True)

if "location" in filtered_food.columns:
    fig_loc = px.histogram(filtered_food, x="location", title="Food Listings by Location", color="location")
    st.plotly_chart(fig_loc, use_container_width=True)

if "meal_type" in filtered_food.columns:
    fig_meal = px.histogram(filtered_food, x="meal_type", title="Food Listings by Meal Type", color="meal_type")
    st.plotly_chart(fig_meal, use_container_width=True)

if "expiry_date" in filtered_food.columns:
    filtered_food["expiry_date"] = pd.to_datetime(filtered_food["expiry_date"], errors="coerce")
    fig_expiry = px.histogram(filtered_food, x="expiry_date", title="Expiry Dates Distribution")
    st.plotly_chart(fig_expiry, use_container_width=True)

# ---------------------
# Map Visualization
# ---------------------
st.subheader("📍 Food Availability Map")

# Dummy lat/lon assignment for all unique locations
import random
locations = filtered_food["location"].unique()
city_coords = {loc: {"lat": random.uniform(-90, 90), "lon": random.uniform(-180, 180)} for loc in locations}

filtered_food["lat"] = filtered_food["location"].map(lambda x: city_coords[x]["lat"])
filtered_food["lon"] = filtered_food["location"].map(lambda x: city_coords[x]["lon"])

map_df = filtered_food.dropna(subset=["lat", "lon"])
if not map_df.empty:
    fig_map = px.scatter_map(
        map_df,
        lat="lat",
        lon="lon",
        hover_name="food_name",
        hover_data=["quantity", "provider_type", "meal_type"],
        color="food_type",
        size="quantity",
        zoom=3,
        height=500,
        title="Food Listings by Location"
    )
    fig_map.update_layout(map_style="open-street-map")
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("No location data available for map visualization.")

# ---------------------
# Download Filtered Data
# ---------------------
st.subheader("📥 Download Filtered Data")
csv = filtered_food.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download as CSV",
    data=csv,
    file_name="filtered_food_listings.csv",
    mime="text/csv",
)

st.success("Analysis complete ✅")
