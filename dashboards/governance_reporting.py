"""
This module renders the Governance & Reporting dashboard.

It provides centralized tools for project governance, including a portfolio-wide
RAID log, a compliance audit trail, and a facility for generating standardized,
one-click reports.
"""
import streamlit as st
import pandas as pd
from datetime import date
from utils.pmo_session_state_manager import SPMOSessionStateManager
from utils.report_generator import generate_project_status_report, generate_board_ready_deck
from utils import plot_utils

def render_governance_dashboard(ssm: SPMOSessionStateManager):
    """Renders the dashboard for project governance, reporting, and audit trails."""
    st.header("⚖️ Governance & Reporting")
    st.caption("Centralize RAID logs, generate standardized reports, and review the compliance audit trail.")

    # --- Data Loading ---
    projects = ssm.get_data("projects")
    raid_logs = ssm.get_data("raid_logs")
    milestones = ssm.get_data("milestones")
    goals = ssm.get_data("strategic_goals")
    alerts = ssm.get_data("alerts")
    # NEW: Load audit trail data
    audit_trail = st.session_state.get('audit_trail', [])

    if not projects:
        st.warning("No project data available to render this dashboard.")
        return

    proj_df = pd.DataFrame(projects)
    active_proj_df = proj_df[proj_df['health_status'] != 'Completed'].copy()
    project_name_map = pd.Series(proj_df.name.values, index=proj_df.id).to_dict()

    # --- Tabbed Interface ---
    tab_raid, tab_reports, tab_audit = st.tabs(["**Portfolio RAID Log**", "**Standardized Reporting**", "**Audit Trail**"])

    # --- Portfolio RAID Log Tab (Unchanged) ---
    with tab_raid:
        st.subheader("Centralized RAID Log")
        st.info("A single source of truth for all Risks, Assumptions, Issues, and Decisions across the active portfolio.", icon="📚")

        if not raid_logs:
            st.warning("No RAID log data is available.")
        else:
            raid_df = pd.DataFrame(raid_logs)
            raid_df['name'] = raid_df['project_id'].map(project_name_map)
            
            col1, col2 = st.columns(2)
            with col1:
                active_project_names = sorted([project_name_map.get(pid) for pid in active_proj_df['id'].unique() if project_name_map.get(pid)])
                selected_projects_raid = st.multiselect("Filter by Project(s)", options=active_project_names, default=active_project_names)
            with col2:
                selected_types_raid = st.multiselect("Filter by Type(s)", options=raid_df['type'].unique(), default=raid_df['type'].unique())
            
            filtered_raid_df = raid_df[(raid_df['name'].isin(selected_projects_raid)) & (raid_df['type'].isin(selected_types_raid))]
            st.dataframe(filtered_raid_df[['log_id', 'name', 'type', 'description', 'owner', 'status', 'due_date']], use_container_width=True, hide_index=True,
                column_config={"log_id": "ID", "name": "Project", "type": "Type", "description": st.column_config.TextColumn("Description", width="large"), "due_date": st.column_config.DateColumn("Due Date", format="YYYY-MM-DD")}
            )

    # --- Standardized Reporting Tab (Unchanged) ---
    with tab_reports:
        st.subheader("One-Click Standardized Reporting Toolkit")
        st.info("Generate standardized reports to reduce administrative burden and ensure consistent communication.", icon="📄")

        st.markdown("##### Single Project Status Report")
        selected_project_id_report = st.selectbox("Select a Project", options=active_proj_df['id'], format_func=lambda x: project_name_map.get(x, x))

        if st.button("🚀 Generate Project Status Report (PPTX)", use_container_width=True):
            with st.spinner(f"Generating status report for {project_name_map.get(selected_project_id_report)}..."):
                project_details = proj_df[proj_df['id'] == selected_project_id_report].to_dict('records')[0]
                project_milestones = pd.DataFrame(milestones)[pd.DataFrame(milestones)['project_id'] == selected_project_id_report]
                project_risks = pd.DataFrame(raid_logs)[(pd.DataFrame(raid_logs)['project_id'] == selected_project_id_report) & (pd.DataFrame(raid_logs)['type'] == 'Risk')]
                report_buffer = generate_project_status_report(project_details=project_details, milestones_df=project_milestones, risks_df=project_risks)
                st.download_button(label="✅ Click to Download Project Report", data=report_buffer, file_name=f"Status_Report_{project_details['name'].replace(' ', '_')}.pptx", mime="application/vnd.openxmlformats-officedocument.presentationml.presentation", use_container_width=True)

        st.divider()
        st.markdown("##### Full Portfolio Executive Deck")
        if st.button("🚀 Generate Board-Ready Portfolio Deck (PPTX)", use_container_width=True, type="primary"):
             with st.spinner("Generating executive portfolio summary..."):
                deck_buffer = generate_board_ready_deck(projects_df=proj_df, goals_df=pd.DataFrame(goals), alerts=alerts, plot_utils=plot_utils)
                st.download_button(label="✅ Click to Download Portfolio Deck", data=deck_buffer, file_name=f"sPMO_Portfolio_Review_{date.today()}.pptx", mime="application/vnd.openxmlformats-officedocument.presentationml.presentation", use_container_width=True)

    # --- Audit Trail Tab (NEW) ---
    with tab_audit:
        st.subheader("Compliance Audit Trail")
        st.info("This log provides an immutable, chronological record of all significant actions taken within the application, essential for **21 CFR Part 11** compliance.", icon="🛡️")

        if not audit_trail:
            st.info("No audit events have been logged in this session.")
        else:
            audit_df = pd.DataFrame(audit_trail).sort_values('timestamp', ascending=False)
            
            st.dataframe(
                audit_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "timestamp": st.column_config.DatetimeColumn("Timestamp", format="YYYY-MM-DD HH:mm:ss"),
                    "user": "User",
                    "event_type": "Event Type",
                    "details": st.column_config.TextColumn("Details", width="large")
                }
            )

            # Add a download button for the audit trail
            csv_data = audit_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Audit Trail (CSV)",
                data=csv_data,
                file_name=f"sPMO_Audit_Trail_{date.today()}.csv",
                mime="text/csv",
                use_container_width=True
            )
