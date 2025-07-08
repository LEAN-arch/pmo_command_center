# pmo_command_center/dashboards/financial_overview.py
"""
This module renders the Financial Overview dashboard. It provides a comprehensive
view of the portfolio's financial health, including budget vs. actuals,
variance analysis, and spend categorization.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.pmo_session_state_manager import SPMOSessionStateManager
from utils.plot_utils import create_financial_burn_chart

def render_financial_dashboard(ssm: SPMOSessionStateManager):
    """Renders the portfolio financial analysis dashboard."""
    st.header("💰 Financial Overview")
    st.caption("This is the **Budget, Actuals, and Variance Analysis** dashboard. Use it to monitor financial performance across the entire portfolio and for individual projects.")

    projects = ssm.get_data("projects")
    financials = ssm.get_data("financials")

    if not projects or not financials:
        st.warning("No project or financial data available.")
        return

    proj_df = pd.DataFrame(projects)
    fin_df = pd.DataFrame(financials)

    # --- Portfolio-Level Financial KPIs ---
    st.subheader("Portfolio Financial Health")
    total_budget = proj_df['budget_usd'].sum()
    total_actuals = proj_df['actuals_usd'].sum()
    portfolio_variance = total_actuals - total_budget
    
    # Calculate portfolio completion vs. budget burn
    proj_df['weighted_completion'] = proj_df['completion_pct'] * proj_df['budget_usd']
    portfolio_completion_pct = proj_df['weighted_completion'].sum() / total_budget
    portfolio_burn_pct = (total_actuals / total_budget) * 100

    kpi_cols = st.columns(3)
    kpi_cols[0].metric("Total Portfolio Budget", f"${total_budget:,.0f}")
    kpi_cols[1].metric("Total Actuals to Date", f"${total_actuals:,.0f}")
    kpi_cols[2].metric("Portfolio Variance", f"${portfolio_variance:,.0f}", delta_color="inverse", help="Negative value indicates portfolio is over budget.")
    
    st.progress(portfolio_burn_pct / 100, text=f"{portfolio_burn_pct:.1f}% Budget Burn vs. {portfolio_completion_pct:.1f}% Weighted Completion")

    st.divider()

    # --- Financial Burn Chart (Portfolio Level) ---
    st.subheader("Portfolio Financial Burn: Planned vs. Actual")
    fig_portfolio_burn = create_financial_burn_chart(fin_df, "Portfolio Financial Burn")
    st.plotly_chart(fig_portfolio_burn, use_container_width=True)

    st.divider()

    # --- Spend by Category and Project ---
    st.subheader("Project Spend Analysis")
    col1, col2 = st.columns(2)

    with col1:
        st.info("Analyze how the portfolio budget is distributed across different spending categories.", icon="📊")
        # Calculate spend by category
        actuals_by_cat = fin_df[fin_df['type'] == 'Actuals'].groupby('category')['amount'].sum().reset_index()
        fig_cat_spend = px.pie(
            actuals_by_cat,
            names='category',
            values='amount',
            title='Actual Spend by Category (Portfolio-wide)',
            hole=0.4
        )
        st.plotly_chart(fig_cat_spend, use_container_width=True)

    with col2:
        st.info("Compare the budget variance for each active project to identify top contributors to over/under spend.", icon="🎯")
        # Calculate variance by project
        active_proj_df = proj_df[proj_df['health_status'] != 'Completed'].copy()
        active_proj_df['variance'] = active_proj_df['actuals_usd'] - active_proj_df['budget_usd']
        
        fig_proj_var = px.bar(
            active_proj_df.sort_values('variance'),
            x='name',
            y='variance',
            title='Budget Variance by Active Project',
            labels={'name': 'Project', 'variance': 'Variance (USD)'},
            color='variance',
            color_continuous_scale='RdYlGn_r'
        )
        fig_proj_var.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_proj_var, use_container_width=True)
