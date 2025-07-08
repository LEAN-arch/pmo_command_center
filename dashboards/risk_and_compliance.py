# pmo_command_center/dashboards/risk_and_compliance.py
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.pmo_session_state_manager import PMOSessionStateManager

def render_risk_dashboard(ssm: PMOSessionStateManager):
    st.header("Portfolio Risk & QMS Compliance Dashboard")

    risks = ssm.get_data("portfolio_risks")
    qms_kpis = ssm.get_data("qms_kpis")

    st.subheader("QMS Health Indicators")
    kpi_cols = st.columns(4)
    kpi_cols[0].metric("Open CAPAs", qms_kpis.get("open_capas", 0))
    kpi_cols[1].metric("Overdue CAPAs", qms_kpis.get("overdue_capas", 0), delta=qms_kpis.get("overdue_capas", 0), delta_color="inverse")
    kpi_cols[2].metric("Post-Market Complaints (YTD)", qms_kpis.get("post_market_complaints_ytd", 0))
    kpi_cols[3].metric("Overdue Training Records", qms_kpis.get("overdue_training_records", 0), delta=qms_kpis.get("overdue_training_records", 0), delta_color="inverse")

    st.divider()
    st.subheader("Portfolio Risk Matrix")

    if not risks:
        st.warning("No portfolio risk data available.")
        return

    df_risks = pd.DataFrame(risks)
    df_risks['rpn'] = df_risks['probability'] * df_risks['impact']

    fig = px.scatter(
        df_risks,
        x="impact",
        y="probability",
        size="rpn",
        color="project_id",
        hover_name="description",
        text="risk_id",
        size_max=40,
        title="Portfolio-Level Risks"
    )
    fig.update_traces(textposition='top center')
    fig.update_layout(
        xaxis=dict(title="Impact (1-5)", range=[0.5, 5.5], dtick=1),
        yaxis=dict(title="Probability (1-5)", range=[0.5, 5.5], dtick=1),
        legend_title="Project"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Detailed Risk Register")
    st.dataframe(df_risks[['risk_id', 'project_id', 'description', 'status']], use_container_width=True, hide_index=True)
