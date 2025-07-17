"""
This module provides a detailed, single-project view. It now includes ML-powered
predictions and an interactive workflow for managing Design Change Controls,
transforming it into a proactive risk and performance management tool.
"""
import streamlit as st
import pandas as pd
from utils.pmo_session_state_manager import SPMOSessionStateManager
from utils.plot_utils import create_financial_burn_chart, create_risk_contribution_plot

def render_project_deep_dive(ssm: SPMOSessionStateManager):
    """Renders an interactive dashboard for analyzing a single project."""
    st.header("🔎 Project Deep Dive & Predictive Analysis")
    st.caption("Select a project to analyze its status, view ML-powered predictions, and manage its governance workflows.")

    # --- Data Loading (Sandbox-aware) ---
    projects = ssm.get_data("projects")
    milestones = ssm.get_data("milestones")
    raid_logs = ssm.get_data("raid_logs")
    change_controls = ssm.get_data("change_controls")
    financials = ssm.get_data("financials")

    if not projects:
        st.warning("No project data available.")
        return

    proj_df = pd.DataFrame(projects)
    active_proj_df = proj_df[proj_df['health_status'] != 'Completed'].copy()
    project_name_map = pd.Series(proj_df.name.values, index=proj_df.id).to_dict()

    if active_proj_df.empty:
        st.info("No active projects available for analysis.")
        return
        
    selected_project_id = st.selectbox(
        "Select an Active Project to Analyze",
        options=active_proj_df['id'],
        format_func=lambda x: f"{x} - {project_name_map.get(x, x)}"
    )
    if not selected_project_id:
        return

    selected_project = active_proj_df[active_proj_df['id'] == selected_project_id].iloc[0]
    project_name = selected_project['name']

    st.divider()
    st.subheader(f"Analysis for: {project_name} ({selected_project_id})")
    
    # --- Top-Level Analysis (Unchanged) ---
    col1, col2 = st.columns(2)
    with col1:
        st.info("#### 🧠 AI-Powered Predictions", icon="🤖")
        with st.container(border=True):
            risk_proba = selected_project.get('predicted_schedule_risk', 0.0)
            st.metric("Predicted Likelihood of Project Delay", f"{risk_proba:.1%}")
            if risk_proba > 0.7: st.error("High risk of delay detected.", icon="🚨")
            elif risk_proba > 0.4: st.warning("Moderate risk of delay.", icon="⚠️")
            else: st.success("Low risk of delay predicted.", icon="✅")
            st.divider()
            predicted_eac = selected_project.get('predicted_eac_usd', 0.0)
            st.metric("AI-Predicted EAC", f"${predicted_eac:,.0f}", delta=f"${(predicted_eac - selected_project.get('budget_usd', 0)):,.0f} vs Budget", delta_color="inverse")

    with col2:
        st.info("#### 📈 Earned Value Performance", icon="📊")
        with st.container(border=True):
            kpi_cols = st.columns(2)
            kpi_cols[0].metric("CPI", f"{selected_project.get('cpi', 0):.2f}", help="Cost Performance Index: >1.0 is Favorable")
            kpi_cols[1].metric("SPI", f"{selected_project.get('spi', 0):.2f}", help="Schedule Performance Index: >1.0 is Favorable")
            st.divider()
            st.markdown(f"**Project Manager:** {selected_project.get('pm')}<br>**Reported Health:** {selected_project.get('health_status')}<br>**Regulatory Path:** {selected_project.get('regulatory_path')}", unsafe_allow_html=True)
            
    # --- Detailed Tabs ---
    st.divider()
    tab_risk, tab_fin, tab_mile, tab_dcr = st.tabs(["**Risk & RAID**", "**Financials**", "**Milestones**", "**Change Control**"])

    with tab_risk:
        st.subheader("Key Drivers of Predicted Schedule Risk")
        risk_contributions = selected_project.get('risk_contributions')
        if isinstance(risk_contributions, pd.DataFrame) and not risk_contributions.empty:
            fig_contrib = create_risk_contribution_plot(risk_contributions, f"Risk Drivers for {project_name}")
            st.plotly_chart(fig_contrib, use_container_width=True)
        else:
            st.info("No predictive model data available to determine risk drivers for this project.")
        
        st.subheader(f"RAID Log for {project_name}")
        project_raid = pd.DataFrame(raid_logs)[pd.DataFrame(raid_logs)['project_id'] == selected_project_id]
        st.dataframe(project_raid[['log_id', 'type', 'description', 'owner', 'status', 'due_date']], use_container_width=True, hide_index=True)

    with tab_fin:
        st.subheader("Financial Performance")
        project_financials = pd.DataFrame(financials)[pd.DataFrame(financials)['project_id'] == selected_project_id]
        if not project_financials.empty:
            burn_chart_fig = create_financial_burn_chart(project_financials, f"Financial Burn for {project_name}")
            st.plotly_chart(burn_chart_fig, use_container_width=True)
        else:
            st.info("No specific financial transaction data available for this project yet.")

    with tab_mile:
        st.subheader("Key Milestones")
        project_milestones = pd.DataFrame(milestones)[pd.DataFrame(milestones)['project_id'] == selected_project_id]
        st.dataframe(project_milestones[['milestone', 'due_date', 'status']], use_container_width=True, hide_index=True)

    # --- ENHANCEMENT: Interactive Change Control Workflow ---
    with tab_dcr:
        st.subheader("Design Change Control Workflow")
        st.caption(f"Manage formal changes per **21 CFR 820.30(i)** for project {selected_project_id}.")
        
        is_sandboxed = st.session_state.get('sandbox_mode', False)
        if not is_sandboxed:
            st.info("Activate 'Sandbox Mode' on the Strategic Scenario Planning dashboard to enable workflow actions like approvals.", icon="🔬")

        change_df = pd.DataFrame(change_controls)
        project_changes = change_df[change_df['project_id'] == selected_project_id]

        if project_changes.empty:
            st.info("No change controls logged for this project.")
        else:
            pending_changes = project_changes[project_changes['status'] != 'Approved']
            approved_changes = project_changes[project_changes['status'] == 'Approved']

            st.markdown("##### Pending Review")
            if pending_changes.empty:
                st.success("No pending change controls for this project.", icon="✅")
            else:
                for _, change in pending_changes.iterrows():
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col1:
                        st.markdown(f"**{change['dcr_id']}**")
                    with col2:
                        st.markdown(change['description'])
                    with col3:
                        # The button is disabled if not in sandbox mode
                        if st.button("Approve", key=change['dcr_id'], use_container_width=True, disabled=not is_sandboxed):
                            # This is a "write" operation, ssm will handle the logic
                            ssm.approve_dcr(dcr_id=change['dcr_id'], project_id=selected_project_id, user="PMO Director")
                            st.rerun()
            
            st.divider()
            st.markdown("##### Approved / Closed")
            if not approved_changes.empty:
                st.dataframe(approved_changes[['dcr_id', 'description']], use_container_width=True, hide_index=True)
