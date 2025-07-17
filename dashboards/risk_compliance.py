# pmo_command_center/dashboards/risk_compliance.py
"""
This module renders the Risk & QMS Compliance dashboard. It provides a
portfolio-level view of aggregated project risks and key indicators of
Quality Management System health, crucial for a regulated environment like Werfen.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import random
from utils.pmo_session_state_manager import SPMOSessionStateManager

def render_risk_dashboard(ssm: SPMOSessionStateManager):
    """Renders the portfolio risk and compliance dashboard."""
    st.header("🛡️ Risk & QMS Compliance")
    st.caption("Monitor aggregated project risks and key indicators of Quality System health to ensure regulatory compliance and audit readiness.")

    # --- Data Loading ---
    raid_logs = ssm.get_data("raid_logs")
    qms_kpis = ssm.get_data("qms_kpis")
    projects = ssm.get_data("projects")

    # --- QMS Health Indicators ---
    st.subheader("Quality Management System (QMS) Health Indicators")
    st.info(
        "These metrics provide a snapshot of the overall health of the Quality System, which directly impacts project execution, "
        "audit readiness, and our regulatory standing with bodies like the FDA.",
        icon="📋"
    )

    kpi_cols = st.columns(4)
    kpi_cols[0].metric("Open CAPAs", qms_kpis.get("open_capas", 0), help="Total open Corrective and Preventive Actions per **21 CFR 820.100**. High numbers may indicate systemic issues.")
    kpi_cols[1].metric("Overdue CAPAs", qms_kpis.get("overdue_capas", 0), delta=str(qms_kpis.get("overdue_capas", 0)), delta_color="inverse")
    kpi_cols[2].metric("Open Internal Audit Findings", qms_kpis.get("internal_audit_findings_open", 0), delta=str(qms_kpis.get("internal_audit_findings_open", 0)), delta_color="inverse", help="Open findings from internal QMS audits per **21 CFR 820.22**.")
    kpi_cols[3].metric("Overdue Training Records", qms_kpis.get("overdue_training_records", 0), delta=str(qms_kpis.get("overdue_training_records", 0)), delta_color="inverse", help="Ensures staff are qualified for their roles per QMS requirements.")

    st.divider()

    # --- Portfolio Risk Matrix ---
    st.subheader("Portfolio Risk Landscape")
    st.info(
        "This risk matrix plots the most significant risks from across the entire portfolio, consistent with **ISO 14971** (Application of risk management to medical devices). "
        "The **Top-Right Quadrant** contains high-probability, high-impact risks that require immediate executive attention.",
        icon="⚠️"
    )

    if not raid_logs or not projects:
        st.warning("No portfolio risk or project data available.")
        return

    # Filter for only 'Risk' items from the RAID log
    df_risks = pd.DataFrame(raid_logs)
    df_risks = df_risks[df_risks['type'] == 'Risk'].copy()
    
    if df_risks.empty:
        st.success("No open risks are currently logged in the portfolio RAID log.", icon="✅")
        return

    # Assume probability and impact are embedded in the description or a separate field if model was richer
    # For demo, we'll assign them randomly if not present.
    if 'probability' not in df_risks.columns:
        df_risks['probability'] = [random.randint(1, 5) for _ in range(len(df_risks))]
    if 'impact' not in df_risks.columns:
        df_risks['impact'] = [random.randint(1, 5) for _ in range(len(df_risks))]

    df_risks['rpn'] = df_risks['probability'] * df_risks['impact']
    proj_df = pd.DataFrame(projects)
    df_risks = pd.merge(df_risks, proj_df[['id', 'name']], left_on='project_id', right_on='id', how='left')

    fig = px.scatter(
        df_risks,
        x="impact",
        y="probability",
        size="rpn",
        color="name",
        hover_name="description",
        text="log_id",
        size_max=40,
        title="Portfolio-Level Risk Matrix"
    )
    fig.update_traces(textposition='top center')
    fig.update_layout(
        xaxis=dict(title="Impact (1-5)", range=[0.5, 5.5], dtick=1),
        yaxis=dict(title="Probability (1-5)", range=[0.5, 5.5], dtick=1),
        legend_title="Project"
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Detailed Risk Register View ---
    st.subheader("Active Risk Register")
    st.caption("This is a filtered view of all items logged as 'Risk' in the central RAID Log.")
    st.dataframe(
        df_risks[['log_id', 'name', 'description', 'status', 'probability', 'impact', 'owner', 'due_date']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "log_id": "Risk ID",
            "name": "Project",
            "description": st.column_config.TextColumn("Description", width="large"),
            "probability": st.column_config.NumberColumn("P", help="Probability (1-5)"),
            "impact": st.column_config.NumberColumn("I", help="Impact (1-5)")
        }
    )
