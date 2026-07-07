import streamlit as st


def show_kpi(df):
    total_revenue = df['revenue'].sum()
    total_rentals = df['rental_count'].sum()
    avg_revenue = df['revenue'].mean()
    top_category = df.groupby('category')['revenue'].sum().idxmax()

    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f"""
    <div class="kpi">
        <h3>Total Revenue</h3>
        <h2>${total_revenue:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
    <div class="kpi">
        <h3>Total Rentals</h3>
        <h2>{total_rentals:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
    <div class="kpi">
        <h3>Avg Revenue</h3>
        <h2>${avg_revenue:,.2f}</h2>
    </div>
    """, unsafe_allow_html=True)

    col4.markdown(f"""
    <div class="kpi">
        <h3>Top Category</h3>
        <h2>{top_category}</h2>
    </div>
    """, unsafe_allow_html=True)