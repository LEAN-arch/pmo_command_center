"""
This module provides a detailed, single-project view. It now includes
machine learning models to predict schedule risk and Estimate at Completion (EAC),
transforming it into a proactive risk and performance management tool.
"""
import streamlit as st
import pandas as pd
from utils.pmo_session_state_manager import SPMOSessionStateManager
from utils.plot_utils import create_financial_burn_chart, create_risk_contribution_plot

def render_project_deep_dive(ssm: SPMOSessionStateManager):
    """Renders an interactive dashboard for analyzing a single project."""
    st.header("🔎 Project Deep Dive & Predictive Analysis")
    st.caption("Select a project to analyze its status, view ML-powered predictions, and access its full RAID log.")

    # --- Data Loading ---
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
    
    # Create a mapping for project names for efficient lookups
    project_name_map = pd.Series(proj_df.name.values, index=proj_df.id).to_dict()

    # --- Project Selection ---
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
    st.markdown(f"**Description:** *{selected_project.get('description', 'N/A')}*")

    # --- Top-Level Analysis: Predictions & Performance ---
    col1, col2 = st.columns(2)

    with col1:
        st.info("#### 🧠 AI-Powered Predictions", icon="🤖")
        with st.container(border=True):
            risk_proba = selected_project.get('predicted_schedule_risk', 0.0)
            st.metric("Predicted Likelihood of Project Delay", f"{risk_proba:.1%}")
            if risk_proba > 0.7:
                st.error("High risk of delay detected.", icon="🚨")
            elif risk_proba > 0.4:
                st.warning("Moderate risk of delay.", icon="⚠️")
            else:
                st.success("Low risk of delay predicted.", icon="✅")
            st.caption("Predicts the chance of finishing late based on historical data.")
            
            st.divider()
            
            predicted_eac = selected_project.get('predicted_eac_usd', 0.0)
            st.metric(
                "AI-Predicted Estimate at Completion (EAC)",
                f"${predicted_eac:,.0f}",
                delta=f"${(predicted_eac - selected_project.get('budget_usd', 0)):,.0f} vs Budget",
                delta_color="inverse",
                help="Forecasts the project's final cost based on its current performance and characteristics."
            )

    with col2:
        st.info("#### 📈 Earned Value Performance", icon="📊")
        with st.container(border=True):
            kpi_cols = st.columns(2)
            kpi_cols[0].metric("Cost Performance Index (CPI)", f"{selected_project.get('cpi', 0):.2f}", help=">1.0 is Favorable (Under Budget)")
            kpi_cols[1].metric("Schedule Perf. Index (SPI)", f"{selected_project.get('spi', 0):.2f}", help=">1.0 is Favorable (Ahead of Schedule)")
            st.caption("Objective metrics for cost and schedule efficiency.")
            
            st.divider()
            
            # Additional contextual info
            st.markdown(f"**Project Manager:** {selected_project.get('pm')}")
            st.markdown(f"**Reported Health:** {selected_project.get('health_status')}")
            st.markdown(f"**Regulatory Path:** {selected_project.get('regulatory_path')}")


    # --- Detailed Tabs ---
    st.divider()
    detail_tabs = st.tabs(["**Risk Drivers & RAID Log**", "**Financials**", "**Milestones**", "**Change Control**"])

    with detail_tabs[0]:
        st.subheader("Key Drivers of Predicted Schedule Risk")
        st.caption("This chart explains which project factors are contributing most to the AI's schedule risk prediction.")
        risk_contributions = selected_project.get('risk_contributions')
        if risk_contributions is not None and not risk_contributions.empty:
            fig_contrib = create_risk_contribution_plot(risk_contributions, f"Risk Drivers for {project_name}")
            st.plotly_chart(fig_contrib, use_container_width=True)
        else:
            st.info("No predictive model available to determine risk drivers for this project.")
        
        st.subheader(f"RAID Log for {project_name}")
        raid_df = pd.DataFrame(raid_logs)
        if not raid_df.empty:
            project_raid = raid_df[raid_df['project_id'] == selected_project_id]
            st.dataframe(project_raid[['log_id', 'type', 'description', 'owner', 'status', 'due_date']], use_container_width=True, hide_index=True)

    with detail_tabs[1]:
        st.subheader("Financial Performance")
        financial_df = pd.DataFrame(financials)
        if not financial_df.empty:
            project_financials = financial_df[financial_df['project_id'] == selected_project_id]
            if not project_financials.empty:
                burn_chart_fig = create_financial_burn_chart(project_financials, f"Financial Burn for {project_name}")
                st.plotly_chart(burn_chart_fig, use_container_width=True)
            else:
                st.info("No specific financial transaction data available for this project yet.")

    with detail_tabs[2]:
        st.subheader("Key Milestones")
        milestone_df = pd.DataFrame(milestones)
        if not milestone_df.empty:
            project_milestones = milestone_df[milestone_df['project_id'] == selected_project_id]
            st.dataframe(project_milestones[['milestone', 'due_date', 'status']], use_container_width=True, hide_index=True)

    with detail_tabs[3]:
        st.subheader("Design Change Controls")
        st.caption(f"Tracking formal changes per **21 CFR 820.30(i)** for project {selected_project_id}.")
        change_df = pd.DataFrame(change_controls)
        if not change_df.empty:
            project_changes = change_df[change_df['project_id'] == selected_project_id]
            st.dataframe(project_changes[['dcr_id', 'description', 'status']], use_container_width=True, hide_index=True)
        else:
            st.info("No change controls logged for this project.")
