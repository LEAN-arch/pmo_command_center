# pmo_command_center/dashboards/portfolio_health.py
import streamlit as st
import pandas as pd
from utils.pmo_session_state_manager import PMOSessionStateManager
from utils.plot_utils import create_portfolio_bubble_chart

def render_portfolio_health_dashboard(ssm: PMOSessionStateManager):
    st.header("Portfolio Health Dashboard")

    projects = ssm.get_data("projects")
    qms_kpis = ssm.get_data("qms_kpis")
    if not projects:
        st.warning("No project data available.")
        return

    df = pd.DataFrame(projects)

    # --- KPIs ---
    st.subheader("Executive KPIs")
    total_budget = df['budget_usd'].sum()
    total_actuals = df['actuals_usd'].sum()
    at_risk_count = len(df[df['health_status'] == "At Risk"])
    open_capas = qms_kpis.get("open_capas", 0)

    kpi_cols = st.columns(4)
    kpi_cols[0].metric("Active Projects", len(df), help="Total number of NPD and LCM projects.")
    kpi_cols[1].metric("Projects At Risk", at_risk_count, delta=at_risk_count, delta_color="inverse")
    kpi_cols[2].metric("Portfolio Budget Burn", f"{(total_actuals / total_budget) * 100:.1f}%", f"${total_actuals:,.0f} / ${total_budget:,.0f}")
    kpi_cols[3].metric("Open CAPAs (Portfolio-wide)", open_capas, delta=open_capas, delta_color="inverse", help="A leading indicator of QMS health.")

    st.divider()

    # --- Portfolio Bubble Chart ---
    st.subheader("Portfolio Landscape: Strategy vs. Risk")
    st.info("""
    **How to read this chart:** This is a strategic view of the entire portfolio, balancing risk against strategic value.
    - **Top-Left (Green Zone):** High-value, low-risk projects. Protect and fund these.
    - **Bottom-Right (Red Zone):** Low-value, high-risk projects. Candidates for re-evaluation or de-scoping.
    - **Bubble Size:** Project Budget | **Color:** Health Status
    """, icon="💡")

    fig = create_portfolio_bubble_chart(df)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- Project Summary Table ---
    st.subheader("Project Summary Table")
    df['variance'] = df['actuals_usd'] - df['budget_usd']
    st.dataframe(
        df[['name', 'project_type', 'phase', 'pm', 'health_status', 'regulatory_path']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "project_type": st.column_config.TextColumn("Type", help="NPD = New Product Development, LCM = Lifecycle Management"),
        }
    )
