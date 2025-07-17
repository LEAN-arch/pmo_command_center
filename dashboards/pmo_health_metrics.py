# pmo_command_center/dashboards/pmo_health_metrics.py
"""
This module renders the PMO Health & Maturity dashboard. It provides metrics on
PMO process effectiveness and uses ML-based clustering to identify project
archetypes, uncovering systemic insights to drive continuous improvement.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.pmo_session_state_manager import SPMOSessionStateManager
from utils.plot_utils import create_gate_variance_plot, create_project_cluster_plot
from utils.ml_models import get_project_clusters # Uses the centralized model

def render_pmo_health_dashboard(ssm: SPMOSessionStateManager):
    """Renders the dashboard for analyzing PMO process maturity and effectiveness."""
    st.header("📈 PMO Health & Maturity")
    st.caption("Measure and improve the effectiveness of the PMO function with metrics on process performance and AI-powered archetype analysis.")

    projects = ssm.get_data("projects")
    gate_data = ssm.get_data("phase_gate_data")

    if not projects:
        st.warning("No project data available for analysis.")
        return

    proj_df = pd.DataFrame(projects)
    gate_df = pd.DataFrame(gate_data) if gate_data else pd.DataFrame()

    # --- Process Performance & Trend Analysis ---
    st.subheader("Process Performance & Trend Analysis")

    tab1, tab2 = st.tabs(["**Gate Performance Analysis**", "**Project Cycle Time Analysis**"])

    with tab1:
        st.info(
            "**Definition:** Gate Schedule Variance measures the difference (in days) between the planned and actual completion of a phase-gate. "
            "**Interpretation:** Consistently negative (late) variance in a specific gate (e.g., 'Development') can indicate systemic issues "
            "like inaccurate planning, resource constraints, or unresolved technical risks in that phase.",
            icon="📈"
        )
        fig_variance = create_gate_variance_plot(gate_df)
        st.plotly_chart(fig_variance, use_container_width=True)

    with tab2:
        st.info(
            "**Definition:** Cycle Time measures the total duration of a project from start to completion. "
            "**Interpretation:** Tracking this metric over time allows the Director to measure the impact of process improvements. "
            "A decreasing trend indicates increasing PMO efficiency.",
            icon="⏱️"
        )
        completed_projects = proj_df[proj_df['final_outcome'].notna()].copy()
        if not completed_projects.empty:
            completed_projects['duration_days'] = (pd.to_datetime(completed_projects['end_date']) - pd.to_datetime(completed_projects['start_date'])).dt.days
            fig_cycle_time = px.box(
                completed_projects, x='project_type', y='duration_days', points="all",
                title="Project Cycle Time by Type (Concept to Completion)",
                labels={'project_type': 'Project Type', 'duration_days': 'Total Duration (Days)'}
            )
            st.plotly_chart(fig_cycle_time, use_container_width=True)
        else:
            st.info("No completed projects are available yet to calculate historical cycle times.")

    st.divider()

    # --- ML-Powered Archetype Analysis ---
    st.subheader("🧠 AI-Powered Project Archetype Analysis")
    st.info(
        "This clustering analysis groups projects by their characteristics (e.g., budget, risk, complexity) to identify common 'archetypes.' "
        "Understanding these archetypes can reveal systemic challenges, such as why 'Large, Complex, NPD' projects consistently face similar issues.",
        icon="🧬"
    )

    col1, col2 = st.columns([1, 2])
    with col1:
        n_clusters = st.slider("Number of Archetypes (Clusters) to Identify", min_value=2, max_value=5, value=3)
        x_axis = st.selectbox("X-Axis for Visualization", options=['budget_usd', 'risk_score', 'complexity', 'team_size', 'strategic_value'], index=0)
        y_axis = st.selectbox("Y-Axis for Visualization", options=['risk_score', 'budget_usd', 'complexity', 'team_size', 'strategic_value'], index=1)

    clustered_df = get_project_clusters(proj_df, n_clusters)

    with col2:
        if clustered_df is not None and not clustered_df.empty:
            fig_cluster = create_project_cluster_plot(clustered_df, x_axis, y_axis)
            st.plotly_chart(fig_cluster, use_container_width=True)
        else:
            st.warning("Could not generate project clusters. Not enough data.")

    st.subheader("Analysis of Project Archetypes")
    if clustered_df is not None and 'cluster' in clustered_df.columns:
        for cluster_name in sorted(clustered_df['cluster'].unique()):
            with st.container(border=True):
                st.markdown(f"#### {cluster_name}")
                cluster_data = clustered_df[clustered_df['cluster'] == cluster_name]
                
                avg_risk = cluster_data['risk_score'].mean()
                avg_budget = cluster_data['budget_usd'].mean()
                avg_complexity = cluster_data['complexity'].mean()
                common_type = cluster_data['project_type'].mode()[0] if not cluster_data.empty else 'N/A'

                description = f"These are typically **{common_type}** projects with "
                if avg_budget > 3_000_000: description += "**large budgets**"
                else: description += "**moderate budgets**"
                description += f" (avg ${avg_budget:,.0f}), "
                if avg_complexity > 3.5: description += "**high complexity**"
                else: description += "**low-to-moderate complexity**"
                description += f" (avg {avg_complexity:.1f}), and "
                if avg_risk > 5: description += "**high inherent risk**"
                else: description += "**low-to-moderate risk**"
                description += f" (avg {avg_risk:.1f})."

                st.write(description)
                
                with st.expander(f"View {len(cluster_data)} Projects in {cluster_name}"):
                    st.dataframe(
                        cluster_data[['name', 'project_type', 'health_status', 'risk_score', 'budget_usd', 'complexity']],
                        hide_index=True,
                        use_container_width=True
                    )
