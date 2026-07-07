import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
import warnings

# Suppress pandas warning about raw psycopg2 connection
warnings.filterwarnings('ignore', category=UserWarning)

# ======================
# PAGE CONFIG
# ======================
st.set_page_config(
    page_title="Engagement & Timing Analysis",
    page_icon="💸",
    layout="wide"
)

# ======================
# STYLE 
# ======================
st.markdown("""
<style>
.metric-card {
    background-color: #1f2937;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    color: white;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
}
.metric-title {
    font-size: 16px;
    color: #9ca3af;
    margin-bottom: 5px;
}
.metric-value {
    font-size: 28px;
    font-weight: bold;
    color: #10b981;
}
.metric-sub {
    font-size: 12px;
    color: #cbd5e1;
}
.insight-card {
    background-color: #374151;
    border-top: 5px solid #3b82f6;
    padding: 20px;
    border-radius: 8px;
    height: 100%;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}
.insight-title {
    font-weight: bold;
    font-size: 16px;
    color: #93c5fd;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.insight-text {
    font-size: 14px;
    color: #e5e7eb;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# ======================
# DATA CONNECTION & CACHE
# ======================
@st.cache_data
def load_data(query):
    conn = psycopg2.connect(
        host="localhost",
        database="dvdrental",
        user="postgres",
        password="rahmamaya"
    )
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ======================
# QUERIES
# ======================

kpi_query = """
SELECT 
    (SELECT COUNT(*) FROM customer) as total_customer,
    (SELECT COUNT(*) FROM rental) as total_rental,
    (SELECT SUM(amount) FROM payment) as total_revenue,
    (SELECT COUNT(*) FROM customer WHERE activebool = true) as active_customer,
    (SELECT COUNT(*) FROM customer WHERE activebool = false) as inactive_customer
"""
kpi_data = load_data(kpi_query).iloc[0]

rental_by_day_query = """
SELECT 
    TRIM(TO_CHAR(rental_date, 'Day')) AS day_name,
    EXTRACT(ISODOW FROM rental_date) as day_num,
    COUNT(rental_id) AS total_rentals
FROM rental
GROUP BY day_name, day_num
ORDER BY day_num
"""
rental_by_day = load_data(rental_by_day_query)

rental_by_hour_query = """
SELECT 
    EXTRACT(HOUR FROM rental_date) AS hour_of_day, 
    COUNT(rental_id) AS total_rentals
FROM rental
GROUP BY hour_of_day
ORDER BY hour_of_day
"""
rental_by_hour = load_data(rental_by_hour_query)

revenue_by_day_query = """
SELECT 
    TRIM(TO_CHAR(payment_date, 'Day')) AS day_name,
    EXTRACT(ISODOW FROM payment_date) as day_num,
    SUM(amount) AS total_revenue
FROM payment
GROUP BY day_name, day_num
ORDER BY day_num
"""
revenue_by_day = load_data(revenue_by_day_query)

revenue_by_hour_query = """
SELECT 
    EXTRACT(HOUR FROM payment_date) AS hour_of_day, 
    SUM(amount) AS total_revenue
FROM payment
GROUP BY hour_of_day
ORDER BY hour_of_day
"""
revenue_by_hour = load_data(revenue_by_hour_query)

rental_rev_comparison_query = """
SELECT 
    TRIM(TO_CHAR(r.rental_date, 'Day')) AS day_name,
    EXTRACT(ISODOW FROM r.rental_date) as day_num,
    COUNT(DISTINCT r.rental_id) AS total_rentals,
    SUM(p.amount) AS total_revenue
FROM rental r
LEFT JOIN payment p ON r.rental_id = p.rental_id
GROUP BY day_name, day_num
ORDER BY day_num
"""
rental_rev = load_data(rental_rev_comparison_query)

engagement_query = """
SELECT 
    EXTRACT(HOUR FROM rental_date) AS hour_of_day,
    CASE WHEN EXTRACT(ISODOW FROM rental_date) IN (6, 7) THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    COUNT(rental_id) AS total_rentals
FROM rental
GROUP BY hour_of_day, day_type
ORDER BY hour_of_day, day_type
"""
engagement = load_data(engagement_query)

# ======================
# GENERATE PLOTLY FIGURES
# ======================
fig_rent_day = px.bar(rental_by_day, x="day_name", y="total_rentals", color="total_rentals", labels={"day_name": "Day", "total_rentals": "Number of Rentals"}, color_continuous_scale="Blues")
fig_rev_day = px.bar(revenue_by_day, x="day_name", y="total_revenue", color="total_revenue", labels={"day_name": "Day", "total_revenue": "Total Revenue ($)"}, color_continuous_scale="Greens")
fig_rent_hour = px.line(rental_by_hour, x="hour_of_day", y="total_rentals", markers=True, labels={"hour_of_day": "Hour (24H)", "total_rentals": "Number of Rentals"})
fig_rent_hour.update_traces(line_color="#3b82f6", line_width=3)
fig_rent_hour.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=2))
fig_rev_hour = px.line(revenue_by_hour, x="hour_of_day", y="total_revenue", markers=True, labels={"hour_of_day": "Hour (24H)", "total_revenue": "Total Revenue ($)"})
fig_rev_hour.update_traces(line_color="#10b981", line_width=3)
fig_rev_hour.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=2))

fig_dual = go.Figure()
fig_dual.add_trace(go.Bar(x=rental_rev['day_name'], y=rental_rev['total_rentals'], name="Total Rentals", marker_color='#3b82f6', yaxis='y'))
fig_dual.add_trace(go.Scatter(x=rental_rev['day_name'], y=rental_rev['total_revenue'], name="Revenue ($)", mode='lines+markers', marker_color='#10b981', line=dict(width=3), yaxis='y2'))
fig_dual.update_layout(
    yaxis=dict(title=dict(text="Total Rental Transactions", font=dict(color="#3b82f6")), tickfont=dict(color="#3b82f6")),
    yaxis2=dict(title=dict(text="Total Revenue ($)", font=dict(color="#10b981")), tickfont=dict(color="#10b981"), anchor="free", overlaying="y", side="right", position=1),
    hovermode="x unified"
)

fig_engage = px.area(engagement, x="hour_of_day", y="total_rentals", color="day_type", line_group="day_type", labels={"hour_of_day": "Hour (24H)", "total_rentals": "Number of Rentals", "day_type": "Day Type"}, color_discrete_map={"Weekend": "#f59e0b", "Weekday": "#8b5cf6"})
fig_engage.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=2))

# ======================
# LAYOUT UTAMA (SCROLL MEMANJANG BEBAS SIDEBAR)
# ======================

st.title("📊 Customer Engagement & Rental Timing Analysis")
st.markdown("This visualization explores how rental trends directly correlate with business optimization.")
st.markdown("---")

# 1. KPI
st.subheader("👥 Overview Activity")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'''<div class="metric-card"><div class="metric-title">Total Customers</div><div class="metric-value">{int(kpi_data["total_customer"]):,}</div><div class="metric-sub">👤 Active: {int(kpi_data["active_customer"])} | ❌ Inactive: {int(kpi_data["inactive_customer"])}</div></div>''', unsafe_allow_html=True)
with col2:
    st.markdown(f'''<div class="metric-card"><div class="metric-title">Total Rental Transactions</div><div class="metric-value">{int(kpi_data["total_rental"]):,}</div><div class="metric-sub">📽️ DVD Borrows</div></div>''', unsafe_allow_html=True)
with col3:
    st.markdown(f'''<div class="metric-card"><div class="metric-title">Total Revenue</div><div class="metric-value">${kpi_data["total_revenue"]:,.2f}</div><div class="metric-sub">💸 Lifetime Sales</div></div>''', unsafe_allow_html=True)
with col4:
    active_pct = int(kpi_data["active_customer"]) / int(kpi_data["total_customer"]) * 100
    st.markdown(f'''<div class="metric-card"><div class="metric-title">Customer Retention</div><div class="metric-value">{active_pct:.1f}%</div><div class="metric-sub">🎯 Active User Ratio</div></div>''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 2. RENTAL & REVENUE TRENDS (Side-by-side per row)
st.subheader("⏰ Timing Trends (Daily & Hourly)")
c1, c2 = st.columns(2)
with c1:
    st.markdown("**Rental Activity by Day**")
    st.plotly_chart(fig_rent_day, use_container_width=True)
with c2:
    st.markdown("**Revenue by Day**")
    st.plotly_chart(fig_rev_day, use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    st.markdown("**Rental Activity by Hour**")
    st.plotly_chart(fig_rent_hour, use_container_width=True)
with c4:
    st.markdown("**Revenue by Hour**")
    st.plotly_chart(fig_rev_hour, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# 3. COMPARISON & PATTERn
st.subheader("⚖️ Customer Engagement Comparative Analysis")
st.plotly_chart(fig_dual, use_container_width=True)
st.markdown("*This analysis aims to comparatively observe whether high rental transaction volumes directly correlate with high revenue. If the green revenue line is significantly higher than the blue volume bar, it indicates premium or higher-priced items were rented more on that day.*")

# Render table (Table 3)
st.markdown("**📋 Daily Figures Breakdown Table (Raw Data):**")
st.dataframe(
    rental_rev.rename(columns={
        'day_name': 'Day',
        'total_rentals': 'Transaction Volume',
        'total_revenue': 'Total Revenue ($)'
    }).drop(columns=['day_num']).style.format({'Total Revenue ($)': '{:,.2f}'}),
    use_container_width=True,
    hide_index=True
)

st.markdown("<br>", unsafe_allow_html=True)

st.subheader("🎯 Customer Engagement Pattern (Weekday vs Weekend by Hour)")
st.plotly_chart(fig_engage, use_container_width=True)


# 4. KEY INSIGHTS (3 CARDS in 3 COLUMNS)
st.markdown("---")
st.subheader("🔑 Key Insights (Business Recommendations)")
st.markdown("Below is a summary of business decision-making insights based on the visualization trends above:")

k1, k2, k3 = st.columns(3)

with k1:
    st.markdown("""
    <div class="insight-card">
        <div class="insight-title">📈 1. Active Rental Patterns</div>
        <div class="insight-text">
            Based on daily time trends, rental peaks frequently shift between the afternoon and late nights. 
            This pattern is crucial as a benchmark for optimal employee shift scheduling to adequately serve rental spikes during busy hours.
        </div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown("""
    <div class="insight-card">
        <div class="insight-title">💵 2. Quality vs Quantity</div>
        <div class="insight-text">
            Looking at the Comparative Chart, a booming rental volume <b>does not always guarantee</b> the highest revenue. 
            This indicates that on certain days customers prefer renting cheaper classic movies, while on other days they actively rent premium new releases.
        </div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown("""
    <div class="insight-card">
        <div class="insight-title">👥 3. Strategic Promotion</div>
        <div class="insight-text">
            There is a drastic activity gap during night hours between Weekends and Weekdays.
            The optimal strategy is to introduce a discounted "Happy Hour" promo during quiet weekday afternoons and a premium "Weekend Combo" pricing for Saturday nights.
        </div>
    </div>
    """, unsafe_allow_html=True)