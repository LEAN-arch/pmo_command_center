# pmo_command_center/dashboards/risk_and_compliance.py
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.pmo_session_state_manager import PMOSessionStateManager

def render_risk_dashboard(ssm: PMOSessionStateManager):
    st.header("Portfolio Risk & QMS Compliance Dashboard")
    st.caption("This dashboard aggregates project-level risks into a portfolio view and monitors key QMS health indicators to ensure regulatory compliance.")

    projects = ssm.get_data("projects")
    qms_kpis = ssm.get_data("qms_kpis")

    st.subheader("Quality Management System (QMS) Health Indicators")
    st.info("These metrics provide a snapshot of the overall health of the Quality System, which directly impacts project execution and audit readiness.", icon="📋")
    
    kpi_cols = st.columns(4)
    kpi_cols[0].metric("Open CAPAs", qms_kpis.get("open_capas", 0), help="Corrective and Preventive Actions. High numbers may indicate systemic issues.")
    kpi_cols[1].metric("Overdue CAPAs", qms_kpis.get("overdue_capas", 0), delta=qms_kpis.get("overdue_capas", 0), delta_color="inverse")
    kpi_cols[2].metric("Open Internal Audit Findings", qms_kpis.get("internal_audit_findings_open", 0), delta=qms_kpis.get("internal_audit_findings_open", 0), delta_color="inverse")
    kpi_cols[3].metric("Overdue Training Records", qms_kpis.get("overdue_training_records", 0), delta=qms_kpis.get("overdue_training_records", 0), delta_color="inverse", help="Ensures staff are qualified for their roles.")

    st.divider()
    st.subheader("Portfolio Risk Landscape")
    st.info("""
    This risk matrix plots the most significant risks from across the entire portfolio. This allows the PMO Director to identify risk concentrations and trends.
    - **Top-Right Quadrant:** High-probability, high-impact risks that require immediate executive attention and mitigation strategies.
    - **Bubble Size:** A proxy for the Risk Priority Number (RPN = Probability x Impact).
    """, icon="⚠️")
    
    # Simulate some project-level risks for demonstration if not in the main model
    # In a real system, this would come from a database.
    risks = [
        {"risk_id": "R-NPD001-01", "project_id": "NPD-001", "description": "Key sensor supplier fails to meet quality specs.", "probability": 4, "impact": 5, "status": "Mitigating"},
        {"risk_id": "R-LCM002-01", "project_id": "LCM-002", "description": "IVDR Notified Body requests additional clinical data.", "probability": 3, "impact": 5, "status": "Monitoring"},
        {"risk_id": "R-NPD003-01", "project_id": "NPD-003", "description": "Novel biomarker shows instability in feasibility studies.", "probability": 5, "impact": 4, "status": "Action Plan Dev"},
        {"risk_id": "R-NPD002-01", "project_id": "NPD-002", "description": "Firmware integration with LIS is more complex than anticipated.", "probability": 2, "impact": 3, "status": "Mitigating"},
    ]

    if not risks:
        st.warning("No portfolio risk data available.")
        return

    df_risks = pd.DataFrame(risks)
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

    st.subheader("Detailed Risk Register")
    st.dataframe(df_risks[['risk_id', 'name', 'description', 'status']], use_container_width=True, hide_index=True)
