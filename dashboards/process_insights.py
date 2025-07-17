# pmo_command_center/dashboards/process_insights.py
"""
This module renders the Process Insights dashboard.

It provides a closed-loop view of PMO methodology adoption and effectiveness,
allowing the Director to track trends and generate evidence-based interventions
to improve PMO maturity.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.pmo_session_state_manager import SPMOSessionStateManager

def render_process_insights_dashboard(ssm: SPMOSessionStateManager):
    """Renders the dashboard for monitoring PMO process adherence and insights."""
    st.header("🔬 Process Insights & Methodology Adoption")
    st.caption("Track methodology adoption levels, analyze process improvement trends, and document retrospectives to drive PMO maturity.")

    # --- Data Loading ---
    adherence_data = ssm.get_data("process_adherence")

    if not adherence_data:
        st.warning("No process adherence data available.")
        return

    adherence_df = pd.DataFrame(adherence_data)

    st.subheader("Methodology Adherence Trends")
    st.info(
        "This chart tracks key process adherence metrics over time. An upward trend across these KPIs provides "
        "evidence of increasing PMO maturity and process discipline.",
        icon="📈"
    )
    
    if not adherence_df.empty:
        fig = px.line(
            adherence_df,
            x='quarter',
            y='value',
            color='metric',
            markers=True,
            title="PMO Process Adherence by Quarter",
            labels={
                "quarter": "Quarter",
                "value": "Adherence / Score (%)",
                "metric": "Adherence KPI"
            }
        )
        fig.update_layout(
            yaxis_range=[0,100],
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No adherence data to display.")
    
    st.divider()

    st.subheader("Improvement Initiatives & Retrospectives")
    st.info(
        "This section documents key process improvement initiatives and learnings from project retrospectives, creating a cycle of continuous improvement.",
        icon="🔄"
    )

    # This would be powered by a more formal knowledge management or continuous improvement system.
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Recent Improvement Initiatives")
        st.markdown("""
        - **Q2 Initiative:** Deployed standardized PowerPoint reporting template via the sPMO Command Center to reduce PM administrative time. **Status:** In Progress.
        - **Q1 Initiative:** Implemented a mandatory pre-gate checklist for DHF documents to improve Gate 3 readiness. **Status:** Completed.
        """)

    with col2:
        st.markdown("##### Key Retrospective Learnings (Last 90 Days)")
        st.markdown("""
        - **Project NPD-H01:** The LIS2-A2 interface was more complex than planned. *Lesson:* Involve technical architecture team earlier in feasibility for connectivity projects.
        - **Project LCM-001:** Scope creep was well-managed through a rigorous change control process. *Best Practice:* Continue strict adherence to the DCR approval process.
        """)
        
    st.divider()
    
    st.subheader("Communication Log")
    st.caption("This log tracks key Q&A and responses related to process and methodology, for example, during audits or town halls.")
    
    # Placeholder for a communication log feature
    comm_log_data = {
        "Date": [(date.today() - timedelta(days=20)).strftime('%Y-%m-%d'), (date.today() - timedelta(days=45)).strftime('%Y-%m-%d')],
        "Topic/Question": ["Query from internal audit regarding RAID log update frequency.", "Question from R&D leadership on resource allocation priority."],
        "Response Summary": ["Confirmed that the sPMO dashboard now tracks timely updates, with a target of 85% weekly adherence.", "Referred to the Strategic Alignment dashboard to show how resources are tied to top corporate goals."],
        "Audience": ["Internal QMS Audit Team", "R&D Town Hall"]
    }
    st.table(pd.DataFrame(comm_log_data))
