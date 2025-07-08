# pmo_command_center/app.py
"""
Main application entry point for the Autoimmunity Division's sPMO Command Center.

This Streamlit application orchestrates a suite of modular dashboards designed to
provide comprehensive, strategic oversight of the entire project portfolio. It
serves as the central hub for the PMO Director to monitor performance, manage
resources, oversee risk and compliance, and align project execution with
corporate strategy.
"""
import logging
import streamlit as st
import os
import sys
import pandas as pd

# --- Robust Path Correction ---
# This ensures that the application can find its own modules when run as a script.
try:
    current_file_path = os.path.abspath(__file__)
    project_root = os.path.dirname(current_file_path)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
except Exception as e:
    st.warning(f"Could not adjust system path. Module imports may fail. Error: {e}")
# --- End of Path Correction Block ---

# --- Local Application Imports ---
# Import all dashboard modules. The file names are now valid Python identifiers.
try:
    from utils.pmo_session_state_manager import SPMOSessionStateManager
    from dashboards.portfolio_dashboard import render_portfolio_dashboard
    from dashboards.project_deep_dive import render_project_deep_dive
    from dashboards.financial_overview import render_financial_dashboard
    from dashboards.risk_compliance import render_risk_dashboard
    from dashboards.resource_allocation import render_resource_dashboard
    from dashboards.strategic_planning import render_strategy_dashboard
    from dashboards.pmo_health_metrics import render_pmo_health_dashboard
    from dashboards.design_control_interface import render_design_control_dashboard
    from dashboards.collaboration_tracker import render_collaboration_dashboard
except ImportError as e:
    st.error(f"Fatal Error: A required dashboard module could not be imported: {e}. Please check the file names and paths in the 'dashboards' directory.")
    logging.critical(f"Fatal module import error: {e}", exc_info=True)
    st.stop()

# --- Page Config & Logging ---
st.set_page_config(layout="wide", page_title="sPMO Command Center", page_icon="🎯")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', force=True)


# --- Main Application Logic ---
def main():
    """Main function to configure and run the Streamlit application."""
    st.title("🎯 Autoimmunity Division - sPMO Command Center")
    st.caption("A Strategic Portfolio Management Dashboard for Executive Oversight")

    try:
        ssm = SPMOSessionStateManager()
    except Exception as e:
        st.error(f"Fatal Error: Could not initialize the application's data model: {e}")
        logging.critical(f"Failed to instantiate SPMOSessionStateManager: {e}", exc_info=True)
        st.stop()

    # --- Sidebar Navigation ---
    # The navigation order is controlled here, providing a logical flow for the user.
    st.sidebar.image("https://www.werfen.com/corp/werfen-web/themes/werfen/images/logo-werfen-blue.svg", width=200)
    st.sidebar.title("sPMO Workspaces")

    # Define the dashboards and their corresponding render functions and captions
    dashboards = {
        "Portfolio Dashboard": {
            "function": render_portfolio_dashboard,
            "caption": "Executive KPIs & Project Landscape"
        },
        "Financial Overview": {
            "function": render_financial_dashboard,
            "caption": "Budget, Actuals, and Variance Analysis"
        },
        "Strategic Planning": {
            "function": render_strategy_dashboard,
            "caption": "Future Initiatives and Strategic Alignment"
        },
        "Resource Allocation": {
            "function": render_resource_dashboard,
            "caption": "Cross-Functional Allocation & Utilization"
        },
        "Project Deep Dive": {
            "function": render_project_deep_dive,
            "caption": "Drill-down into individual project status"
        },
        "Risk & QMS Compliance": {
            "function": render_risk_dashboard,
            "caption": "Portfolio Risks and QMS Health Metrics"
        },
        "PMO Health & KPIs": {
            "function": render_pmo_health_dashboard,
            "caption": "Measure PMO process effectiveness"
        },
        "Design Control Interface": {
            "function": render_design_control_dashboard,
            "caption": "Monitor QMS & Design Control compliance"
        },
        "Cross-Entity Collaboration": {
            "function": render_collaboration_dashboard,
            "caption": "Track inter-site initiatives & best practices"
        },
    }

    # Create the radio button for navigation
    selection = st.sidebar.radio(
        "Navigation",
        list(dashboards.keys()),
        captions=[d["caption"] for d in dashboards.values()]
    )

    # --- Main Panel Rendering ---
    # Call the selected dashboard's render function
    page_to_render = dashboards[selection]["function"]
    page_to_render(ssm)

    # --- Admin & Settings Footer (Placeholder) ---
    with st.sidebar.expander("⚙️ Admin & Settings"):
        st.info("This area is for administrative functions.")
        if st.button("Force Data Refresh"):
            # A more robust implementation would clear specific session state keys
            st.session_state.clear()
            st.rerun()
            
        st.download_button(
            label="Download Portfolio Summary (CSV)",
            data=pd.DataFrame(ssm.get_data("projects")).to_csv(index=False).encode('utf-8'),
            file_name="portfolio_summary.csv",
            mime="text/csv"
        )
        st.caption("Audit trail logs would be accessible here for compliance with 21 CFR Part 11.")


if __name__ == "__main__":
    main()
