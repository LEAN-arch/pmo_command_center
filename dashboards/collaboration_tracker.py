"""
This module renders the Cross-Entity Collaboration dashboard. It helps the
PMO Director track inter-site projects and the exchange of best practices
with other Werfen corporate entities to leverage enterprise-wide knowledge.
"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from utils.pmo_session_state_manager import SPMOSessionStateManager

def render_collaboration_dashboard(ssm: SPMOSessionStateManager):
    """Renders the dashboard for tracking cross-entity collaborations."""
    st.header("🌐 Cross-Entity Collaboration Tracker")
    st.caption("Monitor inter-site projects, shared resources, and the exchange of best practices with other corporate entities, such as Barcelona and Germany.")

    # --- Data Loading ---
    collaborations = ssm.get_data("collaborations")
    projects = ssm.get_data("projects")

    if not collaborations or not projects:
        st.warning("No collaboration or project data available.")
        return

    collab_df = pd.DataFrame(collaborations)
    proj_df = pd.DataFrame(projects)

    # Merge project names into collaboration data for a richer view
    if not collab_df.empty:
        collab_df = pd.merge(collab_df, proj_df[['id', 'name', 'pm']], left_on='project_id', right_on='id', how='left')
    else:
        st.info("There are currently no active inter-site collaborations logged.")
        return

    st.subheader("Active Inter-Site Collaborations")
    st.dataframe(
        collab_df[['name', 'collaborating_entity', 'type', 'status', 'pm']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "name": st.column_config.TextColumn("Our Autoimmunity Project", width="large"),
            "collaborating_entity": st.column_config.TextColumn("Collaborating Werfen Entity", width="large"),
            "type": "Collaboration Type",
            "status": "Status",
            "pm": st.column_config.TextColumn("NA Project Manager Lead")
        }
    )

    st.divider()

    st.subheader("Best Practices Exchange & Knowledge Transfer")
    st.info(
        "This section serves as a repository for best practices shared across entities, fostering continuous improvement "
        "in project management methodology and technical execution. The goal is to leverage Werfen's global expertise.",
        icon="🤝"
    )

    # This would be powered by a more formal knowledge management system in a real application.
    st.markdown("""
    | Date       | Originating Entity        | Best Practice / Lesson Learned                                       | Applicable To                  |
    |------------|---------------------------|----------------------------------------------------------------------|--------------------------------|
    | 2024-04-10 | R&D Center - Barcelona    | Implemented a standardized 'Phase 0' checklist for new technology feasibility studies, reducing risk in NPD projects. | NPD Feasibility                |
    | 2024-03-22 | Regulatory - Germany      | Developed a streamlined template for IVDR Technical File submissions that passed Notified Body review with minimal questions. | All IVDR Projects (e.g., LCM-002) |
    | 2024-02-15 | Operations - San Diego    | Used value stream mapping to reduce reagent kitting time by 15%.     | LCM / COGS Reduction Projects  |
    """)

    st.divider()

    st.subheader("Coordination & Key Meetings")
    st.caption("Tracking key meetings and decisions related to cross-entity initiatives to ensure alignment and accountability.")
    
    meeting_data = {
        "Meeting": ["Quarterly PMO Sync w/ Barcelona", "IVDR Task Force Weekly", "Global Tech Council"],
        "Next Occurrence": [(date.today() + timedelta(days=45)).strftime('%Y-%m-%d'), (date.today() + timedelta(days=4)).strftime('%Y-%m-%d'), (date.today() + timedelta(days=60)).strftime('%Y-%m-%d')],
        "Key Contact (External)": ["Javier Garcia", "Klaus Müller", "Dr. Lena Vogel"],
        "NA Lead": ["David Lee", "Diana Evans", "Sofia Chen"]
    }
    st.dataframe(pd.DataFrame(meeting_data), hide_index=True, use_container_width=True)
