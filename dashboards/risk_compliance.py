# pmo_command_center/dashboards/risk_compliance.py
"""
This module renders the Risk & QMS Compliance dashboard. It provides a
portfolio-level view of aggregated project risks and key indicators of
Quality Management System health, crucial for a regulated environment.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.pmo_session_state_manager import SPMOSessionStateManager

def render_risk_dashboard(ssm: SPMOSessionStateManager):
    """Renders the portfolio risk and compliance dashboard."""
    st.header("🛡️ Risk & QMS Compliance")
    st.caption("This is the **Portfolio Risks and QMS Health Metrics** dashboard. Monitor aggregated project risks and key indicators of Quality System health to ensure regulatory compliance.")

    project_risks = ssm.get_data("project_risks")
    qms_kpis = ssm.get_data("qms_kpis")
    projects = ssm.get_data("projects")

    # --- QMS Health Indicators ---
    st.subheader("Quality Management System (QMS) Health Indicators")
    st.info("These metrics provide a snapshot of the overall health of the Quality System, which directly impacts project execution, audit readiness, and regulatory standing.", icon="📋")
    
    kpi_cols = st.columns(4)
    kpi_cols[0].metric("Open CAPAs", qms_kpis.get("open_capas", 0), help="Corrective and Preventive Actions per **21 CFR 820.100**. High numbers may indicate systemic issues.")
    kpi_cols[1].metric("Overdue CAPAs", qms_kpis.get("overdue_capas", 0), delta=qms_kpis.get("overdue_capas", 0), delta_color="inverse")
    kpi_cols[2].metric("Open Internal Audit Findings", qms_kpis.get("internal_audit_findings_open", 0), delta=qms_kpis.get("internal_audit_findings_open", 0), delta_color="inverse", help="Open findings from internal QMS audits per **21 CFR 820.22**.")
    kpi_cols[3].metric("Overdue Training Records", qms_kpis.get("overdue_training_records", 0), delta=qms_kpis.get("overdue_training_records", 0), delta_color="inverse", help="Ensures staff are qualified for their roles per QMS requirements.")

    st.divider()

    # --- Portfolio Risk Matrix ---
    st.subheader("Portfolio Risk Landscape")
    st.info("""
    **Definition:** This risk matrix plots the most significant risks from across the entire portfolio, consistent with **ISO 14971** (Application of risk management to medical devices).
    
    **Interpretation:**
    - **Top-Right Quadrant:** High-probability, high-impact risks that require immediate executive attention and mitigation strategies.
    - **Bubble Size:** A proxy for the Risk Priority Number (RPN = Probability x Impact).
    """, icon="⚠️")
    
    if not project_risks:
        st.warning("No portfolio risk data available.")
        return

    df_risks = pd.DataFrame(project_risks)
    df_risks['rpn'] = df_risks['probability'] * df_risks['impact']

    # Link project names for better labeling
    proj_df = pd.DataFrame(projects)
    df_risks = pd.merge(df_risks, proj_df[['id', 'name']], left_on='project_id', right_on='id', how='left')

    fig = px.scatter(
        df_risks,
        x="impact",
        y="probability",
        size="rpn",
        color="name",
        hover_name="description",
        text="risk_id",
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

    # --- Detailed Risk Register ---
    st.subheader("Detailed Risk Register")
    st.dataframe(
        df_risks[['risk_id', 'name', 'description', 'status', 'probability', 'impact']],
        use_container_width=True,
        hide_index=True,
        column_config={"name": "Project"}
    )
