# pmo_command_center/dashboards/collaboration_tracker.py
"""
This module renders the Cross-Entity Collaboration dashboard. It helps the
PMO Director track inter-site projects, shared resources, and the exchange
of best practices with other corporate entities.
"""
import streamlit as st
import pandas as pd
from utils.pmo_session_state_manager import SPMOSessionStateManager
from datetime import date, timedelta

def render_collaboration_dashboard(ssm: SPMOSessionStateManager):
    """Renders the dashboard for tracking cross-entity collaborations."""
    st.header("🌐 Cross-Entity Collaboration Tracker")
    st.caption("Monitor inter-site projects, shared resources, and the exchange of best practices with other corporate entities to leverage enterprise-wide knowledge.")

    collaborations = ssm.get_data("collaborations")
    projects = ssm.get_data("projects")

    if not collaborations or not projects:
        st.warning("No collaboration or project data available.")
        return

    collab_df = pd.DataFrame(collaborations)
    proj_df = pd.DataFrame(projects)

    # Merge project names into collaboration data for a richer view
    collab_df = pd.merge(collab_df, proj_df[['id', 'name', 'pm']], left_on='project_id', right_on='id', how='left')

    st.subheader("Active Inter-Site Collaborations")
    st.dataframe(
        collab_df[['name', 'collaborating_entity', 'type', 'status', 'pm']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "name": st.column_config.TextColumn("Autoimmunity Project", width="large"),
            "collaborating_entity": st.column_config.TextColumn("Collaborating Entity", width="large"),
            "type": "Collaboration Type",
            "status": "Status",
            "pm": st.column_config.TextColumn("NA Project Manager")
        }
    )

    st.divider()

    st.subheader("Best Practices Exchange")
    st.info("This section serves as a repository for best practices shared across entities, fostering continuous improvement in project management methodology and technical execution.", icon="🤝")

    # This would be powered by a more formal knowledge management system in a real application
    # For the demo, we use markdown to simulate entries.
    st.markdown("""
    | Date       | Originating Entity        | Best Practice / Lesson Learned                                       | Applicable To                  |
    |------------|---------------------------|----------------------------------------------------------------------|--------------------------------|
    | 2024-04-10 | R&D Center - Barcelona    | Implemented a standardized 'Phase 0' checklist for new technology feasibility studies, reducing risk in NPD projects. | NPD Feasibility                |
    | 2024-03-22 | Regulatory - Germany      | Developed a streamlined template for IVDR Technical File submissions that passed Notified Body review with minimal questions. | All IVDR Projects (e.g., LCM-002) |
    | 2024-02-15 | Operations - San Diego    | Used value stream mapping to reduce reagent kitting time by 15%.     | LCM / COGS Reduction Projects  |
    """)

    st.divider()

    st.subheader("Coordination & Meetings")
    st.info("Tracking key meetings and decisions related to cross-entity initiatives to ensure alignment and accountability.", icon="📅")
    
    # Placeholder for a calendar or meeting notes feature
    st.write({
        "Meeting": ["Quarterly PMO Sync w/ Barcelona", "IVDR Task Force Weekly"],
        "Next Occurrence": [date.today() + timedelta(days=45), date.today() + timedelta(days=4)],
        "Key Contact (External)": ["Javier Garcia", "Klaus Müller"],
        "NA Lead": ["David Lee", "Diana Evans"]
    })
