# pmo_command_center/dashboards/plm_cockpit.py
"""
This module renders the Product Lifecycle Management (PLM) & Design Control Cockpit.

This is a cornerstone dashboard for a regulated medical device environment. It
provides an integrated view of the entire product lifecycle, from the R&D pipeline
and Design Control compliance to the health of on-market products. This dashboard
directly addresses the requirements of 21 CFR 820.30 and the strategic need for
proactive compliance and lifecycle oversight.
"""
import streamlit as st
import pandas as pd
from utils.pmo_session_state_manager import SPMOSessionStateManager
from utils.plot_utils import create_traceability_sankey, create_dhf_completeness_chart

def render_plm_cockpit(ssm: SPMOSessionStateManager):
    """Renders the comprehensive PLM and Design Control dashboard."""
    st.header("🧬 PLM & Design Control Cockpit")
    st.caption("Integrated view of the R&D Pipeline, Design Control Health, and On-Market Product Status.")

    # --- Data Loading ---
    projects = ssm.get_data("projects")
    dhf_items = ssm.get_data("dhf_documents")
    traceability_data = ssm.get_data("traceability_matrix")
    on_market_products = ssm.get_data("on_market_products")

    if not projects:
        st.warning("No project data available to render this dashboard.")
        return

    proj_df = pd.DataFrame(projects)
    active_proj_df = proj_df[proj_df['health_status'] != 'Completed'].copy()

    # --- Tabbed Interface for Logical Separation ---
    tab1, tab2, tab3 = st.tabs(["**R&D Phase-Gate Pipeline**", "**DHF & Traceability**", "**On-Market Product Health**"])

    # --- R&D Phase-Gate Pipeline View ---
    with tab1:
        st.subheader("R&D Pipeline Status (Phase-Gate View)")
        st.info(
            "This Kanban-style board shows the exact status of our entire autoimmune pipeline against our standardized "
            "Product Development Process (PDP). It provides an at-a-glance view of portfolio flow and potential bottlenecks.",
            icon="🚦"
        )

        phases = sorted(active_proj_df['phase'].unique(), key=lambda x: ['Feasibility', 'Development', 'V&V', 'Remediation', 'Launch'].index(x) if x in ['Feasibility', 'Development', 'V&V', 'Remediation', 'Launch'] else 99)
        cols = st.columns(len(phases))

        for i, phase in enumerate(phases):
            with cols[i]:
                st.markdown(f"<h5>{phase}</h5>", unsafe_allow_html=True)
                st.markdown("---")
                projects_in_phase = active_proj_df[active_proj_df['phase'] == phase]
                if not projects_in_phase.empty:
                    for _, project in projects_in_phase.iterrows():
                        with st.container(border=True):
                            st.markdown(f"**{project['id']}**: {project['name']}")
                            st.caption(f"PM: {project['pm']}")
                else:
                    st.caption("No projects in this phase.")

    # --- DHF & Traceability View ---
    with tab2:
        st.subheader("Design History File (DHF) & Requirements Traceability")
        st.info(
            "This section provides critical insights for **21 CFR 820.30** compliance. Monitor DHF completeness to prevent "
            "late-stage documentation crises and visualize requirements traceability to defend designs during audits.",
            icon="📑"
        )
        dhf_df = pd.DataFrame(dhf_items)
        # Calculate DHF completeness per project
        dhf_completeness = dhf_df[dhf_df['status'] == 'Approved'].groupby('project_id').size() / dhf_df.groupby('project_id').size()
        dhf_completeness = (dhf_completeness * 100).round(1).reset_index(name='completeness_pct')

        # Add project name and other details
        dhf_completeness = pd.merge(dhf_completeness, active_proj_df[['id', 'name', 'phase']], left_on='project_id', right_on='id')

        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown("##### DHF Completeness (%)")
            fig_dhf = create_dhf_completeness_chart(dhf_completeness)
            st.plotly_chart(fig_dhf, use_container_width=True)

        with col2:
            st.markdown("##### DHF Document Status")
            selected_project_id_dhf = st.selectbox(
                "Select Project to View DHF Status",
                options=active_proj_df['id'],
                format_func=lambda x: f"{x} - {active_proj_df[active_proj_df['id'] == x]['name'].iloc[0]}"
            )
            if selected_project_id_dhf:
                project_docs = dhf_df[dhf_df['project_id'] == selected_project_id_dhf]
                st.dataframe(
                    project_docs[['doc_type', 'status', 'owner']],
                    use_container_width=True,
                    hide_index=True
                )

        st.divider()
        st.markdown("##### Requirements Traceability Matrix")
        st.caption("Visualize the flow from user needs to V&V for a selected project.")

        if traceability_data:
            trace_df = pd.DataFrame(traceability_data)
            selected_project_id_trace = st.selectbox(
                "Select Project to View Traceability",
                options=trace_df['project_id'].unique(),
                format_func=lambda x: f"{x} - {active_proj_df[active_proj_df['id'] == x]['name'].iloc[0]}"
            )
            if selected_project_id_trace:
                fig_sankey = create_traceability_sankey(trace_df[trace_df['project_id'] == selected_project_id_trace])
                st.plotly_chart(fig_sankey, use_container_width=True)
        else:
            st.warning("No traceability data available.")

    # --- On-Market Product Health View ---
    with tab3:
        st.subheader("On-Market Product Health")
        st.info(
            "This dashboard monitors the health of our established, revenue-generating products like **QUANTA Flash®** and **Aptiva®**. "
            "It tracks post-market surveillance data from our QMS to proactively manage quality and plan for sustaining activities.",
            icon="📈"
        )
        if on_market_products:
            on_market_df = pd.DataFrame(on_market_products)
            st.dataframe(
                on_market_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "product_name": st.column_config.TextColumn("Product Family", width="large"),
                    "open_capas": st.column_config.NumberColumn("Open CAPAs", help="Number of open Corrective/Preventive Actions against this product line."),
                    "complaint_rate_ytd": st.column_config.ProgressColumn("Complaint Rate (YTD)", help="Complaints per 1000 units shipped. Target < 0.5.", format="%.3f", min_value=0, max_value=1.0),
                    "sustaining_project_status": st.column_config.TextColumn("Key Sustaining Project Status")
                }
            )
        else:
            st.warning("No on-market product data available.")
