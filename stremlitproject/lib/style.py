import streamlit as st


def apply_dark_theme() -> None:
    st.markdown(
        """
<style>
    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --secondary: #ec4899;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --dark-bg: #0b1220;
        --card-bg: #111b2e;
        --border: #23314a;
        --text-primary: #f1f5f9;
        --text-secondary: #cbd5e1;
    }

    body, .main {
        background-color: var(--dark-bg);
        color: var(--text-primary);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    }

    [data-testid="stSidebar"] {
        background-color: var(--dark-bg);
        border-right: 1px solid var(--border);
    }

    .stMetric {
        background: linear-gradient(135deg, var(--card-bg) 0%, rgba(17, 27, 46, 0.55) 100%);
        padding: 18px;
        border-radius: 12px;
        border: 1px solid var(--border);
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.30);
    }

    .stMetricLabel {
        font-size: 0.82rem;
        color: var(--text-secondary);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }

    .stMetricValue {
        font-size: 1.95rem;
        font-weight: 800;
        color: var(--text-primary);
    }

    .card {
        background: linear-gradient(135deg, var(--card-bg) 0%, rgba(17, 27, 46, 0.55) 100%);
        padding: 22px;
        border-radius: 12px;
        border: 1px solid var(--border);
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.30);
    }

    .insight-box {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.10) 0%, rgba(236, 72, 153, 0.05) 100%);
        border-left: 3px solid var(--primary);
        padding: 14px 16px;
        border-radius: 10px;
        margin-top: 14px;
        font-size: 0.95rem;
        color: var(--text-secondary);
    }

    .recommendation-card {
        background: linear-gradient(135deg, var(--card-bg) 0%, rgba(17, 27, 46, 0.55) 100%);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 14px;
    }

    .recommendation-card h4 {
        color: var(--primary);
        margin-bottom: 8px;
        font-weight: 700;
    }

    h1, h2, h3 {
        color: var(--text-primary) !important;
    }

    h2 {
        border-bottom: 2px solid var(--primary);
        padding-bottom: 10px;
    }
</style>
        """,
        unsafe_allow_html=True,
    )


def sidebar_branding() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align:center; padding: 18px 0 10px 0;">
                <div style="font-size: 2.1rem; font-weight: 900;">🎬</div>
                <div style="font-size: 1.15rem; font-weight: 800; margin-top: 6px;">DVD Rental</div>
                <div style="font-size: 0.88rem; color: #cbd5e1;">Analytics Dashboard</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()