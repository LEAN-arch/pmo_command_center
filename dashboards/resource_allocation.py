# pmo_command_center/dashboards/resource_allocation.py
"""
This module renders the Resource Allocation & Capacity Management dashboard.
It helps the PMO Director visualize resource deployment, identify bottlenecks,
and forecast future demand using a time-series model.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from prophet import Prophet
from utils.pmo_session_state_manager import SPMOSessionStateManager
from utils.plot_utils import create_resource_heatmap, create_resource_forecast_plot

@st.cache_data
def get_resource_forecast(_demand_history_df: pd.DataFrame, role: str, periods: int):
    """
    Trains a Prophet time-series model and returns a forecast for a specific role.
    The underscore prefix on the DataFrame parameter is a convention to indicate
    that the cached function should not hash the DataFrame's contents but rather
    rely on its identity, which is sufficient for this app's lifecycle.
    """
    df_role = _demand_history_df[_demand_history_df['role'] == role].copy()
    df_prophet = df_role[['date', 'demand_hours']].rename(columns={'date': 'ds', 'demand_hours': 'y'})
    
    if len(df_prophet) < 12: 
        return None

    model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False,
                    changepoint_prior_scale=0.05, seasonality_prior_scale=10.0)
    model.fit(df_prophet)
    
    future = model.make_future_dataframe(periods=periods, freq='MS')
    forecast = model.predict(future)
    
    return forecast

def render_resource_dashboard(ssm: SPMOSessionStateManager):
    """Renders the resource allocation and capacity dashboard."""
    st.header("👥 Resource Allocation & Capacity")
    st.caption("This is the **Cross-Functional Allocation & Utilization** dashboard. Analyze current allocations and use predictive forecasting to plan for future resource needs.")

    allocations = ssm.get_data("allocations")
    resources = ssm.get_data("resources")
    demand_history = ssm.get_data("resource_demand_history")

    if not resources:
        st.warning("No resource data available.")
        return

    # --- Current Allocation Analysis ---
    st.subheader("Current Resource Allocation")

    if not allocations:
        st.warning("No allocation data available.")
    else:
        alloc_df = pd.DataFrame(allocations)
        res_df = pd.DataFrame(resources)
        total_alloc_individual = alloc_df.groupby('resource_name')['allocated_hours_week'].sum().reset_index()
        utilization_df = pd.merge(res_df, total_alloc_individual, left_on='name', right_on='resource_name', how='left').fillna(0)
        utilization_df['utilization_pct'] = (utilization_df['allocated_hours_week'] / utilization_df['capacity_hours_week']) * 100
        
        over_allocated_count = len(utilization_df[utilization_df['utilization_pct'] > 100])
        
        kpi_cols = st.columns(2)
        kpi_cols[0].metric("Average Individual Utilization", f"{utilization_df['utilization_pct'].mean():.1f}%", help="The average workload across all personnel assigned to projects.")
        kpi_cols[1].metric("Over-Allocated Staff (>100%)", over_allocated_count, delta=over_allocated_count, delta_color="inverse", help="Number of individuals with allocated hours exceeding their weekly capacity.")
        
        fig_heatmap = create_resource_heatmap(alloc_df, utilization_df)
        st.plotly_chart(fig_heatmap, use_container_width=True)

    st.divider()

    # --- Predictive Forecasting Section ---
    st.subheader("🧠 AI-Powered Resource Forecasting")
    st.info("Select a functional role to forecast future demand based on historical trends and project pipeline data. This helps identify future resource gaps before they become critical, enabling proactive hiring and resource planning.", icon="🔮")

    if not demand_history:
        st.warning("No historical demand data available for forecasting.")
        return
        
    demand_df = pd.DataFrame(demand_history)
    demand_df['date'] = pd.to_datetime(demand_df['date'])
    
    res_df = pd.DataFrame(resources)
    
    col1, col2 = st.columns(2)
    with col1:
        role_to_forecast = st.selectbox("Select a Functional Role to Forecast", options=res_df['role'].unique())
    with col2:
        forecast_horizon = st.slider("Forecast Horizon (Months)", min_value=6, max_value=24, value=12)

    if role_to_forecast:
        forecast = get_resource_forecast(demand_df, role_to_forecast, forecast_horizon)
        
        if forecast is not None:
            fig_forecast = create_resource_forecast_plot(demand_df[demand_df['role'] == role_to_forecast].set_index('date'), forecast.set_index('ds'))
            st.plotly_chart(fig_forecast, use_container_width=True)

            role_capacity = res_df[res_df['role'] == role_to_forecast]['capacity_hours_week'].sum() * 4.33
            peak_demand = forecast['yhat'].max()
            
            st.metric(
                label=f"Peak Forecasted Monthly Demand for {role_to_forecast}",
                value=f"{peak_demand:,.0f} hours",
                delta=f"{(peak_demand - role_capacity):,.0f} vs. Capacity of {role_capacity:,.0f}",
                delta_color="inverse" if peak_demand > role_capacity else "normal",
                help="Compares the highest forecasted monthly demand to the current total capacity for that role. A positive delta indicates a future shortfall."
            )
        else:
            st.warning(f"Not enough historical data for '{role_to_forecast}' to generate a reliable forecast.")
