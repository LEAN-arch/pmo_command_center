# pmo_command_center/dashboards/pmo_methodology.py
import streamlit as st
import pandas as pd
from utils.pmo_session_state_manager import PMOSessionStateManager
from utils.plot_utils import create_gate_variance_plot

def render_methodology_dashboard(ssm: PMOSessionStateManager):
    st.header("PMO Process & Methodology Dashboard")
    st.caption("This dashboard analyzes the effectiveness and adherence to the deployed project management methodology, identifying trends to improve PMO maturity.")

    gate_data = ssm.get_data("phase_gate_data")
    projects = ssm.get_data("projects")
    if not gate_data or not projects:
        st.warning("No phase-gate or project data available for analysis.")
        return

    gate_df = pd.DataFrame(gate_data)
    proj_df = pd.DataFrame(projects)

    # --- Gate Adherence KPIs ---
    st.subheader("Phase-Gate Performance")
    completed_gates = gate_df.dropna(subset=['actual_date'])
    on_time_gates = completed_gates[pd.to_datetime(completed_gates['actual_date']) <= pd.to_datetime(completed_gates['planned_date'])]
    
    total_completed = len(completed_gates)
    total_on_time = len(on_time_gates)
    adherence_rate = (total_on_time / total_completed) * 100 if total_completed > 0 else 100
    avg_delay = completed_gates[pd.to_datetime(completed_gates['actual_date']) > pd.to_datetime(completed_gates['planned_date'])]['actual_date'].apply(pd.to_datetime) - completed_gates[pd.to_datetime(completed_gates['actual_date']) > pd.to_datetime(completed_gates['planned_date'])]['planned_date'].apply(pd.to_datetime)
    
    kpi_cols = st.columns(2)
    kpi_cols[0].metric("Gate Schedule Adherence", f"{adherence_rate:.1f}%", help="Percentage of completed phase-gates that were met on or before their planned date.")
    kpi_cols[1].metric("Average Delay for Late Gates", f"{avg_delay.mean().days if not avg_delay.empty else 0} Days", help="The average number of days delayed for all gates that missed their planned date.")

    st.info("""
    **Analysis:** Tracking gate adherence is crucial for process control. A low adherence rate or high average delay suggests systemic issues in planning, resource allocation, or risk management that need to be addressed to increase PMO maturity.
    """, icon="📈")

    fig_variance = create_gate_variance_plot(gate_df)
    st.plotly_chart(fig_variance, use_container_width=True)

    st.divider()

    # --- Project Cycle Time Analysis ---
    st.subheader("Project Cycle Time Analysis")
    completed_projects = proj_df[proj_df['health_status'] == "Completed"]
    
    if not completed_projects.empty:
        completed_projects['duration_days'] = (pd.to_datetime(completed_projects['end_date']) - pd.to_datetime(completed_projects['start_date'])).dt.days
        avg_cycle_time_lcm = completed_projects[completed_projects['project_type'] == "LCM"]['duration_days'].mean()
        avg_cycle_time_npd = completed_projects[completed_projects['project_type'] == "NPD"]['duration_days'].mean()
        
        cycle_cols = st.columns(2)
        cycle_cols[0].metric("Avg. LCM Project Cycle Time", f"{avg_cycle_time_lcm:.0f} Days" if pd.notna(avg_cycle_time_lcm) else "N/A")
        cycle_cols[1].metric("Avg. NPD Project Cycle Time", f"{avg_cycle_time_npd:.0f} Days" if pd.notna(avg_cycle_time_npd) else "N/A")

        st.info("""
        **Analysis:** Cycle time is a key indicator of PMO efficiency. Establishing a baseline and tracking this metric over time allows the Director to measure the impact of process improvements and demonstrate increasing organizational maturity.
        """, icon="⏱️")
    else:
        st.info("No completed projects available yet to calculate cycle times.")
        
