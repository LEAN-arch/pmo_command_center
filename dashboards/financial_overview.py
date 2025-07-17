"""
This module renders the Financial & Capacity Planning dashboard. It provides deep
financial analysis, including Earned Value Management (EVM) metrics, and integrates
resource forecasting with capacity planning to ensure strategic alignment of budgets
and personnel.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from prophet import Prophet
from utils.pmo_session_state_manager import SPMOSessionStateManager
from utils.plot_utils import create_financial_burn_chart, create_evm_performance_chart, create_capacity_plan_chart

@st.cache_data
def get_resource_forecast(_demand_history_df: pd.DataFrame, role: str, periods: int):
    """
    Trains a Prophet time-series model and returns a forecast for a specific role.
    Caches the forecast result to avoid retraining on every interaction.
    """
    df_role = _demand_history_df[_demand_history_df['role'] == role].copy()
    df_role['date'] = pd.to_datetime(df_role['date'])
    df_prophet = df_role[['date', 'demand_hours']].rename(columns={'date': 'ds', 'demand_hours': 'y'})
    
    # Prophet requires at least 2 data points, but more is better for a meaningful forecast.
    if len(df_prophet) < 12:
        return None # Not enough historical data for a reliable forecast

    model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False, changepoint_prior_scale=0.05)
    model.fit(df_prophet)
    future = model.make_future_dataframe(periods=periods, freq='MS') # Monthly forecast
    forecast = model.predict(future)
    return forecast

def render_financial_dashboard(ssm: SPMOSessionStateManager):
    """Renders the portfolio financial analysis and capacity planning dashboard."""
    st.header("💰 Financial & Capacity Planning")
    st.caption("Monitor financial performance with EVM, detect spending anomalies, and align future resource needs with capacity.")

    # --- Data Loading ---
    projects = ssm.get_data("projects")
    # --- FIX: Corrected typo from 'sm' to 'ssm' ---
    financials = ssm.get_data("financials")
    resources = ssm.get_data("enterprise_resources")
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
        
        # Calculate EAC using a standard formula as a baseline
        proj_df['formula_eac'] = proj_df.apply(
            lambda row: row['budget_usd'] / row['cpi'] if row.get('cpi', 0) > 0 else row['budget_usd'],
            axis=1
        )
        portfolio_formula_eac = proj_df['formula_eac'].sum()
        portfolio_predicted_eac = proj_df['predicted_eac_usd'].sum()

        kpi_cols = st.columns(4)
        kpi_cols[0].metric("Total Portfolio Budget (BAC)", f"${total_budget:,.0f}")
        kpi_cols[1].metric("Total Actuals to Date (AC)", f"${total_actuals:,.0f}")
        kpi_cols[2].metric("Formula EAC", f"${portfolio_formula_eac:,.0f}", delta=f"${(portfolio_formula_eac - total_budget):,.0f} vs BAC", delta_color="inverse")
        kpi_cols[3].metric("AI-Predicted EAC", f"${portfolio_predicted_eac:,.0f}", delta=f"${(portfolio_predicted_eac - total_budget):,.0f} vs BAC", delta_color="inverse", help="AI forecast of final cost based on performance and project characteristics.")

        st.subheader("Portfolio Financial Burn")
        # To create a portfolio burn chart, we aggregate financial data across all projects
        portfolio_fin_df = fin_df.groupby(['date', 'type'])['amount'].sum().reset_index()
        fig_portfolio_burn = create_financial_burn_chart(portfolio_fin_df, "Cumulative Portfolio Financial Burn")
        st.plotly_chart(fig_portfolio_burn, use_container_width=True)

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
        res_df = pd.DataFrame(resources)
        
        # Calculate total capacity per role in hours per month (avg 4.33 weeks/month)
        capacity_per_role = res_df.groupby('role')['capacity_hours_week'].sum() * 4.33
        
        role_to_forecast = st.selectbox("Select a Functional Role to Forecast", options=sorted(res_df['role'].unique()))
        
        if role_to_forecast:
            with st.spinner(f"Generating 12-month demand forecast for {role_to_forecast}..."):
                forecast = get_resource_forecast(demand_df, role_to_forecast, 12)
            
            if forecast is not None:
                fig_capacity = create_capacity_plan_chart(forecast, capacity_per_role, role_to_forecast)
                st.plotly_chart(fig_capacity, use_container_width=True)
                
                # Analyze the forecast to find the biggest future gap
                future_demand = forecast[forecast['ds'] > pd.to_datetime('today')].copy()
                future_demand['gap'] = future_demand['yhat'] - capacity_per_role.get(role_to_forecast, 0)
                peak_gap = future_demand['gap'].max()

                if peak_gap > 0:
                    st.error(f"**Projected Shortfall:** A peak resource gap of **{peak_gap:,.0f} hours/month** is predicted for **{role_to_forecast}**. Proactive hiring or contractor engagement may be required.", icon="🚨")
                else:
                    st.success(f"**Sufficient Capacity:** Current capacity for **{role_to_forecast}** appears sufficient to meet forecasted demand.", icon="✅")
            else:
                 st.warning(f"Not enough historical data for '{role_to_forecast}' to generate a reliable forecast. At least 12 months of data is recommended.")
