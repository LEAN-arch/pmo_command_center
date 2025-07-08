# pmo_command_center/app.py
import logging
import streamlit as st
import os
import sys

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
try:
    from utils.pmo_session_state_manager import PMOSessionStateManager
    from dashboards.portfolio_health import render_portfolio_health_dashboard
    # Assuming these dashboards will be created, we can import them here
    # from dashboards.financial_overview import render_financial_dashboard
    from dashboards.resource_management import render_resource_dashboard
    from dashboards.risk_and_compliance import render_risk_dashboard
    # from dashboards.strategy_and_pipeline import render_strategy_dashboard
except ImportError as e:
    st.error(f"Fatal Error: A required module could not be imported: {e}.")
    logging.critical(f"Fatal module import error: {e}", exc_info=True)
    st.stop()

# --- Page Config & Logging ---
st.set_page_config(layout="wide", page_title="Werfen PMO Command Center", page_icon="📊")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', force=True)

def main():
    """Main function to run the Streamlit application."""
    st.title("📊 Werfen Autoimmunity - PMO Command Center")
    st.caption("Strategic Portfolio Management Dashboard for Executive Oversight")

    try:
        ssm = PMOSessionStateManager()
    except Exception as e:
        st.error(f"Fatal Error: Could not initialize data model: {e}")
        logging.critical(f"Failed to instantiate PMOSessionStateManager: {e}", exc_info=True)
        st.stop()

    # --- Sidebar Navigation ---
    st.sidebar.image("https://www.werfen.com/corp/werfen-web/themes/werfen/images/logo-werfen-blue.svg", width=200)
    st.sidebar.title("Workspaces")
    app_mode = st.sidebar.radio(
        "Navigation",
        [
            "Portfolio Health",
            "Resource Management",
            "Risk & QMS Compliance",
            "Financial Overview",
            "Strategy & Pipeline",
        ],
        captions=[
            "Executive KPIs & Project Landscape",
            "Cross-Functional Allocation & Utilization",
            "Portfolio Risks and QMS Health Metrics",
            "Budget, Actuals, and Variance Analysis",
            "Future Initiatives and Strategic Alignment"
        ]
    )

    # --- Main Panel Rendering ---
    if app_mode == "Portfolio Health":
        render_portfolio_health_dashboard(ssm)
    elif app_mode == "Resource Management":
        render_resource_dashboard(ssm)
    elif app_mode == "Risk & QMS Compliance":
        render_risk_dashboard(ssm)
    # Add other elif blocks as they are built
    # elif app_mode == "Financial Overview":
    #     render_financial_dashboard(ssm)
    # etc...
    else:
        st.info(f"The '{app_mode}' dashboard is under construction.")


if __name__ == "__main__":
    main()
