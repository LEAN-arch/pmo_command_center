"""
This module renders the consolidated PMO Health & Maturity dashboard. It provides
a 360-degree view of the PMO's operational excellence, combining departmental
budget management, team performance, process effectiveness, and AI-driven
systemic insights.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.pmo_session_state_manager import SPMOSessionStateManager
from utils.plot_utils import create_gate_variance_plot, create_project_cluster_plot
from utils.ml_models import get_project_clusters

def render_pmo_health_dashboard(ssm: SPMOSessionStateManager):
    """Renders the comprehensive dashboard for analyzing PMO maturity and effectiveness."""
    st.header("📈 PMO Health & Maturity")
    st.caption("Measure and improve the effectiveness of the PMO function with metrics on budget, team, process performance, and AI-powered insights.")

    # --- Data Loading ---
    pmo_budget_data = ssm.get_data("pmo_department_budget")
    pmo_team_data = ssm.get_data("pmo_team")
    projects_data = ssm.get_data("projects")
    gate_data = ssm.get_data("phase_gate_data")
    adherence_data = ssm.get_data("process_adherence")

    if not projects_data:
        st.warning("No project data available for full analysis.")
        return

    proj_df = pd.DataFrame(projects_data)

    # --- Main Tabbed Interface ---
    tab_ops, tab_team, tab_perf, tab_insights, tab_ai = st.tabs([
        "**PMO Operations & Budget**", 
        "**PMO Team & Performance**", 
        "**Process Performance**",
        "**Process Insights & Adherence**",
        "**AI-Powered Archetype Analysis**"
    ])

    # --- Tab 1: PMO Operations & Budget ---
    with tab_ops:
        st.subheader("PMO Departmental Financials & Budgeting")
        st.info("Manage the PMO's operational budget, including staffing, training, tooling, and other administrative expenses.", icon="💼")

        if not pmo_budget_data:
            st.warning("No PMO departmental budget data available.")
        else:
            budget_year = pmo_budget_data.get("year", "N/A")
            budget_items_df = pd.DataFrame(pmo_budget_data.get("budget_items", []))

            if not budget_items_df.empty:
                total_budget = budget_items_df['budget'].sum()
                total_actuals = budget_items_df['actuals'].sum()
                total_forecast = budget_items_df['forecast'].sum()

                kpi_cols = st.columns(3)
                kpi_cols[0].metric("Total Annual Budget", f"${total_budget:,.0f}")
                kpi_cols[1].metric("YTD Actuals", f"${total_actuals:,.0f}")
                kpi_cols[2].metric("Full Year Forecast", f"${total_forecast:,.0f}", delta=f"${(total_forecast - total_budget):,.0f} vs Budget", delta_color="inverse")
                
                fig = go.Figure()
                fig.add_trace(go.Bar(y=budget_items_df['category'], x=budget_items_df['budget'], name='Annual Budget', orientation='h', marker_color='grey'))
                fig.add_trace(go.Bar(y=budget_items_df['category'], x=budget_items_df['forecast'], name='Full Year Forecast', orientation='h', marker_color='orange'))
                fig.add_trace(go.Bar(y=budget_items_df['category'], x=budget_items_df['actuals'], name='YTD Actuals', orientation='h', marker_color='crimson'))
                fig.update_layout(barmode='group', title_text=f"PMO Operational Spend for {budget_year}", yaxis_autorange='reversed', height=400)
                st.plotly_chart(fig, use_container_width=True)

    # --- Tab 2: PMO Team & Performance ---
    with tab_team:
        st.subheader("PMO Team Management")
        st.info("Visualize roles, responsibilities, performance scores, certification statuses, and development paths for the PMO team.", icon="🤝")

        if not pmo_team_data:
            st.warning("No PMO team data available.")
        else:
            team_df = pd.DataFrame(pmo_team_data)
            pm_assignments = proj_df[proj_df['health_status'] != 'Completed'].groupby('pm')['id'].apply(lambda x: ', '.join(x)).reset_index().rename(columns={'id': 'assigned_projects', 'pm': 'name'})
            team_details_df = pd.merge(team_df, pm_assignments, on='name', how='left').fillna({"assigned_projects": "None"})

            kpi_cols = st.columns(3)
            kpi_cols[0].metric("Total PMO Headcount", len(team_df))
            kpi_cols[1].metric("Average Performance Score", f"{team_df['performance_score'].mean():.2f} / 5.0")
            kpi_cols[2].metric("PMP Certified Staff", f"{team_df['certification_status'].str.contains('PMP').sum()}")
            
            st.dataframe(team_details_df, use_container_width=True, hide_index=True, column_config={
                "name": "Team Member", "role": "Role",
                "performance_score": st.column_config.ProgressColumn("Performance", format="%.2f/5", min_value=0, max_value=5),
                "certification_status": "Certifications", "development_path": "Development Focus", "assigned_projects": "Current Projects"
            })

    # --- Tab 3: Process Performance ---
    with tab_perf:
        st.subheader("Process Performance & Trend Analysis")
        st.info("Analyze the historical performance of core PMO processes to identify systemic bottlenecks and measure efficiency gains over time.", icon="⏱️")
        gate_df = pd.DataFrame(gate_data) if gate_data else pd.DataFrame()
        
        st.markdown("##### Gate Schedule Variance")
        st.caption("Measures the average delay for each phase-gate across completed projects. Negative values indicate systemic lateness for a specific gate.")
        fig_variance = create_gate_variance_plot(gate_df)
        st.plotly_chart(fig_variance, use_container_width=True)

        st.markdown("##### Project Cycle Time Analysis")
        st.caption("Measures the total duration of completed projects. A decreasing trend indicates increasing PMO efficiency.")
        completed_projects = proj_df[proj_df['final_outcome'].notna()].copy()
        if not completed_projects.empty:
            completed_projects['duration_days'] = (completed_projects['end_date'] - completed_projects['start_date']).dt.days
            fig_cycle_time = px.box(completed_projects, x='project_type', y='duration_days', points="all", title="Project Cycle Time by Type", labels={'project_type': 'Project Type', 'duration_days': 'Total Duration (Days)'})
            st.plotly_chart(fig_cycle_time, use_container_width=True)
        else:
            st.info("No completed projects are available yet to calculate historical cycle times.")
            
    # --- Tab 4: Process Insights & Adherence ---
    with tab_insights:
        st.subheader("Process Insights & Methodology Adherence")
        st.info("Track methodology adoption levels and document retrospectives to create a closed-loop, continuous improvement cycle.", icon="🔄")

        adherence_df = pd.DataFrame(adherence_data)
        if not adherence_df.empty:
            st.markdown("##### Methodology Adherence Trends")
            fig = px.line(adherence_df, x='quarter', y='value', color='metric', markers=True, title="PMO Process Adherence by Quarter", labels={"value": "Adherence (%)", "metric": "Adherence KPI"})
            fig.update_layout(yaxis_range=[0,100], legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("##### Improvement Initiatives & Retrospectives")
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.markdown("###### Recent Improvement Initiatives")
                st.markdown("- **Q2 '24:** Deployed standardized PPT reporting to reduce admin time. (In Progress)\n- **Q1 '24:** Implemented pre-gate DHF checklist. (Completed)")
        with col2:
            with st.container(border=True):
                st.markdown("###### Key Retrospective Learnings")
                st.markdown("- **NPD-H01:** Involve tech architecture earlier for connectivity projects.\n- **LCM-001:** Strict change control was highly effective in managing scope.")

    # --- Tab 5: AI-Powered Archetype Analysis ---
    with tab_ai:
        st.subheader("AI-Powered Project Archetype Analysis")
        st.info("This clustering analysis groups projects by their characteristics to identify common 'archetypes.' Understanding these can reveal systemic challenges.", icon="🧬")

        col1, col2 = st.columns([1, 2])
        with col1:
            n_clusters = st.slider("Number of Archetypes to Identify", 2, 5, 3)
            x_axis = st.selectbox("X-Axis", ['budget_usd', 'risk_score', 'complexity', 'team_size', 'strategic_value'], 0)
            y_axis = st.selectbox("Y-Axis", ['risk_score', 'budget_usd', 'complexity', 'team_size', 'strategic_value'], 1)
        
        clustered_df = get_project_clusters(proj_df, n_clusters)
        
        with col2:
            if clustered_df is not None:
                fig_cluster = create_project_cluster_plot(clustered_df, x_axis, y_axis)
                st.plotly_chart(fig_cluster, use_container_width=True)
            else:
                st.warning("Could not generate clusters. Insufficient project data.")

        if clustered_df is not None and 'cluster' in clustered_df.columns:
            for cluster_name in sorted(clustered_df['cluster'].unique()):
                with st.expander(f"Analyze {cluster_name}"):
                    cluster_data = clustered_df[clustered_df['cluster'] == cluster_name]
                    st.dataframe(cluster_data[['name', 'project_type', 'health_status', 'risk_score', 'budget_usd', 'complexity']], hide_index=True)
