# pmo_command_center/dashboards/4_resource_allocation.py
"""
This module renders the Resource Allocation & Capacity Management dashboard.
It helps the PMO Director visualize resource deployment, identify bottlenecks,
and ensure optimal allocation of personnel.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.pmo_session_state_manager import SPMOSessionStateManager
from utils.plot_utils import create_resource_heatmap

def render_resource_dashboard(ssm: SPMOSessionStateManager):
    """Renders the resource allocation and capacity dashboard."""
    st.header("👥 Resource Allocation & Capacity Management")
    st.caption("Analyze resource deployment across the portfolio to identify bottlenecks, manage capacity, and ensure projects are staffed for success.")

    allocations = ssm.get_data("allocations")
    resources = ssm.get_data("resources")

    if not allocations or not resources:
        st.warning("No resource or allocation data available.")
        return

    alloc_df = pd.DataFrame(allocations)
    res_df = pd.DataFrame(resources)

    # --- Calculate Utilization by Individual and by Function ---
    total_alloc_individual = alloc_df.groupby('resource_name')['allocated_hours_week'].sum().reset_index()
    utilization_df = pd.merge(res_df, total_alloc_individual, left_on='name', right_on='resource_name', how='left').fillna(0)
    utilization_df['utilization_pct'] = (utilization_df['allocated_hours_week'] / utilization_df['capacity_hours_week']) * 100

    # Aggregate by function/role
    functional_utilization = utilization_df.groupby('role').agg(
        total_capacity=('capacity_hours_week', 'sum'),
        total_allocated=('allocated_hours_week', 'sum')
    ).reset_index()
    functional_utilization['utilization_pct'] = (functional_utilization['total_allocated'] / functional_utilization['total_capacity']) * 100

    # --- KPIs ---
    st.subheader("Resource Overview KPIs")
    over_allocated_count = len(utilization_df[utilization_df['utilization_pct'] > 100])
    avg_utilization = utilization_df['utilization_pct'].mean()
    most_strained_func = functional_utilization.loc[functional_utilization['utilization_pct'].idxmax()]

    kpi_cols = st.columns(3)
    kpi_cols[0].metric("Average Individual Utilization", f"{avg_utilization:.1f}%")
    kpi_cols[1].metric("Over-Allocated Staff (>100%)", over_allocated_count, delta=over_allocated_count, delta_color="inverse")
    kpi_cols[2].metric("Most Strained Function", f"{most_strained_func['role']}", f"{most_strained_func['utilization_pct']:.1f}% Utilized")

    # --- Visualizations ---
    viz_tabs = st.tabs(["**Allocation by Function**", "**Allocation by Individual**"])

    with viz_tabs[0]:
        st.subheader("Resource Allocation by Function")
        st.info("This view aggregates hours by role, helping to identify systemic capacity constraints in specific departments (e.g., 'Is RA/QA the bottleneck for all projects?').", icon="🏢")
        
        fig_func = px.bar(
            functional_utilization.sort_values('utilization_pct', ascending=False),
            x='role',
            y=['total_allocated', 'total_capacity'],
            title='Functional Capacity vs. Allocation',
            labels={'role': 'Function / Role', 'value': 'Total Hours per Week'},
            barmode='group'
        )
        st.plotly_chart(fig_func, use_container_width=True)

    with viz_tabs[1]:
        st.subheader("Individual Resource Allocation")
        st.info("This heatmap shows the weekly hour commitment of each person to each project. Bright red cells indicate individuals who are significantly over-allocated.", icon="🔥")
        
        fig_heatmap = create_resource_heatmap(alloc_df, utilization_df)
        st.plotly_chart(fig_heatmap, use_container_width=True)

        st.subheader("Detailed Individual Utilization")
        st.dataframe(
            utilization_df[['name', 'role', 'capacity_hours_week', 'allocated_hours_week', 'utilization_pct']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "utilization_pct": st.column_config.ProgressColumn("Utilization %", format="%.1f%%", min_value=0, max_value=120)
            }
        )
