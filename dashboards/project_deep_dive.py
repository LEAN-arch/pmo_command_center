# pmo_command_center/dashboards/project_deep_dive.py
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
    st.markdown(f"**Description:** *{selected_project['description']}*")

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
            burn_chart_fig = create_financial_burn_chart(project_financials, "Project Financial Burn")
            st.plotly_chart(burn_chart_fig, use_container_width=True)

            variance = selected_project['actuals_usd'] - selected_project['budget_usd']
            fin_kpi_cols = st.columns(3)
            fin_kpi_cols[0].metric("Total Budget", f"${selected_project['budget_usd']:,.0f}")
            fin_kpi_cols[1].metric("Actuals to Date", f"${selected_project['actuals_usd']:,.0f}")
            fin_kpi_cols[2].metric("Variance", f"${variance:,.0f}", delta_color="inverse", help="Negative value indicates project is over budget.")
        else:
            st.info("No detailed financial data available for this project.")

    # Milestones Tab
    with detail_tabs[1]:
        st.subheader("Key Milestones")
        milestone_df = pd.DataFrame(milestones)
        project_milestones = milestone_df[milestone_df['project_id'] == project_id]
        if not project_milestones.empty:
            st.dataframe(
                project_milestones[['milestone', 'due_date', 'status']],
                use_container_width=True, hide_index=True
            )
        else:
            st.info("No milestones defined for this project.")

    # Risks Tab
    with detail_tabs[2]:
        st.subheader("Project-Specific Risks")
        risk_df = pd.DataFrame(project_risks)
        project_risk_data = risk_df[risk_df['project_id'] == project_id]
        if not project_risk_data.empty:
            st.dataframe(
                project_risk_data[['risk_id', 'description', 'probability', 'impact', 'status']],
                use_container_width=True, hide_index=True
            )
        else:
            st.info("No specific risks logged for this project.")

    # Change Control Tab
    with detail_tabs[3]:
        st.subheader("Design Change Controls")
        st.caption("Tracking changes per **21 CFR 820.30(i)**.")
        change_df = pd.DataFrame(change_controls)
        project_changes = change_df[change_df['project_id'] == project_id]
        if not project_changes.empty:
            st.dataframe(
                project_changes[['dcr_id', 'description', 'status']],
                use_container_width=True, hide_index=True
            )
        else:
            st.info("No change controls logged for this project.")
