import streamlit as st
from config.database import fetch_data
from data.queries import main_query
from components.kpi import show_kpi
from components.charts import *
from components.table import show_table

st.set_page_config(layout="wide")

st.title("Content Profitability & Catalog Strategy Dashboard")

df = fetch_data(main_query)

# FILTER
months = df['month'].dropna().sort_values().unique()
selected_month = st.selectbox("Select Month", ["All"] + list(months))

if selected_month != "All":
    df_filtered = df[df['month'] == selected_month]
else:
    df_filtered = df.copy()

# KPI
show_kpi(df_filtered)

st.markdown("##")

# ROW 1
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    revenue_by_category(df_filtered)

with col2:
    rental_vs_revenue(df)

st.markdown("##")

# ROW 2
revenue_trend(df)

st.markdown("##")

# ROW 3
col3, col4 = st.columns([1, 1], gap="large")

with col3:
    price_vs_demand(df_filtered)

with col4:
    show_table(df_filtered)

st.markdown("##")

# INSIGHT
st.markdown("""
### Key Business Insights & Recommendations
- High demand does not always generate high revenue
- Pricing optimization opportunity identified
- Premium content maintains stable demand
""")