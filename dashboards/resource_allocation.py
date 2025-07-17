# pmo_command_center/dashboards/resource_allocation.py
"""
This module renders the tactical Resource Allocation dashboard.
It helps the PMO Director visualize the current deployment of resources
across all active projects and identify potential bottlenecks or burnout risks.
"""
import streamlit as st
import pandas as pd
from utils.pmo_session_state_manager import SPMOSessionStateManager
from utils.plot_utils import create_resource_heatmap

def render_resource_dashboard(ssm: SPMOSessionStateManager):
    """Renders the tactical resource allocation and utilization dashboard."""
    st.header("👥 Tactical Resource Allocation")
    st.caption("This is the **Cross-Functional Allocation & Utilization** dashboard. Analyze current allocations to identify over-utilized resources and imbalances.")

    # --- Data Loading ---
    allocations = ssm.get_data("allocations")
    resources = ssm.get_data("resources")

    if not resources or not allocations:
        st.warning("No resource or allocation data available.")
        return

    alloc_df = pd.DataFrame(allocations)
    res_df = pd.DataFrame(resources)

    # --- Current Allocation Analysis ---
    st.subheader("Current Resource Utilization")
    
    total_alloc_individual = alloc_df.groupby('resource_name')['allocated_hours_week'].sum().reset_index()
    utilization_df = pd.merge(res_df, total_alloc_individual, left_on='name', right_on='resource_name', how='left').fillna(0)
    
    # Ensure capacity is not zero to avoid division errors
    utilization_df['utilization_pct'] = utilization_df.apply(
        lambda row: (row['allocated_hours_week'] / row['capacity_hours_week']) * 100 if row['capacity_hours_week'] > 0 else 0,
        axis=1
    )
    
    over_allocated_count = len(utilization_df[utilization_df['utilization_pct'] > 100])
    
    kpi_cols = st.columns(2)
    kpi_cols[0].metric(
        "Average Individual Utilization", 
        f"{utilization_df['utilization_pct'].mean():.1f}%", 
        help="The average workload across all personnel assigned to projects."
    )
    kpi_cols[1].metric(
        "Over-Allocated Staff (>100%)", 
        over_allocated_count, 
        delta=str(over_allocated_count), 
        delta_color="inverse", 
        help="Number of individuals with allocated hours exceeding their weekly capacity. This is a key indicator of burnout risk."
    )
    
    st.subheader("Resource Allocation Heatmap")
    st.info("This heatmap visualizes the current weekly hour allocation for each resource across active projects. Red squares indicate heavy allocation, which can be a source of project risk.", icon="🔥")
    
    # Create pivot table for the heatmap
    pivot_df = alloc_df.pivot_table(index='resource_name', columns='project_id', values='allocated_hours_week').fillna(0)
    if not pivot_df.empty:
        fig_heatmap = create_resource_heatmap(pivot_df, utilization_df)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.info("No projects currently have allocated resources.")
