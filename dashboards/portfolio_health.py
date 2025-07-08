# pmo_command_center/dashboards/1_portfolio_dashboard.py
"""
This module renders the main Portfolio Dashboard, which serves as the executive
summary for the entire project portfolio. It provides at-a-glance KPIs, a strategic
view of projects, and a summary table.
"""
import streamlit as st
import pandas as pd
from utils.pmo_session_state_manager import SPMOSessionStateManager
from utils.plot_utils import create_portfolio_bubble_chart

def render_portfolio_dashboard(ssm: SPMOSessionStateManager):
    """Renders the main executive-level portfolio health dashboard."""
    st.header("📊 Portfolio Dashboard")
    st.caption("This dashboard provides an executive-level summary of the entire project portfolio, integrating project status with key QMS compliance indicators.")

    projects = ssm.get_data("projects")
    qms_kpis = ssm.get_data("qms_kpis")
    if not projects:
        st.warning("No project data available.")
        return

    df = pd.DataFrame(projects)
    active_df = df[df['health_status'] != "Completed"]

    # --- KPIs ---
    st.subheader("Executive KPIs")
    total_budget = df['budget_usd'].sum()
    total_actuals = df['actuals_usd'].sum()
    at_risk_count = len(active_df[active_df['health_status'] == "At Risk"])
    open_capas = qms_kpis.get("open_capas", 0)

    kpi_cols = st.columns(4)
    kpi_cols[0].metric("Active Projects", len(active_df), help="Total number of active NPD and LCM projects.")
    kpi_cols[1].metric("Projects At Risk", at_risk_count, delta=at_risk_count, delta_color="inverse", help="Projects with significant issues impacting scope, schedule, or budget.")
    kpi_cols[2].metric("Portfolio Budget Burn", f"{(total_actuals / total_budget) * 100:.1f}%", f"${total_actuals:,.0f} / ${total_budget:,.0f}")
    kpi_cols[3].metric("Open CAPAs (Portfolio-wide)", open_capas, delta=qms_kpis.get("overdue_capas", 0), delta_color="inverse", help=f"A leading indicator of QMS health. {qms_kpis.get('overdue_capas', 0)} are overdue.")

    st.divider()

    # --- Portfolio Bubble Chart ---
    st.subheader("Portfolio Landscape: Strategy vs. Risk")
    st.info("""
    **How to read this chart:** This is a strategic view of the entire portfolio, balancing project risk against strategic value to the business.
    - **Top-Left (Green Zone):** High-value, low-risk projects. These are our best investments and should be protected and fully resourced.
    - **Bottom-Right (Red Zone):** Low-value, high-risk projects. These are candidates for re-evaluation, de-scoping, or potential cancellation.
    - **Bubble Size:** Represents the project's total approved budget.
    - **Bubble Color:** Shows the current health status as reported by the Project Manager.
    """, icon="💡")

    fig = create_portfolio_bubble_chart(df)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- Project Summary Table ---
    st.subheader("Project Summary Table")
    
    # Define a function to color the health status for better visibility
    def color_status(status):
        color = 'gray'
        if status == 'On Track':
            color = 'green'
        elif status == 'Needs Monitoring':
            color = 'orange'
        elif status == 'At Risk':
            color = 'red'
        return f'background-color: {color}; color: white'

    st.dataframe(
        df[['name', 'project_type', 'phase', 'pm', 'health_status', 'regulatory_path']].style.applymap(color_status, subset=['health_status']),
        use_container_width=True,
        hide_index=True,
        column_config={
            "name": st.column_config.TextColumn("Project Name", width="large"),
            "project_type": st.column_config.TextColumn("Type", help="NPD = New Product Development, LCM = Lifecycle Management"),
            "phase": st.column_config.TextColumn("Current Phase"),
            "regulatory_path": st.column_config.TextColumn("Reg. Path"),
            "pm": st.column_config.TextColumn("Project Manager"),
            "health_status": st.column_config.TextColumn("Status"),
        }
    )
            "regulatory_path": st.column_config.TextColumn("Reg. Path"),
            "pm": st.column_config.TextColumn("Project Manager"),
        }
    )
