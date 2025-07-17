# pmo_command_center/app.py
"""
Main application entry point for the Werfen Autoimmunity Division's sPMO Command Center.

This Streamlit application orchestrates a suite of modular dashboards designed to
provide comprehensive, strategic oversight of the entire project portfolio. It
serves as the central hub for the PMO Director to monitor performance, manage
resources, oversee risk and compliance, and align project execution with
corporate strategy, enhanced with predictive machine learning capabilities.
"""
import logging
import os
import sys
import pandas as pd
import streamlit as st

# --- Robust Path Correction ---
try:
    # This attempts to add the project root to the path for robust module imports.
    current_file_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_file_path))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
except Exception as e:
    # Fallback for environments where __file__ is not defined
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())
    logging.warning(f"Could not reliably determine project root. Using current working directory. Error: {e}")

# --- Local Application Imports ---
try:
    from utils.pmo_session_state_manager import SPMOSessionStateManager
    from dashboards.portfolio_dashboard import render_portfolio_dashboard
    from dashboards.project_deep_dive import render_project_deep_dive
    from dashboards.financial_overview import render_financial_dashboard
    from dashboards.risk_compliance import render_risk_dashboard
    from dashboards.resource_allocation import render_resource_dashboard
    from dashboards.strategic_planning import render_strategy_dashboard
    from dashboards.pmo_health_metrics import render_pmo_health_dashboard
    from dashboards.plm_cockpit import render_plm_cockpit
    from dashboards.governance_reporting import render_governance_dashboard
    from dashboards.collaboration_tracker import render_collaboration_dashboard
except ImportError as e:
    st.error(f"Fatal Error: A required dashboard module could not be imported: {e}. Please check file names and paths.")
    logging.critical(f"Fatal module import error: {e}", exc_info=True)
    st.stop()

# --- Page Config & Logging ---
st.set_page_config(layout="wide", page_title="Werfen sPMO Command Center", page_icon="🎯")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', force=True)


def main():
    """Main function to configure and run the Streamlit application."""
    st.title("🎯 Werfen Autoimmunity - sPMO Command Center")

    try:
        ssm = SPMOSessionStateManager()
    except Exception as e:
        st.error(f"Fatal Error: Could not initialize the application's data model: {e}")
        logging.critical(f"Failed to instantiate SPMOSessionStateManager: {e}", exc_info=True)
        st.stop()
    
    # --- Automated Alerts Display ---
    alerts = ssm.get_data("alerts")
    if alerts:
        st.subheader("Actionable Alerts")
        for alert in alerts:
            if alert['severity'] == 'error':
                st.error(f"**{alert['type']}:** {alert['message']}", icon="🚨")
            elif alert['severity'] == 'success':
                st.success(f"**{alert['type']}:** {alert['message']}", icon="✅")

    # --- Sidebar Navigation (Reorganized for sPMO Workflow) ---
    st.sidebar.image("https://www.werfen.com/corp/werfen-web/themes/werfen/images/logo-werfen-blue.svg", width=200)
    st.sidebar.title("sPMO Workspaces")

    dashboards = {
        "Executive Portfolio": {
            "function": render_portfolio_dashboard,
            "caption": "Executive KPIs & Project Landscape",
            "icon": "📊"
        },
        "PLM & Design Control Cockpit": {
            "function": render_plm_cockpit,
            "caption": "R&D Pipeline, DHF, and On-Market Products",
            "icon": "🧬"
        },
        "Financial & Capacity Planning": {
            "function": render_financial_dashboard,
            "caption": "Budget, EVM, and Resource Forecasting",
            "icon": "💰"
        },
        "Strategic Alignment": {
            "function": render_strategy_dashboard,
            "caption": "Goal Alignment and Future Initiatives",
            "icon": "🎯"
        },
        "Governance & Reporting": {
            "function": render_governance_dashboard,
            "caption": "RAID Logs and Standardized Reporting",
            "icon": "⚖️"
        },
        "Project Deep Dive": {
            "function": render_project_deep_dive,
            "caption": "Drill-down with Predictive Risk Analysis",
            "icon": "🔎"
        },
        "Resource Allocation": {
            "function": render_resource_dashboard,
            "caption": "Cross-Functional Allocation & Utilization",
            "icon": "👥"
        },
        "Risk & QMS Compliance": {
            "function": render_risk_dashboard,
            "caption": "Portfolio Risks and QMS Health Metrics",
            "icon": "🛡️"
        },
        "PMO Health & Maturity": {
            "function": render_pmo_health_dashboard,
            "caption": "Measure PMO Process Effectiveness",
            "icon": "📈"
        },
        "Cross-Entity Collaboration": {
            "function": render_collaboration_dashboard,
            "caption": "Track Inter-site Initiatives",
            "icon": "🌐"
        },
    }

    selection_options = [f"{d['icon']} {name}" for name, d in dashboards.items()]
    selection = st.sidebar.radio(
        "Navigation",
        selection_options,
        captions=[d["caption"] for d in dashboards.values()]
    )

    # --- Main Panel Rendering ---
    selected_name = selection.split(" ", 1)[1]
    page_to_render = dashboards[selected_name]["function"]
    page_to_render(ssm)

    # --- Admin & Settings Footer ---
    with st.sidebar.expander("⚙️ Admin & Settings"):
        st.info("This area is for administrative functions and data management.")
        if st.button("Force Data Refresh", use_container_width=True, help="Clears all cached data and re-runs the simulation from scratch."):
            st.session_state.clear()
            st.rerun()

        projects_df = pd.DataFrame(ssm.get_data("projects"))
        if not projects_df.empty:
            csv_data = projects_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Portfolio Summary (CSV)",
                data=csv_data,
                file_name="portfolio_summary.csv",
                mime="text/csv",
                use_container_width=True
            )
        st.caption("Audit trail logs would be accessible here for compliance with 21 CFR Part 11.")

if __name__ == "__main__":
    main()
