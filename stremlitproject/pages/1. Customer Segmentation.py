import streamlit as st
import pandas as pd
import joblib
import plotly.express as px

st.set_page_config(layout="wide")

st.title("Customer Segmentation & Recommendation")


# LOAD MODEL

@st.cache_resource
def load_model():
    return (
        joblib.load("kmeans_customer_model.pkl"),
        joblib.load("scaler.pkl"),
        joblib.load("cluster_map.pkl")
    )


# LOAD DATA

@st.cache_data
def load_data():
    df = pd.read_csv("customer_payment_dataset.csv")
    df.columns = df.columns.str.strip()

    if "customer_name" not in df.columns:
        st.error("customer_name tidak ditemukan di CSV")
        st.stop()

    df["recency"] = (
        pd.to_datetime("today") - pd.to_datetime(df["last_payment_date"])
    ).dt.days

    df["frequency"] = df["payment_count"]
    df["monetary"] = df["total_payment"]

    return df

kmeans, scaler, cluster_map = load_model()
df = load_data()


# LOAD RENTAL

rental_df = pd.read_csv("rental.csv").drop_duplicates()

rental_df = rental_df.merge(
    df[["customer_id", "customer_name"]],
    on="customer_id",
    how="left"
)

# CLUSTERING

X_scaled = scaler.transform(df[["recency", "frequency", "monetary"]])
df["cluster"] = kmeans.predict(X_scaled)
df["segment"] = df["cluster"].map(cluster_map)

# SIDEBAR FILTER ✅ PINDAH SINI

st.sidebar.header("Filter")

segment_filter = st.sidebar.multiselect(
    "Segment",
    ["High Value", "Mid Value", "Low Value"],
    default=["High Value", "Mid Value", "Low Value"]
)

min_monetary = st.sidebar.slider(
    "Minimum Monetary",
    0,
    int(df["monetary"].max()),
    0
)

st.sidebar.markdown("---")

# APPLY FILTER

filtered_df = df[
    (df["segment"].isin(segment_filter)) &
    (df["monetary"] >= min_monetary)
]

if filtered_df.empty:
    st.warning("No data available")
    st.stop()

# KPI

st.subheader("Key Metrics")

col1, col2, col3 = st.columns(3)
col1.metric("Total Customers", len(filtered_df))
col2.metric("Avg Monetary", round(filtered_df["monetary"].mean(), 2))
col3.metric("Avg Frequency", round(filtered_df["frequency"].mean(), 2))

st.divider()


# SEGMENT DISTRIBUTION

seg = filtered_df["segment"].value_counts().reset_index()
seg.columns = ["segment", "count"]

fig = px.pie(seg, names="segment", values="count")
st.plotly_chart(fig, use_container_width=True)


# CUSTOMER TABLE

st.subheader("Customer Data")

st.dataframe(filtered_df[
    ["customer_name", "recency", "frequency", "monetary", "segment"]
])


# CUSTOMER DETAIL

st.subheader("Customer Detail")

selected_name = st.selectbox("Select Customer", filtered_df["customer_name"])
selected = filtered_df[filtered_df["customer_name"] == selected_name].iloc[0]
selected_id = selected["customer_id"]

st.write(selected)


# BUSINESS INSIGHT (DATA BASED) 
st.subheader("Business Insight")

avg_r = filtered_df["recency"].mean()
avg_f = filtered_df["frequency"].mean()
avg_m = filtered_df["monetary"].mean()

st.write(f"Recency: {selected['recency']} (avg: {round(avg_r,2)})")
st.write(f"Frequency: {selected['frequency']} (avg: {round(avg_f,2)})")
st.write(f"Monetary: {selected['monetary']} (avg: {round(avg_m,2)})")

if selected["recency"] > avg_r:
    st.warning("Above-average recency → higher churn probability")
else:
    st.success("Below-average recency → active customer")

if selected["frequency"] > avg_f:
    st.success("Above-average frequency → strong engagement")
else:
    st.info("Below-average frequency → weak engagement")

if selected["monetary"] > avg_m:
    st.success("Above-average monetary → high revenue contribution")
else:
    st.warning("Below-average monetary → low contribution")


# CUSTOMER PREFERENCE

st.subheader("Customer Preference")

cust_data = rental_df[rental_df["customer_id"] == selected_id]

if not cust_data.empty:
    genres = cust_data["genre"].value_counts().head(3)
    actors = cust_data["actor"].value_counts().head(3)

    st.write("Top Genres:", ", ".join(genres.index))
    st.write("Top Actors:", ", ".join(actors.index))
else:
    st.warning("No preference data")


# RECOMMENDATION

st.subheader("Film Recommendation")

if cust_data.empty:
    recs = rental_df["title"].value_counts().head(5)

    for i, (title, _) in enumerate(recs.items(), 1):
        st.write(f"{i}. {title}")
        st.caption("Popular movie")

else:
    fav_genres = cust_data["genre"].value_counts().index.tolist()

    recs = rental_df[rental_df["genre"].isin(fav_genres)]
    recs = recs[~recs["title"].isin(cust_data["title"])]

    if recs.empty:
        recs = rental_df.copy()

    recs = recs.drop_duplicates(subset=["title"]).sample(frac=1).head(5)

    for i, row in enumerate(recs.itertuples(), 1):
        st.write(f"{i}. {row.title}")
        st.caption(
            f"Becasue customer showing some interset on this {row.genre} genre, "
            f"so we recomending the same genre which is {row.genre} to this customer"
        )