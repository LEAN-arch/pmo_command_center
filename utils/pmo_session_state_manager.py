"""
Manages the application's session state. This class now acts as an orchestration
engine, fetching data from connectors, running the automation/alerting engine,
applying ML predictions, and managing the "what-if" sandbox state. It is the
central nervous system of the sPMO Command Center.
"""
import logging
import pandas as pd
import streamlit as st
from typing import Any, Dict, List

# Import the abstraction layers for data and machine learning
from utils import data_connectors as dc
from utils import ml_models as ml

logger = logging.getLogger(__name__)

def _run_automation_engine(projects_df: pd.DataFrame, dhf_df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Simulates a proactive automation engine that generates alerts based on data.
    """
    alerts = []
    
    # 1. Automated Predictive Risk Alert
    if 'predicted_schedule_risk' in projects_df.columns:
        high_risk_projects = projects_df[projects_df['predicted_schedule_risk'] > 0.7]
        for _, project in high_risk_projects.iterrows():
            alerts.append({
                "type": "High Predictive Risk",
                "message": f"Project '{project['name']}' has a {project['predicted_schedule_risk']:.0%} predicted risk of delay. Immediate review of risk drivers is recommended.",
                "severity": "error"
            })
        
    # 2. Automated Gate Review Workflow Alert
    dev_projects = projects_df[projects_df['phase'] == 'Development']
    for _, project in dev_projects.iterrows():
        if not dhf_df.empty:
            required_docs = dhf_df[(dhf_df['project_id'] == project['id']) & (dhf_df['gate'] == 'V&V')]
            if not required_docs.empty and all(required_docs['status'] == 'Approved'):
                alerts.append({
                    "type": "Gate Readiness",
                    "message": f"All required DHF documents for project '{project['name']}' are approved. Ready to schedule the V&V Gate Review.",
                    "severity": "success"
                })
    
    # 3. Automated Cost Overrun Alert
    if 'predicted_eac_usd' in projects_df.columns:
        overrun_projects = projects_df[projects_df['predicted_eac_usd'] > projects_df['budget_usd'] * 1.1] # >10% overrun
        for _, project in overrun_projects.iterrows():
             alerts.append({
                "type": "Cost Overrun Predicted",
                "message": f"Project '{project['name']}' is predicted to exceed its budget by more than 10%. Review financial controls.",
                "severity": "error"
            })

    return alerts

def _load_and_process_data() -> Dict[str, Any]:
    """
    Main data loading and processing function. Fetches data from all connectors,
    calculates metrics, trains models, applies predictions, and runs automation.
    This function creates the complete, intelligent data model for the application.
    """
    # 1. Fetch data from all "live" sources using the connector layer
    # (Code for fetching data from dc... functions remains the same)
    projects = dc.get_projects_from_erp()
    dhf_documents = dc.get_dhf_from_qms()
    financials = dc.get_financials_from_erp()
    enterprise_resources = dc.get_enterprise_resources_from_hris()
    allocations = dc.get_allocations_from_planning_tool()
    milestones = dc.get_milestones()
    raid_logs = dc.get_raid_logs()
    qms_kpis = dc.get_qms_kpis()
    on_market_products = dc.get_on_market_products_from_qms()
    traceability_matrix = dc.get_traceability_from_alm()
    phase_gate_data = dc.get_phase_gate_data()
    resource_demand_history = dc.get_resource_demand_history()
    change_controls = dc.get_change_controls()
    collaborations = dc.get_collaborations()
    strategic_goals = dc.get_strategic_goals()
    pmo_team = dc.get_pmo_team_from_hris()
    pmo_department_budget = dc.get_pmo_budget_from_finance()
    process_adherence = dc.get_process_adherence_from_alm()
    
    projects_df = pd.DataFrame(projects)
    dhf_df = pd.DataFrame(dhf_documents)
    
    # 2. Train ML Models on historical data
    schedule_risk_model, risk_features = ml.train_schedule_risk_model(projects_df)
    eac_prediction_model, eac_features = ml.train_eac_prediction_model(projects_df)

    # 3. Enrich Live Data: Apply Calculations and Predictions to Projects
    if not projects_df.empty:
        projects_df['start_date'] = pd.to_datetime(projects_df['start_date'])
        projects_df['end_date'] = pd.to_datetime(projects_df['end_date'])
        projects_df['cpi'] = projects_df.apply(lambda row: row['ev_usd'] / row['actuals_usd'] if row['actuals_usd'] > 0 else 1.0, axis=1)
        projects_df['spi'] = projects_df.apply(lambda row: row['ev_usd'] / row['pv_usd'] if row['pv_usd'] > 0 else 1.0, axis=1)
        
        # --- FIX: Replaced 'result_type=expand' with explicit column assignment for robustness ---
        # This prevents the AttributeError by guaranteeing column data types.
        
        # Step A: Apply the function and get a Series of tuples
        prediction_results = projects_df.apply(
            lambda row: ml.predict_project_schedule_risk(schedule_risk_model, risk_features, row),
            axis=1
        ).tolist()

        # Step B: Unzip the list of tuples into two separate lists
        risk_probabilities, risk_contributions_list = zip(*prediction_results)

        # Step C: Assign the clean lists to the new DataFrame columns
        projects_df['predicted_schedule_risk'] = risk_probabilities
        projects_df['risk_contributions'] = risk_contributions_list
        # --- END FIX ---
        
        projects_df['predicted_eac_usd'] = projects_df.apply(
            lambda row: ml.predict_eac(eac_prediction_model, eac_features, row),
            axis=1
        )
    
    # 4. Run Automation Engine to generate high-priority alerts
    alerts = _run_automation_engine(projects_df, dhf_df)

    # 5. Package all data into a single dictionary for session state
    return {
        "projects": projects_df.to_dict('records'),
        "strategic_goals": strategic_goals,
        "enterprise_resources": enterprise_resources,
        "allocations": allocations,
        "milestones": milestones,
        "raid_logs": raid_logs,
        "qms_kpis": qms_kpis,
        "financials": financials,
        "on_market_products": on_market_products,
        "dhf_documents": dhf_df.to_dict('records'),
        "traceability_matrix": traceability_matrix,
        "phase_gate_data": phase_gate_data,
        "resource_demand_history": resource_demand_history,
        "change_controls": change_controls,
        "collaborations": collaborations,
        "alerts": alerts,
        "pmo_team": pmo_team,
        "pmo_department_budget": pmo_department_budget,
        "process_adherence": process_adherence,
    }

class SPMOSessionStateManager:
    _PMO_DATA_KEY = "pmo_intelligent_data_v13" # Version updated to reflect bug fix
    
    def __init__(self):
        """Initializes the session state, loading and processing all data if not already present."""
        if self._PMO_DATA_KEY not in st.session_state:
            logger.info(f"Initializing session state with intelligent sPMO data model.")
            with st.spinner("Connecting to enterprise systems and running predictive models..."):
                st.session_state[self._PMO_DATA_KEY] = _load_and_process_data()
                st.session_state['sandbox_mode'] = False
                st.session_state['sandbox_actions'] = []

    def get_data(self, key: str, default: Any = None) -> Any:
        """
        Safely retrieves data from the session state model.
        If sandbox mode is active, it returns the modified sandbox data for projects.
        """
        if key == 'projects' and st.session_state.get('sandbox_mode', False):
            return self._get_sandboxed_projects()
            
        return st.session_state.get(self._PMO_DATA_KEY, {}).get(key, default if default is not None else [])

    def _get_sandboxed_projects(self) -> List[Dict[str, Any]]:
        """Applies sandbox actions to a copy of the project data for 'what-if' analysis."""
        original_projects = st.session_state[self._PMO_DATA_KEY]['projects']
        projects_df = pd.DataFrame(original_projects).copy()
        
        for action in st.session_state.get('sandbox_actions', []):
            idx = projects_df.index[projects_df['id'] == action['project_id']]
            if not idx.empty:
                if action['type'] == 'cancel':
                    projects_df = projects_df.drop(idx)
                elif action['type'] == 'accelerate':
                    projects_df.loc[idx, 'budget_usd'] *= 1.20 
                    
        return projects_df.to_dict('records')

    def toggle_sandbox(self):
        """Toggles the sandbox mode on or off."""
        current_mode = st.session_state.get('sandbox_mode', False)
        st.session_state['sandbox_mode'] = not current_mode
        if st.session_state['sandbox_mode'] is False:
            st.session_state['sandbox_actions'] = []
            
    def add_sandbox_action(self, action: Dict[str, Any]):
        """Adds a simulation action to the list for the current sandbox session."""
        if 'sandbox_actions' not in st.session_state:
            st.session_state['sandbox_actions'] = []
        st.session_state['sandbox_actions'].append(action)
