"""
This module renders the Strategic Scenario Planning dashboard. It allows the
PMO Director to map projects to corporate goals, visualize the strategic roadmap,
and now, to generate optimal portfolios using a prescriptive analytics engine.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.pmo_session_state_manager import SPMOSessionStateManager
from utils.optimization import optimize_portfolio # NEW: Import the optimization engine

def render_strategy_dashboard(ssm: SPMOSessionStateManager):
    """Renders the strategic planning, 'what-if' sandbox, and portfolio optimizer."""
    st.header("🎯 Strategic Scenario Planning & Optimization")
    st.caption("Align the portfolio with business strategy, simulate future scenarios, and generate optimal portfolios with prescriptive analytics.")

    # --- Data Loading (Sandbox-aware) ---
    projects = ssm.get_data("projects")
    goals = ssm.get_data("strategic_goals")
    allocations = ssm.get_data("allocations")
    resources = ssm.get_data("enterprise_resources")

    if not projects or not goals:
        st.warning("No project or strategic goal data available.")
        return

    proj_df = pd.DataFrame(projects)
    goals_df = pd.DataFrame(goals)
    alloc_df = pd.DataFrame(allocations)
    res_df = pd.DataFrame(resources)
    aligned_df = pd.merge(proj_df, goals_df, left_on='strategic_goal_id', right_on='id', how='left', suffixes=('_proj', '_goal'))
    project_name_map = pd.Series(proj_df.name.values, index=proj_df.id).to_dict()

    # --- Main Tabbed Interface ---
    tab_roadmap, tab_sandbox, tab_optimizer = st.tabs(["**Strategic Roadmap**", "**'What-If' Sandbox**", "**Portfolio Optimizer**"])

    # --- Tab 1: Strategic Roadmap (Existing Functionality) ---
    with tab_roadmap:
        st.subheader("Portfolio Budget Allocation by Strategic Goal")
        if not aligned_df.empty:
            aligned_df['goal'] = aligned_df['goal'].fillna('Unaligned/Operational')
            budget_by_goal = aligned_df.groupby('goal')['budget_usd'].sum().reset_index()
            fig_pie = px.pie(budget_by_goal, names='goal', values='budget_usd', title='Portfolio Budget Allocation', hole=0.4)
            fig_pie.update_traces(textposition='inside', textinfo='percent+label', sort=False)
            st.plotly_chart(fig_pie, use_container_width=True)

        st.divider()
        st.subheader("Strategic Roadmap Timeline")
        roadmap_df = aligned_df[aligned_df['health_status'] != 'Completed'].copy()
        if not roadmap_df.empty:
            fig_roadmap = px.timeline(roadmap_df.sort_values('start_date', ascending=False), x_start="start_date", x_end="end_date", y="name", color="goal", hover_name="name")
            fig_roadmap.update_layout(title="Active Project Roadmap", xaxis_title="Year", yaxis_title=None, legend_title="Strategic Goal", height=max(400, len(roadmap_df) * 35))
            st.plotly_chart(fig_roadmap, use_container_width=True)

    # --- Tab 2: 'What-If' Sandbox (Enhanced) ---
    with tab_sandbox:
        st.subheader("🔬 'What-If' Portfolio Sandbox")
        is_sandboxed = st.session_state.get('sandbox_mode', False)
        st.toggle("Activate Sandbox Mode", value=is_sandboxed, on_change=ssm.toggle_sandbox, help="Simulate changes to the portfolio without affecting the live data. Deactivate to reset.")

        if is_sandboxed:
            st.warning("**SANDBOX MODE ACTIVE:** All data in the app now reflects your simulation. Deactivate the toggle to reset.", icon="⚠️")
            active_projects_for_sim = proj_df[proj_df['health_status'] != 'Completed']
            if not active_projects_for_sim.empty:
                st.markdown("##### Simulate Project Actions")
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    selected_project_id = st.selectbox("Select a project:", options=active_projects_for_sim['id'], format_func=lambda x: f"{project_name_map.get(x, x)}")
                with col2:
                    if st.button("Sim: Cancel Project", use_container_width=True):
                        # In the new model, this just removes the project from the sandbox dataframe
                        sandbox_model = ssm._get_active_data_model()
                        sandbox_model['projects'] = [p for p in sandbox_model['projects'] if p['id'] != selected_project_id]
                        ssm.log_audit_event("Sandbox Simulation", f"Simulated cancellation of project '{selected_project_id}'.")
                        st.rerun()
                
                # NEW: Deeper resource simulation
                with col3:
                    if st.button("Sim: Reallocate Resources", use_container_width=True, help="Removes canceled project's resource load."):
                        ssm.reallocate_resources_from_project(selected_project_id)
                        st.rerun()

            st.divider()
            st.subheader("Simulated Strategic Investment KPIs")
            total_budget = aligned_df['budget_usd'].sum()
            total_active_projects = len(aligned_df[aligned_df['health_status'] != 'Completed'])
            kpi_cols = st.columns(3)
            kpi_cols[0].metric("Portfolio Scenario", "Sandbox Simulation")
            kpi_cols[1].metric("Total Portfolio Budget", f"${total_budget:,.0f}")
            kpi_cols[2].metric("Total Active Projects", total_active_projects)

    # --- Tab 3: Portfolio Optimizer (NEW) ---
    with tab_optimizer:
        st.subheader("🚀 Prescriptive Portfolio Optimizer")
        st.info("Define your strategic objectives and constraints, and let the analytics engine recommend the optimal portfolio of projects to fund.", icon="💡")

        with st.form("optimizer_form"):
            st.markdown("##### 1. Define Strategic Objective")
            objective = st.radio("Select the primary goal for this portfolio:", ('Maximize Strategic Value', 'Minimize Risk'), horizontal=True)

            st.markdown("##### 2. Set Portfolio Constraints")
            max_budget = st.slider("Maximum Total Portfolio Budget ($M)", min_value=1.0, max_value=50.0, value=20.0, step=0.5) * 1_000_000
            
            st.markdown("###### Key Resource Capacity Constraints (Total Hours/Week)")
            # Get key roles with the most allocations
            top_roles = alloc_df.groupby('resource_name').sum(numeric_only=True).nlargest(3, 'allocated_hours_week').index
            top_roles = res_df[res_df['name'].isin(top_roles)]['role'].unique()

            resource_constraints = {}
            for role in top_roles:
                total_capacity = res_df[res_df['role'] == role]['capacity_hours_week'].sum()
                resource_constraints[role] = st.slider(f"Max Hours for {role}", 0, int(total_capacity), int(total_capacity))

            submitted = st.form_submit_button("Optimize Portfolio", use_container_width=True, type="primary")

        if submitted:
            with st.spinner("Running optimization engine..."):
                # Use the live, unfiltered project list as candidates for optimization
                live_projects_df = pd.DataFrame(st.session_state[ssm._PMO_LIVE_DATA_KEY]['projects'])
                
                summary, result_df = optimize_portfolio(
                    projects_df=live_projects_df[live_projects_df['health_status'] != 'Completed'],
                    allocations_df=alloc_df,
                    resources_df=res_df,
                    constraints={'max_budget': max_budget, 'resource_constraints': resource_constraints},
                    objective=objective
                )
            
            st.subheader("Optimization Results")
            if result_df.empty:
                st.error(f"**Optimization Status:** {summary.get('status', 'Failed')}")
            else:
                st.success(f"**Optimization Status:** Optimal solution found!")
                
                kpi_cols = st.columns(4)
                kpi_cols[0].metric("Projects Selected", summary.get('num_projects_selected', 0))
                kpi_cols[1].metric("Total Budget Used", f"${summary.get('total_budget_used', 0):,.0f}")
                kpi_cols[2].metric("Total Strategic Value", f"{summary.get('total_strategic_value', 0):.0f}")
                kpi_cols[3].metric("Average Portfolio Risk", f"{summary.get('average_portfolio_risk', 0):.1f}")
                
                st.markdown("##### Recommended Portfolio")
                st.dataframe(result_df[['id', 'name', 'strategic_value', 'risk_score', 'budget_usd']], use_container_width=True, hide_index=True)

                not_selected_df = live_projects_df[~live_projects_df['id'].isin(result_df['id'])]
                with st.expander("View projects not selected due to constraints"):
                    st.dataframe(not_selected_df[['id', 'name', 'strategic_value', 'risk_score', 'budget_usd']], use_container_width=True, hide_index=True)
