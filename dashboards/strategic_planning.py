# pmo_command_center/dashboards/strategic_planning.py
"""
This module renders the Strategic Planning & Alignment dashboard. It allows the
PMO Director to map projects to corporate goals, interactively analyze the
portfolio's strategic alignment, and visualize the long-term roadmap.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.pmo_session_state_manager import SPMOSessionStateManager

def render_strategy_dashboard(ssm: SPMOSessionStateManager):
    """Renders the strategic planning and project pipeline dashboard."""
    st.header("🎯 Strategic Alignment & Roadmap")
    st.caption("Align the project portfolio with business strategy, analyze investment allocation, and visualize the long-term roadmap.")

    # --- Data Loading and Merging ---
    projects = ssm.get_data("projects")
    goals = ssm.get_data("strategic_goals")

    if not projects or not goals:
        st.warning("No project or strategic goal data available.")
        return

    proj_df = pd.DataFrame(projects)
    goals_df = pd.DataFrame(goals)
    aligned_df = pd.merge(proj_df, goals_df, left_on='strategic_goal_id', right_on='id', how='left', suffixes=('_proj', '_goal'))

    # --- Interactive Goal Selection ---
    st.subheader("Analysis by Strategic Goal")
    st.info(
        "Select a specific strategic goal to filter the entire dashboard. This allows for a deep-dive analysis into how the portfolio is supporting "
        "each of Werfen's key business objectives.",
        icon="🔎"
    )

    goal_list = ['All Strategic Goals'] + goals_df['goal'].tolist()
    selected_goal = st.selectbox("Filter by a Strategic Goal", options=goal_list)

    # Filter the main dataframe based on selection
    if selected_goal != 'All Strategic Goals':
        filtered_aligned_df = aligned_df[aligned_df['goal'] == selected_goal].copy()
    else:
        filtered_aligned_df = aligned_df.copy()

    # --- Strategic Alignment KPIs ---
    st.subheader("Strategic Investment KPIs")
    
    total_budget = filtered_aligned_df['budget_usd'].sum()
    total_projects = len(filtered_aligned_df)
    total_active_projects = len(filtered_aligned_df[filtered_aligned_df['health_status'] != 'Completed'])

    kpi_cols = st.columns(3)
    kpi_cols[0].metric("Selected Goal(s)", selected_goal)
    kpi_cols[1].metric("Total Aligned Budget", f"${total_budget:,.0f}")
    kpi_cols[2].metric("Total Active Projects Aligned", total_active_projects)

    # --- Strategic Allocation Chart ---
    st.subheader("Portfolio Budget Allocation by Strategic Goal")
    
    budget_by_goal = filtered_aligned_df.groupby('goal')['budget_usd'].sum().reset_index()
    fig_pie = px.pie(
        budget_by_goal,
        names='goal',
        values='budget_usd',
        title='Portfolio Budget Allocation',
        hole=0.4
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label', sort=False)
    st.plotly_chart(fig_pie, use_container_width=True)

    st.divider()

    # --- Strategic Roadmap Timeline ---
    st.subheader("Strategic Roadmap Timeline")
    st.info(
        "A high-level Gantt chart visualizing the timeline of major projects, color-coded by the strategic goal they support. "
        "This is a key tool for long-term planning and executive communication.",
        icon="🗺️"
    )

    roadmap_df = filtered_aligned_df[filtered_aligned_df['health_status'] != 'Completed'].copy()
    if not roadmap_df.empty:
        roadmap_df['start_date'] = pd.to_datetime(roadmap_df['start_date'])
        roadmap_df['end_date'] = pd.to_datetime(roadmap_df['end_date'])

        fig_roadmap = px.timeline(
            roadmap_df.sort_values('start_date', ascending=False),
            x_start="start_date",
            x_end="end_date",
            y="name",
            color="goal",
            hover_name="name",
            custom_data=['pm', 'phase', 'regulatory_path']
        )
        fig_roadmap.update_traces(
            hovertemplate="<b>%{hover_name}</b><br>" +
                          "Phase: %{customdata[1]} | PM: %{customdata[0]}<br>" +
                          "Reg. Path: %{customdata[2]}<extra></extra>"
        )
        fig_roadmap.update_layout(
            title="Active Project Roadmap",
            xaxis_title="Year",
            yaxis_title=None,
            legend_title="Strategic Goal",
            height=max(400, len(roadmap_df) * 35), # Dynamic height
        )
        st.plotly_chart(fig_roadmap, use_container_width=True)
    else:
        st.info(f"No active projects are aligned with the selected goal: '{selected_goal}'.")

    st.divider()

    # --- New Initiatives Funnel (Placeholder) ---
    st.subheader("New Initiatives Pipeline")
    st.info(
        "Feature under construction: A full initiatives funnel with business case summaries and scoring would be managed here, "
        "providing a view into the future portfolio.",
        icon="🚧"
    )
