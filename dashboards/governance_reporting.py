"""
This module renders the Governance & Reporting dashboard.

It provides centralized tools for project governance, including a portfolio-wide
RAID (Risks, Assumptions, Issues, Decisions) log and a facility for generating
standardized, one-click reports. This enforces a "One Werfen" approach to
project management, ensuring consistency and efficiency.
"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from utils.pmo_session_state_manager import SPMOSessionStateManager
from utils.report_generator import generate_project_status_report, generate_board_ready_deck
from utils import plot_utils # Pass plot utils to the report generator

def render_governance_dashboard(ssm: SPMOSessionStateManager):
    """Renders the dashboard for project governance tools and reporting."""
    st.header("⚖️ Governance & Reporting")
    st.caption("Centralize RAID logs for consistent governance and generate standardized project reports with a single click.")

    # --- Data Loading ---
    projects = ssm.get_data("projects")
    raid_logs = ssm.get_data("raid_logs")
    milestones = ssm.get_data("milestones")
    goals = ssm.get_data("strategic_goals")
    alerts = ssm.get_data("alerts")


    if not projects:
        st.warning("No project data available to render this dashboard.")
        return

    proj_df = pd.DataFrame(projects)
    active_proj_df = proj_df[proj_df['health_status'] != 'Completed'].copy()
    project_name_map = pd.Series(proj_df.name.values, index=proj_df.id).to_dict()

    # --- Tabbed Interface ---
    tab1, tab2, tab3 = st.tabs(["**Portfolio RAID Log**", "**Standardized Reporting**", "**Communication Log**"])

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
        raid_df['name'] = raid_df['project_id'].map(project_name_map)

        # --- Filtering Controls ---
        col1, col2 = st.columns(2)
        with col1:
            # Use the active project names for filtering
            active_project_names = [project_name_map.get(pid) for pid in active_proj_df['id'].unique()]
            selected_projects_raid = st.multiselect(
                "Filter by Project(s)",
                options=sorted(active_project_names),
                default=sorted(active_project_names)
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
        st.subheader("One-Click Standardized Reporting Toolkit")
        st.info(
            "Select a project to generate a standardized, one-page status report, or generate a comprehensive, board-ready "
            "summary of the entire portfolio. This feature drastically reduces administrative burden and ensures consistent communication.",
            icon="📄"
        )

        st.markdown("##### Single Project Status Report")
        selected_project_id_report = st.selectbox(
            "Select a Project",
            options=active_proj_df['id'],
            format_func=lambda x: project_name_map.get(x, x)
        )

        if st.button("🚀 Generate Project Status Report (PPTX)", use_container_width=True, type="primary"):
            with st.spinner(f"Generating status report for {project_name_map.get(selected_project_id_report)}..."):
                try:
                    project_details = proj_df[proj_df['id'] == selected_project_id_report].to_dict('records')[0]
                    milestone_data = pd.DataFrame(ssm.get_data("milestones"))
                    project_milestones = milestone_data[milestone_data['project_id'] == selected_project_id_report]
                    raid_data = pd.DataFrame(raid_logs)
                    project_risks = raid_data[(raid_data['project_id'] == selected_project_id_report) & (raid_data['type'] == 'Risk')]

                    report_buffer = generate_project_status_report(
                        project_details=project_details,
                        milestones_df=project_milestones,
                        risks_df=project_risks
                    )

                    st.download_button(
                        label="✅ Click to Download Project Report",
                        data=report_buffer,
                        file_name=f"Status_Report_{project_details['name'].replace(' ', '_')}.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Failed to generate report: {e}")
        
        st.divider()
        st.markdown("##### Full Portfolio Executive Deck")
        if st.button("🚀 Generate Board-Ready Portfolio Deck (PPTX)", use_container_width=True, type="primary"):
             with st.spinner("Generating executive portfolio summary..."):
                try:
                    deck_buffer = generate_board_ready_deck(
                        projects_df=proj_df,
                        goals_df=pd.DataFrame(goals),
                        alerts=alerts,
                        plot_utils=plot_utils
                    )
                    st.download_button(
                        label="✅ Click to Download Portfolio Deck",
                        data=deck_buffer,
                        file_name=f"sPMO_Portfolio_Review_{date.today()}.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Failed to generate deck: {e}", icon="🚨")


    # --- Communication Log ---
    with tab3:
        st.subheader("Communication & Audit Trail Log")
        st.info(
            "This log tracks key Q&A and responses related to process and methodology, for example, during audits or town halls. "
            "In a validated system, this would serve as part of the formal audit trail.",
            icon="🗣️"
        )
    
        # This is a placeholder for a more robust feature connected to a database.
        comm_log_data = {
            "Date": [(date.today() - timedelta(days=20)).strftime('%Y-%m-%d'), (date.today() - timedelta(days=45)).strftime('%Y-%m-%d')],
            "Topic/Question": ["Query from internal audit regarding RAID log update frequency.", "Question from R&D leadership on resource allocation priority."],
            "Response Summary": ["Confirmed that the sPMO dashboard now tracks timely updates, with a target of 85% weekly adherence.", "Referred to the Strategic Alignment dashboard to show how resources are tied to top corporate goals."],
            "Audience": ["Internal QMS Audit Team", "R&D Town Hall"]
        }
        st.dataframe(pd.DataFrame(comm_log_data), use_container_width=True, hide_index=True)
