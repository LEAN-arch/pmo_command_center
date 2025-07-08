# pmo_command_center/dashboards/pmo_health_metrics.py
"""
This module renders the PMO Health & KPIs dashboard. It includes ML-based
clustering to identify project archetypes and uncover systemic insights.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from utils.pmo_session_state_manager import SPMOSessionStateManager
from utils.plot_utils import create_gate_variance_plot, create_project_cluster_plot

@st.cache_data
def get_project_clusters(_proj_df: pd.DataFrame, n_clusters: int):
    """Applies K-Means clustering to identify project archetypes."""
    features = ['budget_usd', 'risk_score', 'complexity', 'team_size']
    df_for_clustering = _proj_df[features].copy()
    
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df_for_clustering)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(scaled_features)
    
    _proj_df['cluster'] = [f"Archetype {i}" for i in kmeans.labels_]
    return _proj_df

def render_pmo_health_dashboard(ssm: SPMOSessionStateManager):
    """Renders the dashboard for analyzing PMO process maturity and effectiveness."""
    st.header("📈 PMO Health & KPIs")
    st.caption("This dashboard provides metrics on PMO process effectiveness, helping to measure and improve the maturity of the project management function.")

    projects = ssm.get_data("projects")
    if not projects:
        st.warning("No project data available for analysis.")
        return
        
    proj_df = pd.DataFrame(projects)

    # --- Trend Analysis Section ---
    st.subheader("Process Performance & Trend Analysis")
    
    tab1, tab2 = st.tabs(["**Gate Performance Analysis**", "**Project Cycle Time Analysis**"])

    with tab1:
        gate_data = ssm.get_data("phase_gate_data")
        gate_df = pd.DataFrame(gate_data) if gate_data else pd.DataFrame()
        st.info("**Definition:** Gate Schedule Variance measures the difference (in days) between the planned and actual completion of a phase-gate. **Interpretation:** Consistently negative (late) variance in a specific gate (e.g., 'Development') can indicate systemic issues like inaccurate planning, resource constraints, or unresolved technical risks in that phase.", icon="📈")
        fig_variance = create_gate_variance_plot(gate_df)
        st.plotly_chart(fig_variance, use_container_width=True)

    with tab2:
        completed_projects = proj_df[proj_df['final_outcome'].notna()]
        if not completed_projects.empty:
            completed_projects['duration_days'] = (pd.to_datetime(completed_projects['end_date']) - pd.to_datetime(completed_projects['start_date'])).dt.days
            fig_cycle_time = px.box(completed_projects, x='project_type', y='duration_days', points="all",
                                    title="Project Cycle Time by Type (Concept to Completion)",
                                    labels={'project_type': 'Project Type', 'duration_days': 'Total Duration (Days)'})
            st.plotly_chart(fig_cycle_time, use_container_width=True)
            st.info("**Definition:** Cycle Time measures the total duration of a project from start to completion. **Interpretation:** Tracking this metric over time allows the Director to measure the impact of process improvements. A decreasing trend indicates increasing PMO efficiency.", icon="⏱️")
        else:
            st.info("No completed projects are available yet to calculate historical cycle times.")

    st.divider()

    # --- ML-Powered Archetype Analysis ---
    st.subheader("🧠 AI-Powered Project Archetype Analysis")
    st.info("This clustering analysis groups projects by their characteristics (e.g., budget, risk, complexity) to identify common 'archetypes.' Understanding these archetypes can reveal systemic challenges, such as why 'Large, Complex, NPD' projects consistently face similar issues.", icon="🧬")

    col1, col2 = st.columns([1,2])
    with col1:
        n_clusters = st.slider("Number of Archetypes (Clusters) to Identify", min_value=2, max_value=5, value=3)
        x_axis = st.selectbox("X-Axis for Visualization", options=['budget_usd', 'risk_score', 'complexity', 'team_size', 'strategic_value'], index=0)
        y_axis = st.selectbox("Y-Axis for Visualization", options=['risk_score', 'budget_usd', 'complexity', 'team_size', 'strategic_value'], index=1)
    
    clustered_df = get_project_clusters(proj_df, n_clusters)

    with col2:
        fig_cluster = create_project_cluster_plot(clustered_df, x_axis, y_axis)
        st.plotly_chart(fig_cluster, use_container_width=True)

    st.subheader("Analysis of Project Archetypes")
    for i in range(n_clusters):
        archetype_name = f"Archetype {i}"
        with st.container(border=True):
            st.markdown(f"#### {archetype_name}")
            cluster_data = clustered_df[clustered_df['cluster'] == archetype_name]
            avg_risk = cluster_data['risk_score'].mean()
            avg_budget = cluster_data['budget_usd'].mean()
            
            completed_cluster = cluster_data[cluster_data['final_outcome'].notna()]
            if not completed_cluster.empty:
                on_time_rate = (len(completed_cluster[completed_cluster['final_outcome'] == 'On-Time']) / len(completed_cluster)) * 100
                st.write(f"This archetype consists of **{len(cluster_data)} projects** with an average risk score of **{avg_risk:.1f}** and budget of **${avg_budget:,.0f}**. Historically, projects of this type have had an on-time completion rate of **{on_time_rate:.1f}%**.")
            else:
                st.write(f"This archetype consists of **{len(cluster_data)} active projects** with an average risk score of **{avg_risk:.1f}** and budget of **${avg_budget:,.0f}**. No historical data is available for this type yet.")
            
            with st.expander(f"View Projects in {archetype_name}"):
                st.dataframe(cluster_data[['name', 'project_type', 'health_status', 'risk_score', 'budget_usd', 'complexity']], hide_index=True)
