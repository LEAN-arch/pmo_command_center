"""
This module renders the tactical Resource Allocation dashboard.
It helps the PMO Director visualize the current deployment of resources
across all active projects and identify potential bottlenecks or burnout risks
by integrating data from the enterprise-wide resource pool.
"""
import streamlit as st
import pandas as pd
from utils.pmo_session_state_manager import SPMOSessionStateManager
from utils.plot_utils import create_resource_heatmap

def render_resource_dashboard(ssm: SPMOSessionStateManager):
    """Renders the tactical resource allocation and utilization dashboard."""
    st.header("👥 Resource Allocation")
    st.caption("This is the **Cross-Functional Allocation & Utilization** dashboard. Analyze current allocations across the enterprise to identify over-utilized resources and imbalances.")

    # --- Data Loading ---
    # ENHANCEMENT: Uses the full enterprise-wide resource pool
    allocations = ssm.get_data("allocations")
    resources = ssm.get_data("enterprise_resources")

    if not resources or not allocations:
        st.warning("No resource or allocation data available.")
        return

    alloc_df = pd.DataFrame(allocations)
    res_df = pd.DataFrame(resources)

    # --- Current Allocation Analysis ---
    st.subheader("Current Resource Utilization")
    
    # Calculate total allocated hours for each individual
    total_alloc_individual = alloc_df.groupby('resource_name')['allocated_hours_week'].sum().reset_index()
    
    # Merge allocation data with the resource master list
    utilization_df = pd.merge(res_df, total_alloc_individual, left_on='name', right_on='resource_name', how='left')
    # Fill NaN values for allocated hours with 0 for resources with no current assignments
    utilization_df['allocated_hours_week'] = utilization_df['allocated_hours_week'].fillna(0)
    
    # Calculate utilization percentage
    utilization_df['utilization_pct'] = utilization_df.apply(
        lambda row: (row['allocated_hours_week'] / row['capacity_hours_week']) * 100 if row['capacity_hours_week'] > 0 else 0,
        axis=1
    )
    
    over_allocated_count = len(utilization_df[utilization_df['utilization_pct'] > 100])
    
    kpi_cols = st.columns(3)
    kpi_cols[0].metric(
        "Average Individual Utilization", 
        f"{utilization_df[utilization_df['allocated_hours_week'] > 0]['utilization_pct'].mean():.1f}%", 
        help="The average workload across all personnel currently assigned to projects."
    )
    kpi_cols[1].metric(
        "Over-Allocated Staff (>100%)", 
        over_allocated_count, 
        delta=str(over_allocated_count) if over_allocated_count > 0 else None, 
        delta_color="inverse", 
        help="Number of individuals with allocated hours exceeding their weekly capacity. This is a key indicator of burnout risk."
    )
    kpi_cols[2].metric(
        "Total Resources in Pool",
        len(res_df),
        help="Total number of personnel in the enterprise resource pool available for projects."
    )
    
    st.subheader("Resource Allocation Heatmap")
    st.info("This heatmap visualizes the current weekly hour allocation for each resource across active projects. Red squares indicate heavy allocation, which can be a source of project risk. Hover for details.", icon="🔥")
    
    # Create a pivot table for the heatmap: resources as rows, projects as columns
    pivot_df = alloc_df.pivot_table(index='resource_name', columns='project_id', values='allocated_hours_week').fillna(0)
    
    if not pivot_df.empty:
        # Pass the pivot table and the full utilization data to the plotting function
        fig_heatmap = create_resource_heatmap(pivot_df, utilization_df)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.info("No projects currently have allocated resources.")
        
    st.divider()
    
    st.subheader("Detailed Utilization View")
    st.caption("A detailed table showing capacity, allocation, and utilization for every individual in the resource pool. Sort by utilization to find the most stretched resources.")
    
    st.dataframe(
        utilization_df[['name', 'role', 'location', 'capacity_hours_week', 'allocated_hours_week', 'utilization_pct']].sort_values('utilization_pct', ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            "name": "Resource Name",
            "role": "Functional Role",
            "location": "Location",
            "capacity_hours_week": st.column_config.NumberColumn("Capacity (Hrs/Wk)"),
            "allocated_hours_week": st.column_config.NumberColumn("Allocated (Hrs/Wk)"),
            "utilization_pct": st.column_config.ProgressColumn("Utilization %", min_value=0, max_value=150, format="%.0f%%")
        }
    )
