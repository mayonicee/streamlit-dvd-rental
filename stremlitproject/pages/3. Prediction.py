import streamlit as st
import pandas as pd
import joblib

st.set_page_config(layout="wide")
st.title("Customer Prediction")

@st.cache_resource
def load_model():
    return (
        joblib.load("kmeans_customer_model.pkl"),
        joblib.load("scaler.pkl"),
        joblib.load("cluster_map.pkl")
    )

@st.cache_data
def load_data():
    df = pd.read_csv("customer_payment_dataset.csv")
    df.columns = df.columns.str.strip()

    df["recency"] = (
        pd.to_datetime("today") - pd.to_datetime(df["last_payment_date"])
    ).dt.days

    df["frequency"] = df["payment_count"]
    df["monetary"] = df["total_payment"]

    return df

kmeans, scaler, cluster_map = load_model()
df = load_data()

avg_r = df["recency"].mean()
avg_f = df["frequency"].mean()
avg_m = df["monetary"].mean()

with st.form("predict"):
    r = st.number_input("Recency", 0)
    f = st.number_input("Frequency", 0)
    m = st.number_input("Monetary", 0.0)

    submit = st.form_submit_button("Predict")

if submit:
    X = scaler.transform([[r, f, m]])
    cluster = kmeans.predict(X)[0]
    segment = cluster_map.get(cluster, "Unknown")

    st.success(f"Predicted Segment: {segment}")

    if r > avg_r:
        st.warning("High recency → churn risk")

    if f < avg_f:
        st.info("Low frequency → low engagement")

    if m > avg_m:
        st.success("High monetary → strong customer value")