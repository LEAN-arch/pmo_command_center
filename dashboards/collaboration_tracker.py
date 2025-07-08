# pmo_command_center/dashboards/collaboration_tracker.py
"""
This module renders the Cross-Entity Collaboration dashboard. It helps the
PMO Director track inter-site projects, shared resources, and the exchange
of best practices with other Werfen entities.
"""
import streamlit as st
import pandas as pd
from utils.pmo_session_state_manager import SPMOSessionStateManager

def render_collaboration_dashboard(ssm: SPMOSessionStateManager):
    """Renders the dashboard for tracking cross-entity collaborations."""
    st.header("🌐 Cross-Entity Collaboration Tracker")
    st.caption("Monitor inter-site projects, shared resources, and the exchange of best practices with other Werfen entities.")

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
            "name": "Autoimmunity Project",
            "collaborating_entity": "Collaborating Werfen Entity",
            "type": "Collaboration Type",
            "status": "Status",
            "pm": "NA Project Manager"
        }
    )

    st.divider()

    st.subheader("Best Practices Exchange")
    st.info("This section serves as a repository for best practices shared across Werfen entities, fostering continuous improvement in project management methodology.", icon="🤝")

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
    st.info("Tracking key meetings and decisions related to cross-entity initiatives.", icon="📅")
    
    # Placeholder for a calendar or meeting notes feature
    st.write({
        "Meeting": ["Quarterly PMO Sync w/ Barcelona", "IVDR Task Force Weekly"],
        "Next Occurrence": [date.today() + timedelta(days=45), date.today() + timedelta(days=4)],
        "Key Contact": ["Javier Garcia", "Klaus Müller"]
    })
