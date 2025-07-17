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

    # --- Data Loading (Sandbox-aware) ---
    projects = ssm.get_data("projects")
    dhf_items = ssm.get_data("dhf_documents")
    traceability_data = ssm.get_data("traceability_matrix")
    on_market_products = ssm.get_data("on_market_products")

    if not projects:
        st.warning("No project data available to render this dashboard.")
        return

    proj_df = pd.DataFrame(projects)
    active_proj_df = proj_df[proj_df['health_status'] != 'Completed'].copy()
    project_name_map = pd.Series(proj_df.name.values, index=proj_df.id).to_dict()

    # --- Main Tabbed Interface ---
    tab1, tab2, tab3 = st.tabs(["**R&D Phase-Gate Pipeline**", "**DHF & Traceability**", "**On-Market Product Health**"])

    # --- ENHANCEMENT: R&D Phase-Gate Pipeline View with Realistic Phases ---
    with tab1:
        st.subheader("R&D Pipeline Status (Phase-Gate View)")
        st.info(
            "This Kanban-style board shows the status of the autoimmune pipeline against our standardized "
            "Product Development Process (PDP), providing an at-a-glance view of portfolio flow.",
            icon="🚦"
        )

        # Define the complete, ordered list of phases for a realistic PDP
        pdp_phases = [
            'Concept', 'Feasibility', 'Development', 
            'Verification & Validation', 'Regulatory Approval', 
            'Launch', 'Remediation'
        ]
        
        # Filter to show only phases that currently have active projects
        present_phases = sorted(
            active_proj_df['phase'].unique(), 
            key=lambda x: pdp_phases.index(x) if x in pdp_phases else 99
        )
        
        if not present_phases:
            st.info("No active projects in the pipeline.")
        else:
            cols = st.columns(len(present_phases))
            for i, phase in enumerate(present_phases):
                with cols[i]:
                    st.markdown(f"<h5>{phase}</h5>", unsafe_allow_html=True)
                    st.markdown("---")
                    projects_in_phase = active_proj_df[active_proj_df['phase'] == phase]
                    for _, project in projects_in_phase.iterrows():
                        with st.container(border=True):
                            st.markdown(f"**{project['id']}**: {project['name']}")
                            st.caption(f"PM: {project['pm']}")

    # --- DHF & Traceability View (Unchanged) ---
    with tab2:
        st.subheader("Design History File (DHF) & Requirements Traceability")
        st.info("Monitor **21 CFR 820.30** compliance, track DHF completeness, and visualize requirements traceability.", icon="📑")
        
        if not dhf_items:
            st.warning("No DHF document data available.")
        else:
            dhf_df = pd.DataFrame(dhf_items)
            total_docs = dhf_df.groupby('project_id').size()
            approved_docs = dhf_df[dhf_df['status'] == 'Approved'].groupby('project_id').size()
            dhf_completeness = (approved_docs / total_docs * 100).fillna(0).round(1).reset_index(name='completeness_pct')
            dhf_completeness = pd.merge(dhf_completeness, proj_df[['id', 'name']], left_on='project_id', right_on='id')

            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown("##### DHF Completeness (%)")
                fig_dhf = create_dhf_completeness_chart(dhf_completeness)
                st.plotly_chart(fig_dhf, use_container_width=True)
            with col2:
                st.markdown("##### DHF Document Status")
                selected_project_id_dhf = st.selectbox("Select Project", options=active_proj_df['id'], format_func=lambda x: project_name_map.get(x, x), key="dhf_select")
                if selected_project_id_dhf:
                    project_docs = dhf_df[dhf_df['project_id'] == selected_project_id_dhf]
                    st.dataframe(project_docs[['doc_type', 'status', 'owner']], use_container_width=True, hide_index=True)

            st.divider()
            st.markdown("##### Requirements Traceability Matrix")
            if traceability_data:
                trace_df = pd.DataFrame(traceability_data)
                unique_trace_projects = trace_df['project_id'].unique()
                selected_project_id_trace = st.selectbox("Select Project", options=unique_trace_projects, format_func=lambda x: project_name_map.get(x, x), key="trace_select")
                if selected_project_id_trace:
                    fig_sankey = create_traceability_sankey(trace_df[trace_df['project_id'] == selected_project_id_trace])
                    st.plotly_chart(fig_sankey, use_container_width=True)
            else:
                st.warning("No traceability data available.")

    # --- On-Market Product Health View (Unchanged) ---
    with tab3:
        st.subheader("On-Market Product Health")
        st.info("Monitor post-market surveillance data from the QMS to proactively manage quality and plan sustaining activities.", icon="📈")
        
        if on_market_products:
            on_market_df = pd.DataFrame(on_market_products)
            st.dataframe(on_market_df, use_container_width=True, hide_index=True,
                column_config={
                    "product_name": st.column_config.TextColumn("Product Family", width="large"),
                    "open_capas": st.column_config.NumberColumn("Open CAPAs"),
                    "complaint_rate_ytd": st.column_config.ProgressColumn("Complaint Rate (YTD)", help="Target < 0.5", format="%.3f", min_value=0, max_value=1.0),
                }
            )
        else:
            st.warning("No on-market product data available.")
