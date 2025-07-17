# pmo_command_center/dashboards/financial_overview.py
"""
This module renders the Financial & Capacity Planning dashboard. It provides deep
financial analysis, including Earned Value Management (EVM) metrics, and integrates
resource forecasting with capacity planning to ensure strategic alignment of budgets
and personnel.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import IsolationForest
from prophet import Prophet
from utils.pmo_session_state_manager import SPMOSessionStateManager
from utils.plot_utils import create_financial_burn_chart, create_evm_performance_chart, create_capacity_plan_chart

@st.cache_data
def find_spending_anomalies(_fin_df: pd.DataFrame):
    """Uses Isolation Forest to detect anomalous monthly spending."""
    if _fin_df.empty or 'type' not in _fin_df.columns:
        return pd.DataFrame()

    actuals_df = _fin_df[_fin_df['type'] == 'Actuals'].copy()
    if actuals_df.empty:
        return pd.DataFrame()

    monthly_spend = actuals_df.groupby([pd.to_datetime(actuals_df['date']).dt.to_period('M'), 'project_id'])['amount'].sum().reset_index()
    if len(monthly_spend) < 2:
        return pd.DataFrame()

    model = IsolationForest(contamination='auto', random_state=42)
    predictions = model.fit_predict(monthly_spend[['amount']])

    monthly_spend['anomaly'] = predictions
    anomalous_data = monthly_spend[monthly_spend['anomaly'] == -1].copy()
    if not anomalous_data.empty:
        anomalous_data['date'] = anomalous_data['date'].dt.to_timestamp()
    return anomalous_data

@st.cache_data
def get_resource_forecast(_demand_history_df: pd.DataFrame, role: str, periods: int):
    """Trains a Prophet time-series model and returns a forecast for a specific role."""
    df_role = _demand_history_df[_demand_history_df['role'] == role].copy()
    df_prophet = df_role[['date', 'demand_hours']].rename(columns={'date': 'ds', 'demand_hours': 'y'})
    if len(df_prophet) < 12:
        return None

    model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False, changepoint_prior_scale=0.05)
    model.fit(df_prophet)
    future = model.make_future_dataframe(periods=periods, freq='MS')
    forecast = model.predict(future)
    return forecast

def render_financial_dashboard(ssm: SPMOSessionStateManager):
    """Renders the portfolio financial analysis and capacity planning dashboard."""
    st.header("💰 Financial & Capacity Planning")
    st.caption("Monitor financial performance with EVM, detect spending anomalies, and align future resource needs with capacity.")

    # --- Data Loading ---
    projects = ssm.get_data("projects")
    financials = ssm.get_data("financials")
    resources = ssm.get_data("resources")
    demand_history = ssm.get_data("resource_demand_history")

    if not projects:
        st.warning("No project data available.")
        return

    proj_df = pd.DataFrame(projects)
    fin_df = pd.DataFrame(financials)

    # --- Tabbed Interface ---
    tab1, tab2, tab3 = st.tabs(["**Portfolio Financial Health**", "**Earned Value Management (EVM)**", "**Capacity Planning**"])

    # --- Portfolio Financial Health Tab ---
    with tab1:
        st.subheader("Portfolio Financial Health")
        total_budget = proj_df['budget_usd'].sum()
        total_actuals = proj_df['actuals_usd'].sum()
        portfolio_eac = proj_df['eac_usd'].sum()

        kpi_cols = st.columns(3)
        kpi_cols[0].metric("Total Portfolio Budget (BAC)", f"${total_budget:,.0f}")
        kpi_cols[1].metric("Total Actuals to Date (AC)", f"${total_actuals:,.0f}")
        kpi_cols[2].metric("Forecast at Completion (EAC)", f"${portfolio_eac:,.0f}", delta=f"${(portfolio_eac - total_budget):,.0f} vs BAC", delta_color="inverse")

        st.subheader("🧠 AI-Powered Anomaly Detection in Project Spend")
        anomalies = find_spending_anomalies(fin_df)
        if not anomalies.empty:
            st.error(f"**{len(anomalies)} unusual spending events detected.** These months may warrant investigation.", icon="🚨")
        else:
            st.success("No significant spending anomalies detected in historical data.", icon="✅")

        anomaly_dates = anomalies['date'].tolist() if not anomalies.empty else None
        fig_portfolio_burn = create_financial_burn_chart(fin_df, "Portfolio Financial Burn", anomaly_dates)
        st.plotly_chart(fig_portfolio_burn, use_container_width=True)

        st.subheader("Spend Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.info("Analyze how the portfolio budget is distributed across spending categories.", icon="📊")
            actuals_by_cat = fin_df[fin_df['type'] == 'Actuals'].groupby('category')['amount'].sum().reset_index()
            fig_cat_spend = px.pie(actuals_by_cat, names='category', values='amount', title='Actual Spend by Category (Portfolio-wide)', hole=0.4)
            st.plotly_chart(fig_cat_spend, use_container_width=True)
        with col2:
            st.info("Compare budget variance for each active project to identify top contributors.", icon="🎯")
            active_proj_df = proj_df[proj_df['health_status'] != 'Completed'].copy()
            active_proj_df['variance'] = active_proj_df['actuals_usd'] - active_proj_df['budget_usd']
            fig_proj_var = px.bar(active_proj_df.sort_values('variance'), x='name', y='variance', title='Budget Variance by Active Project',
                                  labels={'name': 'Project', 'variance': 'Variance (USD)'}, color='variance', color_continuous_scale='RdYlGn_r')
            fig_proj_var.update_layout(coloraxis_showscale=False, xaxis_title=None)
            st.plotly_chart(fig_proj_var, use_container_width=True)

    # --- Earned Value Management Tab ---
    with tab2:
        st.subheader("Earned Value Management Analysis")
        st.info(
            "**Cost Performance Index (CPI)** and **Schedule Performance Index (SPI)** are the gold standards for objectively measuring project performance. "
            "A value **> 1.0 is favorable** (under budget or ahead of schedule), while a value **< 1.0 is unfavorable**.",
            icon="📈"
        )
        fig_evm = create_evm_performance_chart(proj_df)
        st.plotly_chart(fig_evm, use_container_width=True)

    # --- Capacity Planning Tab ---
    with tab3:
        st.subheader("Strategic Capacity Planning")
        st.info(
            "This tool answers the critical question: **'Do we have the right people to execute our future project pipeline?'** "
            "It uses AI to forecast demand for key roles and compares it against our current capacity, enabling proactive hiring decisions.",
            icon="🔮"
        )
        if not demand_history or not resources:
            st.warning("Resource demand history or capacity data is not available.")
            return

        demand_df = pd.DataFrame(demand_history)
        demand_df['date'] = pd.to_datetime(demand_df['date'])
        res_df = pd.DataFrame(resources)
        
        # Calculate capacity per role
        capacity_per_role = res_df.groupby('role')['capacity_hours_week'].sum() * 4.33 # Monthly capacity
        
        role_to_forecast = st.selectbox("Select a Functional Role to Forecast", options=res_df['role'].unique())
        
        if role_to_forecast:
            forecast = get_resource_forecast(demand_df, role_to_forecast, 12)
            if forecast is not None:
                fig_capacity = create_capacity_plan_chart(forecast, capacity_per_role, role_to_forecast)
                st.plotly_chart(fig_capacity, use_container_width=True)
                
                # Identify future state
                future_demand = forecast[forecast['ds'] > pd.to_datetime('today')].copy()
                future_demand['gap'] = future_demand['yhat'] - capacity_per_role[role_to_forecast]
                
                peak_gap = future_demand['gap'].max()
                if peak_gap > 0:
                    st.error(f"**Projected Shortfall:** A peak resource gap of **{peak_gap:,.0f} hours/month** is predicted for **{role_to_forecast}**. "
                             "Action may be required (e.g., hiring, re-prioritizing projects) to mitigate this future constraint.", icon="🚨")
                else:
                    st.success(f"**Sufficient Capacity:** Current capacity for **{role_to_forecast}** appears sufficient to meet forecasted demand for the next 12 months.", icon="✅")
            else:
                 st.warning(f"Not enough historical data for '{role_to_forecast}' to generate a reliable forecast.")
