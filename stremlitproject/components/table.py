import streamlit as st

def show_table(df):
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("Film Performance Details")

    # =========================
    # AGGREGATION
    # =========================
    table = df.groupby(['title', 'category']).agg({
        'rental_count': 'sum',
        'revenue': 'sum',
        'price': 'mean'
    }).reset_index()

    # =========================
    # PROFITABILITY TAG
    # =========================
    median_revenue = table['revenue'].median()

    table['profitability'] = table['revenue'].apply(
        lambda x: 'High' if x >= median_revenue else 'Low'
    )

    # =========================
    # SORTING
    # =========================
    table = table.sort_values(by='revenue', ascending=False)

    # =========================
    # DISPLAY
    # =========================
    st.dataframe(
        table,
        use_container_width=True
    )

    st.markdown('</div>', unsafe_allow_html=True)