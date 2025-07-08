# pmo_command_center/dashboards/design_control_interface.py
"""
This module renders the Design Control & QMS Interface dashboard. It provides
a compliance-focused view of the portfolio, tracking phase-gate status and
the completeness of key DHF documents.
"""
import streamlit as st
import pandas as pd
from utils.pmo_session_state_manager import SPMOSessionStateManager

def render_design_control_dashboard(ssm: SPMOSessionStateManager):
    """Renders the dashboard for monitoring Design Control and QMS compliance."""
    st.header("📂 Design Control Interface")
    st.caption("Monitor portfolio-wide adherence to Design Control procedures (per **21 CFR 820.30**) and the status of key QMS documents.")

    projects = ssm.get_data("projects")
    # In a real app, this would query a document management system (e.g., Veeva, MasterControl)
    # For this demo, we'll simulate some key documents.
    dhf_docs = [
        {"project_id": "NPD-001", "doc_type": "Design & Development Plan", "status": "Approved"},
        {"project_id": "NPD-001", "doc_type": "Risk Management File", "status": "In Review"},
        {"project_id": "NPD-001", "doc_type": "V&V Master Plan", "status": "Draft"},
        {"project_id": "NPD-002", "doc_type": "Design & Development Plan", "status": "Approved"},
        {"project_id": "NPD-002", "doc_type": "Risk Management File", "status": "Approved"},
        {"project_id": "NPD-002", "doc_type": "Software Development Plan", "status": "Approved"},
        {"project_id": "LCM-002", "doc_type": "IVDR Gap Analysis Report", "status": "Approved"},
        {"project_id": "LCM-002", "doc_type": "Technical File Remediation Plan", "status": "Approved"},
    ]

    if not projects:
        st.warning("No project data available.")
        return

    proj_df = pd.DataFrame(projects)
    docs_df = pd.DataFrame(dhf_docs)

    # --- Phase-Gate Status Board ---
    st.subheader("Portfolio Phase-Gate Status")
    st.info("This view tracks the current Design Control phase of each active project, providing a clear picture of the portfolio's maturity and progress through the development lifecycle.", icon="🚦")

    # Kanban-style board
    phases = ['Feasibility', 'Development', 'V&V', 'Remediation'] # Define a logical order for the columns
    cols = st.columns(len(phases))

    for i, phase in enumerate(phases):
        with cols[i]:
            st.markdown(f"<h5>{phase}</h5>", unsafe_allow_html=True)
            st.markdown("---")
            projects_in_phase = proj_df[proj_df['phase'] == phase]
            if not projects_in_phase.empty:
                for _, project in projects_in_phase.iterrows():
                    st.success(f"**{project['id']}**: {project['name']}")
            else:
                st.caption("No projects in this phase.")

    st.divider()

    # --- DHF Document Status per Project ---
    st.subheader("Key DHF Document Status")
    st.info("This table provides a high-level check on the completeness of critical Design History File (DHF) documentation for each project. Missing or non-approved documents in late-stage projects represent a significant compliance risk.", icon="📑")
    
    # Create a pivot table for a clean matrix view
    doc_status_pivot = docs_df.pivot(index='project_id', columns='doc_type', values='status').fillna("N/A")
    
    # Add project name for readability
    doc_status_pivot = pd.merge(proj_df[['id', 'name']], doc_status_pivot, left_on='id', right_index=True).set_index('name')

    # Color-coding for status
    def color_doc_status(val):
        color = 'grey'
        if val == 'Approved': color = '#2ca02c' # green
        elif val == 'In Review': color = '#ff7f0e' # orange
        elif val == 'Draft': color = '#1f77b4' # blue
        return f'background-color: {color}; color: white;' if val != "N/A" else ''

    st.dataframe(
        doc_status_pivot.style.map(color_doc_status),
        use_container_width=True
    )

    st.divider()

    # --- Design Review Action Items (Placeholder) ---
    st.subheader("Open Design Review Actions")
    st.warning("Feature under construction: This section would aggregate all open action items from formal Design Reviews across the portfolio to identify bottlenecks in decision-making or execution. This is critical for ensuring that gate transitions are truly complete.", icon="🚧")
