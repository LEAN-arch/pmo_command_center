"""
This module renders the Strategic Scenario Planning dashboard. It allows the
PMO Director to map projects to corporate goals, visualize the strategic roadmap,
and manage the portfolio's future state using an interactive "what-if" sandbox.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.pmo_session_state_manager import SPMOSessionStateManager

def render_strategy_dashboard(ssm: SPMOSessionStateManager):
    """Renders the strategic planning and 'what-if' scenario dashboard."""
    st.header("🎯 Strategic Scenario Planning")
    st.caption("Align the project portfolio with business strategy and simulate future scenarios using the 'What-If' Sandbox.")

    # --- Data Loading and Merging ---
    # The ssm.get_data() call will automatically return sandboxed data if active
    projects = ssm.get_data("projects")
    goals = ssm.get_data("strategic_goals")

    if not projects or not goals:
        st.warning("No project or strategic goal data available.")
        return

    proj_df = pd.DataFrame(projects)
    goals_df = pd.DataFrame(goals)
    aligned_df = pd.merge(proj_df, goals_df, left_on='strategic_goal_id', right_on='id', how='left', suffixes=('_proj', '_goal'))
    
    # Create a mapping for project names for efficient lookups
    project_name_map = pd.Series(proj_df.name.values, index=proj_df.id).to_dict()

    # --- "What-If" Sandbox Mode ---
    st.subheader("🔬 'What-If' Portfolio Sandbox")
    
    is_sandboxed = st.session_state.get('sandbox_mode', False)
    st.toggle(
        "Activate Sandbox Mode", 
        value=is_sandboxed,
        on_change=ssm.toggle_sandbox,
        help="Simulate changes to the portfolio without affecting the live data. Deactivate to reset."
    )

    if is_sandboxed:
        st.warning(
            "**SANDBOX MODE ACTIVE:** All changes shown on this page are part of a simulation. "
            "Deactivate the toggle above to reset and view live data.", 
            icon="⚠️"
        )
        active_projects_for_sim = proj_df[proj_df['health_status'] != 'Completed']
        
        if not active_projects_for_sim.empty:
            col1, col2, col3 = st.columns([2,1,1])
            with col1:
                selected_project_id = st.selectbox(
                    "Select a project to simulate an action:",
                    options=active_projects_for_sim['id'],
                    format_func=lambda x: f"{project_name_map.get(x, x)}"
                )
            with col2:
                if st.button("Simulate: Cancel Project", use_container_width=True, key=f"cancel_{selected_project_id}"):
                    ssm.add_sandbox_action({'type': 'cancel', 'project_id': selected_project_id})
                    st.rerun()
            with col3:
                if st.button("Simulate: Accelerate", use_container_width=True, help="Simulates a 20% budget increase to accelerate timeline.", key=f"accel_{selected_project_id}"):
                    ssm.add_sandbox_action({'type': 'accelerate', 'project_id': selected_project_id})
                    st.rerun()
    
    # --- Strategic Alignment KPIs (Dynamically update with sandbox) ---
    st.subheader("Strategic Investment KPIs")
    
    total_budget = aligned_df['budget_usd'].sum()
    total_active_projects = len(aligned_df[aligned_df['health_status'] != 'Completed'])

    kpi_cols = st.columns(3)
    kpi_cols[0].metric("Portfolio Scenario", "Sandbox Simulation" if is_sandboxed else "Live Data")
    kpi_cols[1].metric("Total Portfolio Budget", f"${total_budget:,.0f}")
    kpi_cols[2].metric("Total Active Projects", total_active_projects)

    # --- Strategic Allocation Chart ---
    st.subheader("Portfolio Budget Allocation by Strategic Goal")
    
    if not aligned_df.empty:
        # Fill unaligned projects with a specific category for visualization
        aligned_df['goal'] = aligned_df['goal'].fillna('Unaligned/Operational')
        budget_by_goal = aligned_df.groupby('goal')['budget_usd'].sum().reset_index()
        
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
    
    roadmap_df = aligned_df[aligned_df['health_status'] != 'Completed'].copy()
    if not roadmap_df.empty:
        # Ensure dates are in datetime format for plotting
        roadmap_df['start_date'] = pd.to_datetime(roadmap_df['start_date'])
        roadmap_df['end_date'] = pd.to_datetime(roadmap_df['end_date'])

        fig_roadmap = px.timeline(
            roadmap_df.sort_values('start_date', ascending=False),
            x_start="start_date",
            x_end="end_date",
            y="name",
            color="goal",
            hover_name="name",
            custom_data=['pm', 'start_date', 'end_date']
        )
        fig_roadmap.update_traces(
            hovertemplate="<b>%{hover_name}</b><br>" +
                          "PM: %{customdata[0]}<br>" +
                          "Start: %{customdata[1]|%Y-%m-%d}<br>" +
                          "End: %{customdata[2]|%Y-%m-%d}<extra></extra>"
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
        st.info("No active projects in the current scenario to display on the roadmap.")
