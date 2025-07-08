# pmo_command_center/dashboards/financial_overview.py
"""
This module renders the Financial Overview dashboard. It includes ML-powered
anomaly detection to proactively flag unusual spending patterns.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import IsolationForest
from utils.pmo_session_state_manager import SPMOSessionStateManager
from utils.plot_utils import create_financial_burn_chart

def find_spending_anomalies(fin_df: pd.DataFrame):
    """Uses Isolation Forest to detect anomalous monthly spending."""
    if fin_df.empty:
        return []

    # Aggregate total actual spend by month and project
    actuals_df = fin_df[fin_df['type'] == 'Actuals'].copy()
    monthly_spend = actuals_df.groupby([pd.to_datetime(actuals_df['date']).dt.to_period('M'), 'project_id'])['amount'].sum().reset_index()
    
    if len(monthly_spend) < 2:
        return []

    # Train model on the amount
    model = IsolationForest(contamination='auto', random_state=42)
    predictions = model.fit_predict(monthly_spend[['amount']])
    
    monthly_spend['anomaly'] = predictions
    anomalous_data = monthly_spend[monthly_spend['anomaly'] == -1]
    
    # Convert period back to datetime for plotting
    anomalous_data['date'] = anomalous_data['date'].dt.to_timestamp()
    return anomalous_data

def render_financial_dashboard(ssm: SPMOSessionStateManager):
    """Renders the portfolio financial analysis dashboard with anomaly detection."""
    st.header("💰 Financial Overview")
    st.caption("This is the **Budget, Actuals, and Variance Analysis** dashboard. Use it to monitor financial performance and detect unusual spending patterns with embedded AI.")

    projects = ssm.get_data("projects")
    financials = ssm.get_data("financials")

    if not projects or not financials:
        st.warning("No project or financial data available.")
        return

    proj_df = pd.DataFrame(projects)
    fin_df = pd.DataFrame(financials)

    # --- Portfolio-Level Financial KPIs (same as before) ---
    st.subheader("Portfolio Financial Health")
    total_budget = proj_df['budget_usd'].sum()
    total_actuals = proj_df['actuals_usd'].sum()
    portfolio_variance = total_actuals - total_budget
    kpi_cols = st.columns(3)
    kpi_cols[0].metric("Total Portfolio Budget", f"${total_budget:,.0f}")
    kpi_cols[1].metric("Total Actuals to Date", f"${total_actuals:,.0f}")
    kpi_cols[2].metric("Portfolio Variance", f"${portfolio_variance:,.0f}", delta_color="inverse")

    st.divider()

    # --- Anomaly Detection ---
    st.subheader("🧠 AI-Powered Anomaly Detection in Project Spend")
    anomalies = find_spending_anomalies(fin_df)

    if not anomalies.empty:
        st.error(f"**{len(anomalies)} unusual spending events detected.** These months show a spend pattern that significantly differs from the norm and may warrant investigation.", icon="🚨")
        # Link project names to the anomalies
        anomalies_with_names = pd.merge(anomalies, proj_df[['id', 'name']], left_on='project_id', right_on='id')
        st.dataframe(
            anomalies_with_names[['date', 'name', 'amount']],
            column_config={
                "date": "Month",
                "name": "Project",
                "amount": st.column_config.NumberColumn("Anomalous Spend", format="$%d")
            },
            hide_index=True, use_container_width=True
        )
    else:
        st.success("No significant spending anomalies detected in the historical data.", icon="✅")

    st.divider()
    
    # --- Financial Burn Chart with Anomalies ---
    st.subheader("Portfolio Financial Burn: Planned vs. Actual")
    anomaly_dates = anomalies['date'].tolist() if not anomalies.empty else None
    fig_portfolio_burn = create_financial_burn_chart(fin_df, "Portfolio Financial Burn", anomaly_dates)
    st.plotly_chart(fig_portfolio_burn, use_container_width=True)

    st.divider()

    # --- Spend by Category and Project (same as before) ---
    st.subheader("Project Spend Analysis")
    col1, col2 = st.columns(2)
    with col1:
        actuals_by_cat = fin_df[fin_df['type'] == 'Actuals'].groupby('category')['amount'].sum().reset_index()
        fig_cat_spend = px.pie(actuals_by_cat, names='category', values='amount', title='Actual Spend by Category (Portfolio-wide)', hole=0.4)
        st.plotly_chart(fig_cat_spend, use_container_width=True)

    with col2:
        active_proj_df = proj_df[proj_df['health_status'] != 'Completed'].copy()
        active_proj_df['variance'] = active_proj_df['actuals_usd'] - active_proj_df['budget_usd']
        fig_proj_var = px.bar(active_proj_df.sort_values('variance'), x='name', y='variance', title='Budget Variance by Active Project',
                              labels={'name': 'Project', 'variance': 'Variance (USD)'}, color='variance', color_continuous_scale='RdYlGn_r')
        fig_proj_var.update_layout(coloraxis_showscale=False, xaxis_title=None)
        st.plotly_chart(fig_proj_var, use_container_width=True)
