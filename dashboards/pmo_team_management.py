# pmo_command_center/dashboards/pmo_team_management.py
"""
This module renders the PMO Team Management dashboard.

It provides the Director, PMO with a centralized view of their team's structure,
performance, and development, supporting key leadership responsibilities.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.pmo_session_state_manager import SPMOSessionStateManager

def render_pmo_team_dashboard(ssm: SPMOSessionStateManager):
    """Renders the dashboard for managing the PMO team."""
    st.header("🤝 PMO Team Management")
    st.caption("Visualize roles, responsibilities, performance scores, certification statuses, and development paths for the PMO team.")

    # --- Data Loading ---
    pmo_team = ssm.get_data("pmo_team")
    projects = ssm.get_data("projects")

    if not pmo_team or not projects:
        st.warning("No PMO team or project data available.")
        return

    team_df = pd.DataFrame(pmo_team)
    proj_df = pd.DataFrame(projects)

    # --- High-Level KPIs ---
    st.subheader("PMO Team Overview")
    kpi_cols = st.columns(3)
    total_headcount = len(team_df)
    avg_perf_score = team_df['performance_score'].mean()
    pmp_certified_count = team_df['certification_status'].str.contains("PMP").sum()
    
    kpi_cols[0].metric("Total PMO Headcount", total_headcount)
    kpi_cols[1].metric("Average Performance Score", f"{avg_perf_score:.2f} / 5.0")
    kpi_cols[2].metric("PMP Certified Staff", f"{pmp_certified_count} ({pmp_certified_count/total_headcount:.0%})")
    
    st.divider()

    # --- Team Roster and Details ---
    st.subheader("PMO Team Roster & Assignments")

    # Create a summary of project assignments for each PM
    pm_assignments = proj_df.groupby('pm')['id'].apply(lambda x: ', '.join(x)).reset_index()
    pm_assignments.rename(columns={'id': 'assigned_projects', 'pm': 'name'}, inplace=True)

    # Merge this back into the team dataframe
    team_details_df = pd.merge(team_df, pm_assignments, on='name', how='left').fillna("None")

    st.dataframe(
        team_details_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "name": st.column_config.TextColumn("Team Member", width="medium"),
            "role": "Role",
            "performance_score": st.column_config.ProgressColumn("Performance Score", format="%.2f", min_value=0, max_value=5),
            "certification_status": st.column_config.TextColumn("Certifications", width="medium"),
            "development_path": st.column_config.TextColumn("Development Focus", width="large"),
            "assigned_projects": st.column_config.TextColumn("Current Projects", width="large")
        }
    )
    
    st.divider()

    # --- Visual Analysis ---
    st.subheader("Team Skill & Performance Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("Distribution of roles within the PMO.", icon="📊")
        role_counts = team_df['role'].value_counts().reset_index()
        fig_roles = px.pie(role_counts, names='role', values='count', title="PMO Role Distribution", hole=0.4)
        st.plotly_chart(fig_roles, use_container_width=True)
        
    with col2:
        st.info("Performance scores across the team.", icon="🎯")
        fig_perf = px.box(team_df, x='role', y='performance_score', points="all",
                          title="Performance Scores by Role",
                          labels={'role': 'Role', 'performance_score': 'Performance Score (1-5)'})
        fig_perf.update_yaxes(range=[0,5.5])
        st.plotly_chart(fig_perf, use_container_width=True)
