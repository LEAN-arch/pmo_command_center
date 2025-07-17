# pmo_command_center/dashboards/portfolio_dashboard.py
"""
This module renders the main Executive Portfolio Dashboard. It provides at-a-glance
KPIs, a strategic view of projects, and a summary table featuring an automated,
objective portfolio health scorecard.
"""
import streamlit as st
import pandas as pd
import numpy as np
from utils.pmo_session_state_manager import SPMOSessionStateManager
from utils.plot_utils import create_portfolio_bubble_chart

def calculate_health_score(project_row: pd.Series) -> float:
    """Calculates a weighted health score for a project."""
    weights = {'spi': 0.4, 'cpi': 0.4, 'risk': 0.2}
    spi_score = np.clip(project_row.get('spi', 0) * 100, 0, 100)
    cpi_score = np.clip(project_row.get('cpi', 0) * 100, 0, 100)
    risk_score_val = project_row.get('risk_score', 5)
    risk_score = (10 - risk_score_val) / 9 * 100
    weighted_score = (
        spi_score * weights['spi'] +
        cpi_score * weights['cpi'] +
        risk_score * weights['risk']
    )
    return weighted_score

def render_portfolio_dashboard(ssm: SPMOSessionStateManager):
    """Renders the main executive-level portfolio health dashboard."""
    st.header("📊 Executive Portfolio Dashboard")
    st.caption("This is the **Executive KPIs & Project Landscape** dashboard. It provides a high-level summary of portfolio health, integrating project status with key QMS compliance indicators.")

    projects = ssm.get_data("projects")
    qms_kpis = ssm.get_data("qms_kpis")
    if not projects:
        st.warning("No project data available.")
        return

    df = pd.DataFrame(projects)
    active_df = df[df['health_status'] != "Completed"].copy()

    if not active_df.empty:
        active_df['health_score'] = active_df.apply(calculate_health_score, axis=1)
        portfolio_health = np.average(active_df['health_score'], weights=active_df['budget_usd'])
    else:
        portfolio_health = 100

    st.subheader("Executive KPIs")
    total_budget = df['budget_usd'].sum()
    total_actuals = df['actuals_usd'].sum()
    open_capas = qms_kpis.get("open_capas", 0)

    kpi_cols = st.columns(4)
    kpi_cols[0].metric(
        "Portfolio Health Score",
        f"{portfolio_health:.1f}/100",
        help="An objective, budget-weighted health score derived from project CPI, SPI, and Risk scores. Target > 85."
    )
    kpi_cols[1].metric(
        "Active Projects",
        len(active_df),
        help="Total number of active New Product Development (NPD) and Lifecycle Management (LCM) projects."
    )
    kpi_cols[2].metric(
        "Portfolio Budget Burn",
        f"{(total_actuals / total_budget) * 100:.1f}%" if total_budget > 0 else "0%",
        f"${total_actuals:,.0f} / ${total_budget:,.0f}",
        help="Total actual spend versus total approved budget for all projects."
    )
    kpi_cols[3].metric(
        "Open CAPAs (QMS Health)",
        open_capas,
        delta=f"{qms_kpis.get('overdue_capas', 0)} Overdue",
        delta_color="inverse",
        help=f"A leading indicator of QMS health per 21 CFR 820.100."
    )

    st.divider()

    st.subheader("Portfolio Landscape: Strategy vs. Risk")
    st.info(
        "**How to read this chart:** This is a strategic view of the entire portfolio, balancing project risk against strategic value to the business. "
        "The **Top-Left (High Value, Low Risk)** is the ideal quadrant. **Bubble Size** represents budget.",
        icon="💡"
    )

    fig = create_portfolio_bubble_chart(df)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Project Health Scorecard")
    st.caption("Detailed, objective health scores for each active project.")

    def color_health_score(score):
        if score >= 85: color = '#2ca02c'
        elif score >= 65: color = '#ff7f0e'
        else: color = '#d62728'
        return f'background-color: {color}; color: white; font-weight: bold;'

    if not active_df.empty:
        display_df = active_df[[
            'name', 'project_type', 'phase', 'pm', 'health_score', 'cpi', 'spi', 'risk_score'
        ]].copy()

        styled_df = display_df.style.map(
            color_health_score, subset=['health_score']
        ).format({
            'health_score': '{:.1f}',
            'cpi': '{:.2f}',
            'spi': '{:.2f}'
        })

        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "name": st.column_config.TextColumn("Project Name", width="large"),
                "project_type": st.column_config.TextColumn("Type"),
                "phase": st.column_config.TextColumn("Current Phase"),
                "pm": st.column_config.TextColumn("Project Manager"),
                "health_score": st.column_config.TextColumn("Health Score"),
                "cpi": st.column_config.TextColumn("CPI"),
                "spi": st.column_config.TextColumn("SPI"),
                "risk_score": st.column_config.TextColumn("Risk"),
            }
        )
    else:
        st.info("No active projects to display.")
