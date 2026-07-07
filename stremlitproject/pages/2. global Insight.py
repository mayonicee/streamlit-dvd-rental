import streamlit as st
import pandas as pd
import joblib
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Global & Store Insight")

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

df = load_data()

rental_df = pd.read_csv("rental.csv").drop_duplicates()
rental_df = rental_df.merge(
    df[["customer_id", "customer_name"]],
    on="customer_id",
    how="left"
)

# GLOBAL
st.subheader("Global Insight")

genre = rental_df["genre"].value_counts().reset_index()
genre.columns = ["genre", "count"]

fig1 = px.bar(genre, x="genre", y="count", text="count")
st.plotly_chart(fig1, use_container_width=True)

top_genre = genre.iloc[0]

st.write(
    f"Top genre '{top_genre['genre']}' contributes {round((top_genre['count']/genre['count'].sum())*100,2)}% of total demand"
)

# TOP CUSTOMER
st.subheader("Top Customers")

top_customers = df.sort_values("monetary", ascending=False).head(10)

fig_top = px.bar(
    top_customers,
    x="customer_name",
    y="monetary",
    text="monetary"
)

st.plotly_chart(fig_top, use_container_width=True)

total_revenue = df["monetary"].sum()
top_revenue = top_customers["monetary"].sum()

st.write(
    f"Top 10 customers contribute {round((top_revenue/total_revenue)*100,2)}% of total revenue"
)

# STORE
st.subheader("Store Performance")

store_customer = df.groupby("store_id")["customer_id"].nunique().reset_index()
store_customer.columns = ["store_id", "total_customer"]

fig_store_customer = px.bar(
    store_customer,
    x="store_id",
    y="total_customer",
    text="total_customer",
    title="Total Customers per Store"
)

st.plotly_chart(fig_store_customer, use_container_width=True)

top_store_customer = store_customer.loc[store_customer["total_customer"].idxmax()]
total_customer_all = store_customer["total_customer"].sum()

st.write(
    f"Store {top_store_customer['store_id']} has the highest customer base "
    f"with {top_store_customer['total_customer']} customers "
    f"({round((top_store_customer['total_customer']/total_customer_all)*100,2)}% of total)"
)

store_val = df.groupby("store_id")["monetary"].mean().reset_index()

fig_store = px.bar(store_val, x="store_id", y="monetary", text="monetary")
st.plotly_chart(fig_store, use_container_width=True)

best_store = store_val.loc[store_val["monetary"].idxmax()]

st.write(
    f"Store {best_store['store_id']} has highest avg revenue ({round(best_store['monetary'],2)})"
)