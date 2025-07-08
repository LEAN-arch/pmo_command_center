# pmo_command_center/dashboards/strategic_planning.py
"""
This module renders the Strategic Planning & Pipeline dashboard. It allows the
PMO Director to map projects to corporate goals, visualize the strategic roadmap,
and manage the funnel of new initiatives.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.pmo_session_state_manager import SPMOSessionStateManager

def render_strategy_dashboard(ssm: SPMOSessionStateManager):
    """Renders the strategic planning and project pipeline dashboard."""
    st.header("🎯 Strategic Planning & Pipeline")
    st.caption("This is the **Future Initiatives and Strategic Alignment** dashboard. Align the project portfolio with business strategy and visualize the long-term roadmap.")

    projects = ssm.get_data("projects")
    goals = ssm.get_data("strategic_goals")

    if not projects or not goals:
        st.warning("No project or strategic goal data available.")
        return

    proj_df = pd.DataFrame(projects)
    goals_df = pd.DataFrame(goals)

    # --- Strategic Alignment Analysis ---
    st.subheader("Portfolio Alignment to Strategic Goals")
    st.info("This chart shows how the portfolio's budget is allocated across the company's key strategic objectives. It helps answer the critical business question: 'Are we putting our money where our strategy is?'", icon="💰")

    # Merge data to link projects with goals
    aligned_df = pd.merge(proj_df, goals_df, left_on='strategic_goal_id', right_on='id', how='left')
    
    # Group by strategic goal and sum the budget
    budget_by_goal = aligned_df.groupby('goal')['budget_usd'].sum().reset_index()

    fig_pie = px.pie(
        budget_by_goal,
        names='goal',
        values='budget_usd',
        title='Portfolio Budget Allocation by Strategic Goal',
        hole=0.4
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label', sort=False)
    st.plotly_chart(fig_pie, use_container_width=True)

    st.divider()

    # --- Strategic Roadmap ---
    st.subheader("Strategic Roadmap Timeline")
    st.info("A high-level Gantt chart visualizing the timeline of major projects, color-coded by the strategic goal they support. This is a key tool for long-term planning and executive communication.", icon="🗺️")

    # Filter out completed projects for a forward-looking roadmap
    roadmap_df = aligned_df[aligned_df['health_status'] != 'Completed'].copy()
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
        title="3-5 Year Strategic Project Roadmap",
        xaxis_title="Year",
        yaxis_title="Project",
        legend_title="Strategic Goal",
        height=500,
    )
    st.plotly_chart(fig_roadmap, use_container_width=True)

    st.divider()

    # --- New Initiatives Funnel (Placeholder for full feature) ---
    st.subheader("New Initiatives Pipeline")
    st.info("This section manages the funnel of new project ideas, from initial concept through feasibility to approval, providing a view into the future portfolio.", icon="🧪")
    
    st.info("Feature under construction: A full initiatives funnel with business case summaries would be managed here.", icon="🚧")
    # In a full app, this would be an editable table or kanban board
    # For now, a placeholder:
    st.write({
        "Idea Stage": ["New POC Platform Concept"],
        "Feasibility Study": ["NextGen Hemostasis Reagent (NPD-003)"],
        "Approved for Development": ["AcuStar NeoSTAT IL-6 Assay (NPD-001)"]
    })
