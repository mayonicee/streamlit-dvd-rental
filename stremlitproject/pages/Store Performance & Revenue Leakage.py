import pandas as pd
import plotly.express as px
import streamlit as st

from lib.data import load_data
from lib.style import apply_dark_theme


def money(value: float) -> str:
    return f"${value:,.2f}"


st.set_page_config(
    page_title="Store Performance & Revenue Leakage",
    page_icon="🏬",
    layout="wide",
    initial_sidebar_state="collapsed",
)
apply_dark_theme()

st.markdown(
    """
<style>
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

.block { padding: 8px 0 14px 0; }
</style>
""",
    unsafe_allow_html=True,
)

bundle = load_data(prefer_postgres=True)
rental = bundle.rental.copy()
payment = bundle.payment.copy()

if rental.empty:
    st.error("No rental data found.")
    st.stop()

rental["store_id"] = rental["store_id"].astype(int)
payment["rental_id"] = payment["rental_id"].astype(int)

payment_joined = payment.merge(rental[["rental_id", "store_id", "customer_id"]], on="rental_id", how="inner")

base = (
    rental.groupby("store_id")
    .agg(
        total_rentals=("rental_id", "count"),
        active_customers=("customer_id", "nunique"),
    )
    .reset_index()
)

pay = (
    payment_joined.groupby("store_id")
    .agg(
        total_payments=("payment_id", "count"),
        total_revenue=("amount", "sum"),
    )
    .reset_index()
)

kpi = base.merge(pay, on="store_id", how="left").fillna({"total_payments": 0, "total_revenue": 0.0})
kpi["rentals_per_customer"] = (kpi["total_rentals"] / kpi["active_customers"].replace(0, pd.NA)).fillna(0.0)
kpi["rental_to_payment_rate"] = (kpi["total_payments"] / kpi["total_rentals"].replace(0, pd.NA)).fillna(0.0)
kpi["avg_payment_value"] = (kpi["total_revenue"] / kpi["total_payments"].replace(0, pd.NA)).fillna(0.0)
kpi = kpi.sort_values("store_id").reset_index(drop=True)

# Defaults for 2-store comparison layout
store_ids = sorted(kpi["store_id"].tolist())
has_two_stores = len(store_ids) >= 2
if has_two_stores:
    store1 = kpi[kpi["store_id"] == store_ids[0]].iloc[0]
    store2 = kpi[kpi["store_id"] == store_ids[1]].iloc[0]

# Title
st.title("Store Performance & Revenue Leakage")
st.caption("Based on rental & payment transactions only")

with st.container():
    # 1) Basic Data Overview
    st.markdown("### 1. Basic Data Overview")
    o1, o2, o3 = st.columns(3)
    with o1:
        st.metric("Total Rentals", f"{int(kpi['total_rentals'].sum()):,}")
    with o2:
        st.metric("Total Payments", f"{int(kpi['total_payments'].sum()):,}")
    with o3:
        st.metric("Total Active Customers", f"{int(kpi['active_customers'].sum()):,}")
    st.caption("Core transaction metrics by store")

with st.container():
    # 2) Store Performance Snapshot
    st.markdown("### 2. Store Performance Snapshot")
    if has_two_stores:
        s1_col, s2_col = st.columns(2)
        with s1_col:
            st.subheader(f"Store #{int(store1['store_id'])}")
            m11, m12 = st.columns(2)
            with m11:
                st.metric("Revenue", money(float(store1["total_revenue"])))
                st.metric("Rentals", f"{int(store1['total_rentals']):,}")
            with m12:
                st.metric("Customers", f"{int(store1['active_customers']):,}")
                st.metric("Rental-to-Payment Rate", f"{100 * float(store1['rental_to_payment_rate']):.2f}%")
        with s2_col:
            st.subheader(f"Store #{int(store2['store_id'])}")
            m21, m22 = st.columns(2)
            with m21:
                st.metric("Revenue", money(float(store2["total_revenue"])))
                st.metric("Rentals", f"{int(store2['total_rentals']):,}")
            with m22:
                st.metric("Customers", f"{int(store2['active_customers']):,}")
                st.metric("Rental-to-Payment Rate", f"{100 * float(store2['rental_to_payment_rate']):.2f}%")
    else:
        st.info("Store comparison needs at least two stores.")
    st.caption("Store #2 shows lower payment completion efficiency")

with st.container():
    # 3) Store Comparison Visuals
    st.markdown("### 3. Store Comparison Visuals")
    v1, v2, v3 = st.columns(3)
    with v1:
        fig_rev = px.bar(
            kpi,
            x="store_id",
            y="total_revenue",
            labels={"store_id": "Store", "total_revenue": "Revenue"},
            title="Revenue per store",
            color="store_id",
        )
        fig_rev.update_layout(showlegend=False)
        st.plotly_chart(fig_rev, use_container_width=True)
    with v2:
        rent_cust = kpi.melt(
            id_vars="store_id",
            value_vars=["total_rentals", "active_customers"],
            var_name="Metric",
            value_name="Count",
        )
        rent_cust["Metric"] = rent_cust["Metric"].map({"total_rentals": "Rentals", "active_customers": "Customers"})
        fig_rc = px.bar(
            rent_cust,
            x="store_id",
            y="Count",
            color="Metric",
            barmode="group",
            labels={"store_id": "Store"},
            title="Rentals vs customers",
        )
        st.plotly_chart(fig_rc, use_container_width=True)
    with v3:
        fig_rate = px.bar(
            kpi,
            x="store_id",
            y="rental_to_payment_rate",
            labels={"store_id": "Store", "rental_to_payment_rate": "Rate"},
            title="Payment completion rate",
            color="store_id",
        )
        fig_rate.update_yaxes(tickformat=".0%")
        fig_rate.update_layout(showlegend=False)
        st.plotly_chart(fig_rate, use_container_width=True)
    st.caption("Revenue gap driven by lower completion rate")

with st.container():
    # 4) Transaction Flow
    st.markdown("### 4. Transaction Flow")
    flow_rows = []
    for _, row in kpi.iterrows():
        sid = int(row["store_id"])
        flow_rows.extend(
            [
                {"Store": f"Store #{sid}", "Stage": "Customers", "Count": int(row["active_customers"])},
                {"Store": f"Store #{sid}", "Stage": "Rentals", "Count": int(row["total_rentals"])},
                {"Store": f"Store #{sid}", "Stage": "Payments", "Count": int(row["total_payments"])},
            ]
        )
    flow_df = pd.DataFrame(flow_rows)
    fig_flow = px.funnel(flow_df, x="Count", y="Stage", color="Store")
    st.plotly_chart(fig_flow, use_container_width=True)
    st.caption("Drop occurs between rentals and payments")

with st.container():
    # 5) Revenue vs Customers
    st.markdown("### 5. Revenue vs Customers")
    fig_scatter = px.scatter(
        kpi,
        x="active_customers",
        y="total_revenue",
        size="total_rentals",
        color="store_id",
        text=kpi["store_id"].astype(int).map(lambda x: f"Store #{x}"),
        labels={"active_customers": "Active Customers", "total_revenue": "Revenue", "store_id": "Store"},
    )
    fig_scatter.update_traces(textposition="top center")
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.caption("Store #2 generates less revenue per customer")

with st.container():
    # 6) Revenue Efficiency Analysis
    st.markdown("### 6. Revenue Efficiency Analysis")
    efficiency = kpi.rename(
    columns={
        "store_id": "Store",
        "total_rentals": "Total Rentals",
        "total_payments": "Total Payments",
        "total_revenue": "Total Revenue",
        "active_customers": "Active Customers",
        "rentals_per_customer": "Rentals per Customer",
        "rental_to_payment_rate": "Rental-to-Payment Rate",
        "avg_payment_value": "Average Payment Value",
    }
).copy()
    efficiency["Rental-to-Payment Rate"] = efficiency["Rental-to-Payment Rate"].map(lambda x: f"{x * 100:.2f}%")
    efficiency["Average Payment Value"] = efficiency["Average Payment Value"].map(money)
    st.dataframe(efficiency, use_container_width=True, hide_index=True)
    st.markdown("- Store #2: lower payment completion")
    st.markdown("- Store #1: lower average payment")

with st.container():
    # 7) Revenue Opportunity
    st.markdown("### 7. 💰 Revenue Opportunity")
    if has_two_stores:
        expected_revenue = float(store2["total_rentals"]) * float(store1["rental_to_payment_rate"]) * float(store2["avg_payment_value"])
        actual_revenue = float(store2["total_revenue"])
        opportunity = expected_revenue - actual_revenue
        g1, g2, g3 = st.columns(3)
        with g1:
            st.metric("Expected Revenue", money(expected_revenue))
        with g2:
            st.metric("Actual Revenue", money(actual_revenue))
        with g3:
            st.metric("Opportunity Gap", money(opportunity))
    else:
        st.info("Opportunity view needs at least two stores.")
    st.caption("Potential gain if Store #2 matches Store #1")

with st.container():
    # 8) Actionable Recommendations
    st.markdown("### 8. Actionable Recommendations")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Improve Payment Completion**")
        st.markdown("- Standardize follow-up")
        st.markdown("- Monitor completion rate")
    with c2:
        st.markdown("**Increase Average Payment**")
        st.markdown("- Promote bundles")
        st.markdown("- Optimize pricing mix")
    with c3:
        st.markdown("**Operational Improvements**")
        st.markdown("- Benchmark Store #1")
        st.markdown("- Track store KPIs")
        st.markdown("""
<style>
[data-testid="stSidebar"] { display: block !important; }
[data-testid="stSidebarNav"] { display: block !important; }
</style>
""", unsafe_allow_html=True)