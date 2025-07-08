# pmo_command_center/dashboards/pmo_health_metrics.py
"""
This module renders the PMO Health & KPIs dashboard. It is focused on metrics
that measure the effectiveness and maturity of the project management office
and its deployed methodologies.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.pmo_session_state_manager import SPMOSessionStateManager
from utils.plot_utils import create_gate_variance_plot

def render_pmo_health_dashboard(ssm: SPMOSessionStateManager):
    """Renders the dashboard for analyzing PMO process maturity and effectiveness."""
    st.header("📈 PMO Health & KPIs")
    st.caption("This dashboard provides metrics on PMO process effectiveness, helping to measure and improve the maturity of the project management function.")

    gate_data = ssm.get_data("phase_gate_data")
    projects = ssm.get_data("projects")
    project_risks = ssm.get_data("project_risks")

    if not projects:
        st.warning("No project data available for analysis.")
        return

    gate_df = pd.DataFrame(gate_data) if gate_data else pd.DataFrame()
    proj_df = pd.DataFrame(projects)
    risk_df = pd.DataFrame(project_risks) if project_risks else pd.DataFrame()

    # --- PMO Process Control KPIs / CTQs ---
    st.subheader("PMO Process Control & Efficiency (CTQs)")
    st.info("These metrics are **Critical-to-Quality (CTQs)** for a high-performing PMO. They measure the predictability and efficiency of the project management methodology, providing a basis for continuous improvement.", icon="🎯")

    # Gate Adherence
    on_time_gates_pct = 0
    if not gate_df.empty:
        completed_gates = gate_df.dropna(subset=['actual_date'])
        if not completed_gates.empty:
            on_time_gates = completed_gates[pd.to_datetime(completed_gates['actual_date']) <= pd.to_datetime(completed_gates['planned_date'])]
            on_time_gates_pct = (len(on_time_gates) / len(completed_gates)) * 100

    # Risk Closure Rate
    risk_closure_rate = 0
    if not risk_df.empty:
        active_risk_statuses = ["Mitigating", "Monitoring", "Action Plan Dev"]
        closed_risks = risk_df[~risk_df['status'].isin(active_risk_statuses)]
        risk_closure_rate = (len(closed_risks) / len(risk_df)) * 100 if not risk_df.empty else 0

    # Budget Variance
    active_projects = proj_df[proj_df['health_status'] != 'Completed']
    active_projects['budget_variance_pct'] = ((active_projects['actuals_usd'] - active_projects['budget_usd']) / active_projects['budget_usd']) * 100
    avg_budget_variance = active_projects['budget_variance_pct'].mean() if not active_projects.empty else 0


    kpi_cols = st.columns(3)
    kpi_cols[0].metric("Gate Schedule Adherence", f"{on_time_gates_pct:.1f}%", help="CTQ for Predictability. The percentage of completed phase-gates met on or before the planned date.")
    kpi_cols[1].metric("Avg. Project Budget Variance", f"{avg_budget_variance:.1f}%", help="CTQ for Financial Control. The average budget variance across all active projects. Negative is over budget.", delta_color="inverse")
    kpi_cols[2].metric("Risk Closure Rate", f"{risk_closure_rate:.1f}%", help="CTQ for Proactiveness. The percentage of identified risks that have been successfully closed/mitigated.")

    st.divider()

    # --- Trend Analysis Section ---
    st.subheader("Trend Analysis for Continuous Improvement")
    
    tab1, tab2 = st.tabs(["**Gate Performance Analysis**", "**Project Cycle Time Analysis**"])

    with tab1:
        st.info("Tracking gate performance helps identify systemic issues in planning, resource allocation, or risk management that need to be addressed to increase PMO maturity.", icon="📈")
        fig_variance = create_gate_variance_plot(gate_df)
        st.plotly_chart(fig_variance, use_container_width=True)

    with tab2:
        completed_projects = proj_df[proj_df['health_status'] == "Completed"]
        if not completed_projects.empty:
            completed_projects['duration_days'] = (pd.to_datetime(completed_projects['end_date']) - pd.to_datetime(completed_projects['start_date'])).dt.days
            
            fig_cycle_time = px.box(
                completed_projects,
                x='project_type',
                y='duration_days',
                points="all",
                title="Project Cycle Time by Type (Concept to Completion)",
                labels={'project_type': 'Project Type', 'duration_days': 'Total Duration (Days)'}
            )
            st.plotly_chart(fig_cycle_time, use_container_width=True)
            st.info("Cycle time is a key indicator of PMO efficiency. Establishing a baseline and tracking this metric over time allows the Director to measure the impact of process improvements.", icon="⏱️")
        else:
            st.info("No completed projects are available yet to calculate historical cycle times.")
