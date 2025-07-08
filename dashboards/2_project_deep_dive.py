# pmo_command_center/dashboards/2_project_deep_dive.py
"""
This module provides a detailed, single-project view, allowing the PMO Director
to "deep dive" into the specifics of any project in the portfolio.
"""
import streamlit as st
import pandas as pd
from utils.pmo_session_state_manager import SPMOSessionStateManager
from utils.plot_utils import create_financial_burn_chart

def render_project_deep_dive(ssm: SPMOSessionStateManager):
    """Renders an interactive dashboard for analyzing a single project."""
    st.header("🔎 Project Deep Dive")
    st.caption("Select a project to analyze its detailed status, including milestones, financials, risks, and change controls.")

    projects = ssm.get_data("projects")
    milestones = ssm.get_data("milestones")
    project_risks = ssm.get_data("project_risks")
    change_controls = ssm.get_data("change_controls")
    financials = ssm.get_data("financials")

    if not projects:
        st.warning("No project data available.")
        return

    proj_df = pd.DataFrame(projects)
    
    # --- Project Selector ---
    project_names = proj_df['name'].tolist()
    selected_project_name = st.selectbox("Select a Project to Analyze", options=project_names)
    
    if not selected_project_name:
        return

    selected_project = proj_df[proj_df['name'] == selected_project_name].iloc[0]
    project_id = selected_project['id']

    st.divider()
    st.subheader(f"Analysis for: {selected_project_name} ({project_id})")

    # --- High-Level Project KPIs ---
    kpi_cols = st.columns(4)
    kpi_cols[0].metric("Health Status", selected_project['health_status'])
    kpi_cols[1].metric("Current Phase", selected_project['phase'])
    kpi_cols[2].metric("Project Manager", selected_project['pm'])
    kpi_cols[3].metric("Completion", f"{selected_project['completion_pct']}%")

    # --- Tabbed View for Details ---
    detail_tabs = st.tabs(["**Financials & Budget**", "**Milestones**", "**Risks**", "**Change Control**"])

    # Financials Tab
    with detail_tabs[0]:
        st.subheader("Financial Performance")
        financial_df = pd.DataFrame(financials)
        project_financials = financial_df[financial_df['project_id'] == project_id]

        if not project_financials.empty:
            burn_chart_fig = create_financial_burn_chart(project_financials)
            st.plotly_chart(burn_chart_fig, use_container_width=True)

            variance = selected_project['actuals_usd'] - selected_project['budget_usd']
            fin_kpi_cols = st.columns(3)
            fin_kpi_cols[0].metric("Total Budget", f"${selected_project['budget_usd']:,.0f}")
            fin_kpi_cols[1].metric("Actuals to Date", f"${selected_p
