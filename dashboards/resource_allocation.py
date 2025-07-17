# pmo_command_center/dashboards/resource_allocation.py
"""
This module renders the Resource Allocation & Capacity Management dashboard.
It helps the PMO Director visualize resource deployment, identify bottlenecks,
and forecast future demand using a time-series model.
"""
import streamlit as st
import pandas as pd
from prophet import Prophet
from utils.pmo_session_state_manager import SPMOSessionStateManager
from utils.plot_utils import create_resource_heatmap, create_capacity_plan_chart

@st.cache_data
def get_resource_forecast(_demand_history_df: pd.DataFrame, role: str, periods: int):
    """
    Trains a Prophet time-series model and returns a forecast for a specific role.
    The underscore prefix on the DataFrame parameter is a convention to indicate
    that the cached function should not hash the DataFrame's contents.
    """
    df_role = _demand_history_df[_demand_history_df['role'] == role].copy()
    df_role['date'] = pd.to_datetime(df_role['date'])
    df_prophet = df_role[['date', 'demand_hours']].rename(columns={'date': 'ds', 'demand_hours': 'y'})

    if len(df_prophet) < 12:
        return None # Not enough data for a reliable forecast

    model = Prophet(
        yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False,
        changepoint_prior_scale=0.05, seasonality_prior_scale=10.0
    )
    model.fit(df_prophet)

    future = model.make_future_dataframe(periods=periods, freq='MS')
    forecast = model.predict(future)
    return forecast

def render_resource_dashboard(ssm: SPMOSessionStateManager):
    """Renders the resource allocation and capacity dashboard."""
    st.header("👥 Resource Allocation & Capacity")
    st.caption("Analyze current allocations and use predictive forecasting to plan for future resource needs.")

    # --- Data Loading ---
    allocations = ssm.get_data("allocations")
    resources = ssm.get_data("resources")
    demand_history = ssm.get_data("resource_demand_history")

    if not resources:
        st.warning("No resource data available.")
        return

    res_df = pd.DataFrame(resources)

    # --- Tabbed Interface ---
    tab1, tab2 = st.tabs(["**Strategic Capacity Planning**", "**Current Tactical Allocation**"])

    # --- Strategic Capacity Planning Tab ---
    with tab1:
        st.subheader("🧠 AI-Powered Resource Forecasting & Capacity Planning")
        st.info(
            "This tool answers the critical question: **'Do we have the right people to execute our future project pipeline?'** "
            "It uses AI to forecast demand for key roles and compares it against our current capacity, enabling proactive hiring and resource planning.",
            icon="🔮"
        )
        if not demand_history:
            st.warning("No historical demand data available for forecasting.")
            return

        demand_df = pd.DataFrame(demand_history)
        capacity_per_role = res_df.groupby('role')['capacity_hours_week'].sum() * 4.33  # Monthly capacity

        col1, col2 = st.columns(2)
        with col1:
            role_to_forecast = st.selectbox("Select a Functional Role to Forecast", options=res_df['role'].unique())
        with col2:
            forecast_horizon = st.slider("Forecast Horizon (Months)", min_value=6, max_value=24, value=12)

        if role_to_forecast:
            forecast = get_resource_forecast(demand_df, role_to_forecast, forecast_horizon)

            if forecast is not None:
                fig_capacity = create_capacity_plan_chart(forecast, capacity_per_role, role_to_forecast)
                st.plotly_chart(fig_capacity, use_container_width=True)

                # Analyze and display the future gap
                future_demand = forecast[forecast['ds'] > pd.to_datetime('today')].copy()
                future_demand['gap'] = future_demand['yhat'] - capacity_per_role.get(role_to_forecast, 0)
                peak_gap = future_demand['gap'].max()

                if peak_gap > 0:
                    st.error(
                        f"**Projected Shortfall:** A peak resource gap of **{peak_gap:,.0f} hours/month** is predicted for **{role_to_forecast}**. "
                        "Action may be required (e.g., hiring, re-prioritizing projects) to mitigate this future constraint.",
                        icon="🚨"
                    )
                else:
                    st.success(
                        f"**Sufficient Capacity:** Current capacity for **{role_to_forecast}** appears sufficient to meet forecasted demand for the next {forecast_horizon} months.",
                        icon="✅"
                    )
            else:
                st.warning(f"Not enough historical data for '{role_to_forecast}' to generate a reliable forecast.")

    # --- Current Tactical Allocation Tab ---
    with tab2:
        st.subheader("Current Resource Allocation (Tactical View)")
        st.caption("A heatmap visualizing the current weekly hour allocation for each resource across active projects.")

        if not allocations:
            st.warning("No allocation data available.")
        else:
            alloc_df = pd.DataFrame(allocations)
            total_alloc_individual = alloc_df.groupby('resource_name')['allocated_hours_week'].sum().reset_index()
            utilization_df = pd.merge(res_df, total_alloc_individual, left_on='name', right_on='resource_name', how='left').fillna(0)
            utilization_df['utilization_pct'] = (utilization_df['allocated_hours_week'] / utilization_df['capacity_hours_week']) * 100

            over_allocated_count = len(utilization_df[utilization_df['utilization_pct'] > 100])

            kpi_cols = st.columns(2)
            kpi_cols[0].metric("Average Individual Utilization", f"{utilization_df['utilization_pct'].mean():.1f}%", help="The average workload across all personnel assigned to projects.")
            kpi_cols[1].metric("Over-Allocated Staff (>100%)", over_allocated_count, delta=str(over_allocated_count), delta_color="inverse", help="Number of individuals with allocated hours exceeding their weekly capacity.")

            # Create pivot table for the heatmap
            pivot_df = alloc_df.pivot_table(index='resource_name', columns='project_id', values='allocated_hours_week').fillna(0)
            if not pivot_df.empty:
                fig_heatmap = create_resource_heatmap(pivot_df, utilization_df)
                st.plotly_chart(fig_heatmap, use_container_width=True)
            else:
                st.info("No projects currently have allocated resources.")
