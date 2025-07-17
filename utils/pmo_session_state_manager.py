# pmo_command_center/utils/pmo_session_state_manager.py
"""
Manages the application's session state. This class now acts as an orchestration
engine, fetching data from connectors, running the automation/alerting engine,
applying ML predictions, and managing the "what-if" sandbox state.
"""
import logging
import pandas as pd
import streamlit as st
from typing import Any, Dict, List

# Import the new abstraction layers
from utils import data_connectors as dc
from utils import ml_models as ml

logger = logging.getLogger(__name__)

def _run_automation_engine(projects_df: pd.DataFrame, dhf_df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Simulates a proactive automation engine that generates alerts based on data.
    """
    alerts = []
    
    # 1. Automated Risk Alert
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
            
    # (Resource conflict alerts would be generated in the resource dashboard based on forecast)
    return alerts

def _load_and_process_data() -> Dict[str, Any]:
    """
    Main data loading and processing function. Fetches data from connectors,
    calculates metrics, trains models, applies predictions, and runs automation.
    """
    # 1. Fetch data from "live" sources using the connector layer
    projects = dc.get_projects_from_erp()
    dhf_documents = dc.get_dhf_from_qms()
    financials = dc.get_financials_from_erp()
    resources = dc.get_resources_from_hris()
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

    # Create DataFrames
    projects_df = pd.DataFrame(projects)
    dhf_df = pd.DataFrame(dhf_documents)
    
    # 2. Train ML Models
    schedule_risk_model, risk_features = ml.train_schedule_risk_model(projects_df)
    eac_prediction_model, eac_features = ml.train_eac_prediction_model(projects_df)

    # 3. Apply Predictions to Projects
    if not projects_df.empty:
        # Calculate standard EVM metrics first
        projects_df['cpi'] = projects_df.apply(lambda row: row['ev_usd'] / row['actuals_usd'] if row['actuals_usd'] > 0 else 0, axis=1)
        projects_df['spi'] = projects_df.apply(lambda row: row['ev_usd'] / row['pv_usd'] if row['pv_usd'] > 0 else 0, axis=1)
        
        # Apply ML predictions
        predictions = projects_df.apply(
            lambda row: ml.predict_project_schedule_risk(schedule_risk_model, risk_features, row),
            axis=1
        )
        projects_df['predicted_schedule_risk'] = [p[0] for p in predictions]
        projects_df['risk_contributions'] = [p[1] for p in predictions]
        
        projects_df['predicted_eac_usd'] = projects_df.apply(
            lambda row: ml.predict_eac(eac_prediction_model, eac_features, row),
            axis=1
        )
    
    # 4. Run Automation Engine to generate alerts
    alerts = _run_automation_engine(projects_df, dhf_df)

    return {
        "projects": projects_df.to_dict('records'),
        "strategic_goals": strategic_goals,
        "resources": resources,
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
    }


class SPMOSessionStateManager:
    _PMO_DATA_KEY = "pmo_intelligent_data_v11"
    
    def __init__(self):
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
        """Applies sandbox actions to a copy of the project data."""
        # Ensure we start with the original, unmodified project list
        original_projects = st.session_state[self._PMO_DATA_KEY]['projects']
        projects_df = pd.DataFrame(original_projects)
        
        for action in st.session_state.get('sandbox_actions', []):
            if action['type'] == 'cancel':
                projects_df = projects_df[projects_df['id'] != action['project_id']]
            elif action['type'] == 'accelerate':
                # Simulate budget increase
                idx = projects_df.index[projects_df['id'] == action['project_id']]
                if not idx.empty:
                    # Use .loc to ensure modification happens on the DataFrame
                    projects_df.loc[idx, 'budget_usd'] *= 1.20 # 20% budget increase
                    
        return projects_df.to_dict('records')

    def toggle_sandbox(self):
        current_mode = st.session_state.get('sandbox_mode', False)
        st.session_state['sandbox_mode'] = not current_mode
        if st.session_state['sandbox_mode'] is False:
            # Reset actions when exiting sandbox
            st.session_state['sandbox_actions'] = []
            
    def add_sandbox_action(self, action: Dict[str, Any]):
        if 'sandbox_actions' not in st.session_state:
            st.session_state['sandbox_actions'] = []
        st.session_state['sandbox_actions'].append(action)
