# pmo_command_center/dashboards/governance_reporting.py
"""
This module renders the Governance & Reporting dashboard.

It provides centralized tools for project governance, including a portfolio-wide
RAID (Risks, Assumptions, Issues, Decisions) log and a facility for generating
standardized, one-click project status reports. This enforces a "One Werfen"
approach to project management, ensuring consistency and efficiency.
"""
import streamlit as st
import pandas as pd
from utils.pmo_session_state_manager import SPMOSessionStateManager
from utils.report_generator import generate_project_status_report

def render_governance_dashboard(ssm: SPMOSessionStateManager):
    """Renders the dashboard for project governance tools."""
    st.header("⚖️ Governance & Reporting")
    st.caption("Centralize RAID logs for consistent governance and generate standardized project status reports with a single click.")

    # --- Data Loading ---
    projects = ssm.get_data("projects")
    raid_logs = ssm.get_data("raid_logs")

    if not projects:
        st.warning("No project data available to render this dashboard.")
        return

    proj_df = pd.DataFrame(projects)
    active_proj_df = proj_df[proj_df['health_status'] != 'Completed'].copy()

    # --- Tabbed Interface ---
    tab1, tab2 = st.tabs(["**Portfolio RAID Log**", "**Standardized Reporting**"])

    # --- Portfolio RAID Log ---
    with tab1:
        st.subheader("Centralized RAID Log")
        st.info(
            "This log provides a single source of truth for all major Risks, Assumptions, Issues, and Decisions across the active portfolio. "
            "Use the filters to focus on specific projects or item types. This is crucial for cross-project awareness and knowledge management.",
            icon="📚"
        )

        if not raid_logs:
            st.warning("No RAID log data is available.")
            return

        raid_df = pd.DataFrame(raid_logs)
        raid_df = pd.merge(raid_df, proj_df[['id', 'name']], left_on='project_id', right_on='id', how='left')

        # --- Filtering Controls ---
        col1, col2 = st.columns(2)
        with col1:
            selected_projects_raid = st.multiselect(
                "Filter by Project(s)",
                options=active_proj_df['name'].unique(),
                default=active_proj_df['name'].unique()
            )
        with col2:
            selected_types_raid = st.multiselect(
                "Filter by Type(s)",
                options=raid_df['type'].unique(),
                default=raid_df['type'].unique()
            )

        # Apply filters
        filtered_raid_df = raid_df[
            (raid_df['name'].isin(selected_projects_raid)) &
            (raid_df['type'].isin(selected_types_raid))
        ]

        st.dataframe(
            filtered_raid_df[['log_id', 'name', 'type', 'description', 'owner', 'status', 'due_date']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "log_id": "Log ID",
                "name": "Project",
                "type": st.column_config.TextColumn("Type (RAID)"),
                "description": st.column_config.TextColumn("Description", width="large"),
                "owner": "Owner",
                "status": "Status",
                "due_date": st.column_config.DateColumn("Due Date", format="YYYY-MM-DD")
            }
        )
        st.caption("In a full application, this would be an editable table allowing for real-time updates.")

    # --- Standardized Reporting ---
    with tab2:
        st.subheader("Generate Standardized Project Status Report")
        st.info(
            "Select a project to generate a standardized, one-page status report in Microsoft PowerPoint format. "
            "This feature drastically reduces the administrative burden on Project Managers and ensures consistent communication to stakeholders.",
            icon="📄"
        )

        selected_project_id_report = st.selectbox(
            "Select a Project to Generate a Report",
            options=active_proj_df['id'],
            format_func=lambda x: f"{x} - {active_proj_df[active_proj_df['id'] == x]['name'].iloc[0]}"
        )

        if st.button("🚀 Generate Report", use_container_width=True, type="primary"):
            with st.spinner(f"Generating status report for {selected_project_id_report}..."):
                try:
                    # Gather all necessary data for the selected project
                    project_details = proj_df[proj_df['id'] == selected_project_id_report].to_dict('records')[0]
                    financial_data = pd.DataFrame(ssm.get_data("financials"))
                    project_financials = financial_data[financial_data['project_id'] == selected_project_id_report]
                    milestone_data = pd.DataFrame(ssm.get_data("milestones"))
                    project_milestones = milestone_data[milestone_data['project_id'] == selected_project_id_report]
                    raid_data = pd.DataFrame(raid_logs)
                    project_risks = raid_data[(raid_data['project_id'] == selected_project_id_report) & (raid_data['type'] == 'Risk')]

                    # Call the report generation utility
                    report_buffer = generate_project_status_report(
                        project_details=project_details,
                        financials_df=project_financials,
                        milestones_df=project_milestones,
                        risks_df=project_risks
                    )

                    st.download_button(
                        label="✅ Click to Download Report",
                        data=report_buffer,
                        file_name=f"Status_Report_{project_details['name'].replace(' ', '_')}.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Failed to generate report: {e}")
