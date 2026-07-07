import plotly.express as px
import streamlit as st

# =========================
# CARD WRAPPER
# =========================
def card_start():
    st.markdown('<div class="card">', unsafe_allow_html=True)

def card_end():
    st.markdown('</div>', unsafe_allow_html=True)


# =========================
# CHART 1: REVENUE BY CATEGORY
# =========================
def revenue_by_category(df):
    card_start()

    st.subheader("Revenue Distribution by Category")

    data = df.groupby('category')['revenue'].sum().reset_index()

    fig = px.bar(
        data,
        x='category',
        y='revenue',
        text_auto=True
    )

    fig.update_layout(
        xaxis_title="Category",
        yaxis_title="Revenue",
        template="plotly_dark"
    )

    st.plotly_chart(fig)

    card_end()


# =========================
# CHART 2: RENTAL VS REVENUE (ALL DATA)
# =========================
def rental_vs_revenue(df):
    card_start()

    st.subheader("Rental Demand vs Revenue Analysis (All Time)")

    film_agg = df.groupby('title').agg({
        'rental_count': 'sum',
        'revenue': 'sum',
        'price': 'mean'
    }).reset_index()

    fig = px.scatter(
        film_agg,
        x='rental_count',
        y='revenue',
        size='price',
        hover_name='title'
    )

    fig.update_layout(
        xaxis_title="Rental Count",
        yaxis_title="Revenue",
        template="plotly_dark"
    )

    st.plotly_chart(fig)

    card_end()


# =========================
# CHART 3: REVENUE TREND
# =========================
def revenue_trend(df):
    card_start()

    st.subheader("Revenue Trend Over Time")

    trend = df.groupby('month')['revenue'].sum().reset_index()

    fig = px.line(
        trend,
        x='month',
        y='revenue',
        markers=True
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Revenue",
        template="plotly_dark"
    )

    st.plotly_chart(fig)

    card_end()


# =========================
# CHART 4: PRICE VS DEMAND
# =========================
def price_vs_demand(df):
    card_start()

    st.subheader("Price vs Customer Demand")

    fig = px.scatter(
        df,
        x='price',
        y='rental_count',
        color='category'
    )

    fig.update_layout(
        xaxis_title="Price",
        yaxis_title="Rental Count",
        template="plotly_dark"
    )

    st.plotly_chart(fig)

    card_end()

st.markdown("<br>", unsafe_allow_html=True)