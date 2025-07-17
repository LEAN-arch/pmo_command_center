"""
Manages the application's session state. This class now acts as an orchestration
and transaction engine, fetching data, running automation, applying ML predictions,
managing a deep "what-if" sandbox, and logging a compliance audit trail.
It is the central nervous system of the sPMO Command Center.
"""
import logging
import pandas as pd
import streamlit as st
from typing import Any, Dict, List
import copy
from datetime import datetime

# Import the abstraction layers
from utils import data_connectors as dc
from utils import ml_models as ml

logger = logging.getLogger(__name__)

def _run_automation_engine(projects_df: pd.DataFrame, dhf_df: pd.DataFrame) -> List[Dict[str, Any]]:
    # (This function's internal logic is unchanged and correct)
    alerts = []
    if 'predicted_schedule_risk' in projects_df.columns:
        high_risk_projects = projects_df[projects_df['predicted_schedule_risk'] > 0.7]
        for _, project in high_risk_projects.iterrows():
            alerts.append({"type": "High Predictive Risk", "message": f"Project '{project['name']}' has a {project['predicted_schedule_risk']:.0%} predicted risk of delay. Immediate review recommended.", "severity": "error"})
    dev_projects = projects_df[projects_df['phase'] == 'Development']
    for _, project in dev_projects.iterrows():
        if not dhf_df.empty:
            required_docs = dhf_df[(dhf_df['project_id'] == project['id']) & (dhf_df['gate'] == 'V&V')]
            if not required_docs.empty and all(required_docs['status'] == 'Approved'):
                alerts.append({"type": "Gate Readiness", "message": f"All DHF documents for '{project['name']}' are approved. Ready for V&V Gate Review.", "severity": "success"})
    if 'predicted_eac_usd' in projects_df.columns:
        overrun_projects = projects_df[projects_df['predicted_eac_usd'] > projects_df['budget_usd'] * 1.1]
        for _, project in overrun_projects.iterrows():
             alerts.append({"type": "Cost Overrun Predicted", "message": f"Project '{project['name']}' is predicted to exceed budget by >10%. Review financial controls.", "severity": "error"})
    return alerts


def _load_and_process_data() -> Dict[str, Any]:
    # (This function's internal logic is unchanged and correct)
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
    
    schedule_risk_model, risk_features = ml.train_schedule_risk_model(projects_df)
    eac_prediction_model, eac_features = ml.train_eac_prediction_model(projects_df)

    if not projects_df.empty:
        projects_df['start_date'] = pd.to_datetime(projects_df['start_date'])
        projects_df['end_date'] = pd.to_datetime(projects_df['end_date'])
        projects_df['cpi'] = projects_df.apply(lambda row: row['ev_usd'] / row['actuals_usd'] if row['actuals_usd'] > 0 else 1.0, axis=1)
        projects_df['spi'] = projects_df.apply(lambda row: row['ev_usd'] / row['pv_usd'] if row['pv_usd'] > 0 else 1.0, axis=1)
        
        risk_probabilities = []; risk_contributions_list = []
        for index, row in projects_df.iterrows():
            prob, contrib_df = ml.predict_project_schedule_risk(schedule_risk_model, risk_features, row)
            risk_probabilities.append(prob); risk_contributions_list.append(contrib_df)
        projects_df['predicted_schedule_risk'] = risk_probabilities
        projects_df['risk_contributions'] = risk_contributions_list
        
        projects_df['predicted_eac_usd'] = projects_df.apply(lambda row: ml.predict_eac(eac_prediction_model, eac_features, row), axis=1)
    
    alerts = _run_automation_engine(projects_df, dhf_df)

    return {
        "projects": projects_df.to_dict('records'), "strategic_goals": strategic_goals,
        "enterprise_resources": enterprise_resources, "allocations": allocations,
        "milestones": milestones, "raid_logs": raid_logs, "qms_kpis": qms_kpis,
        "financials": financials, "on_market_products": on_market_products,
        "dhf_documents": dhf_df.to_dict('records'), "traceability_matrix": traceability_matrix,
        "phase_gate_data": phase_gate_data, "resource_demand_history": resource_demand_history,
        "change_controls": change_controls, "collaborations": collaborations, "alerts": alerts,
        "pmo_team": pmo_team, "pmo_department_budget": pmo_department_budget,
        "process_adherence": process_adherence,
    }

class SPMOSessionStateManager:
    _PMO_LIVE_DATA_KEY = "pmo_live_data_v15"
    _PMO_SANDBOX_KEY = "pmo_sandbox_data_v15" # NEW: Key for the isolated sandbox data
    
    def __init__(self):
        """Initializes session state, loading live data and setting up sandbox keys if not present."""
        if self._PMO_LIVE_DATA_KEY not in st.session_state:
            logger.info("Initializing session state with live sPMO data model.")
            with st.spinner("Connecting to enterprise systems and running predictive models..."):
                st.session_state[self._PMO_LIVE_DATA_KEY] = _load_and_process_data()
                st.session_state[self._PMO_SANDBOX_KEY] = None # Sandbox is initially empty
                st.session_state['sandbox_mode'] = False
                st.session_state['audit_trail'] = [] # Initialize empty audit trail

    def _get_active_data_model(self, is_write_op: bool = False):
        """Returns the active data model (live or sandbox) based on the current mode."""
        if st.session_state.get('sandbox_mode', False):
            # If in sandbox mode, always return the sandbox model
            return st.session_state[self._PMO_SANDBOX_KEY]
        
        if is_write_op:
            # Prevent accidental writes to live data; force sandbox for state changes
            st.error("State modifications are only allowed in Sandbox Mode. Please activate it.")
            st.stop()
        
        # Default to live data for read operations
        return st.session_state[self._PMO_LIVE_DATA_KEY]

    def get_data(self, key: str, default: Any = None) -> Any:
        """Safely retrieves data from the currently active data model (live or sandbox)."""
        active_model = self._get_active_data_model()
        return active_model.get(key, default if default is not None else [])

    def log_audit_event(self, event_type: str, details: str, user: str = "System"):
        """Logs a critical event to the audit trail for compliance."""
        # NEW: Centralized audit logging for 21 CFR Part 11
        event = {
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "event_type": event_type,
            "details": details
        }
        st.session_state['audit_trail'].append(event)
        logger.info(f"AUDIT EVENT: {event}")

    def approve_dcr(self, dcr_id: str, project_id: str, user: str):
        """Workflow to approve a DCR and log the event."""
        # NEW: Workflow integration example
        active_model = self._get_active_data_model(is_write_op=True)
        changes = active_model['change_controls']
        for change in changes:
            if change['dcr_id'] == dcr_id:
                change['status'] = 'Approved'
                self.log_audit_event("DCR Approval", f"User '{user}' approved DCR '{dcr_id}' for project '{project_id}'.", user)
                break
    
    def reallocate_resources_from_project(self, project_id_to_cancel: str):
        """Sandbox-only: Zeros out allocations for a canceled project, freeing resources."""
        # NEW: Deeper what-if simulation
        if not st.session_state.get('sandbox_mode', False):
            st.warning("Resource reallocation is only available in Sandbox Mode.")
            return

        active_model = self._get_active_data_model()
        # Create a new list of allocations, excluding the canceled project's
        current_allocations = active_model['allocations']
        new_allocations = [alloc for alloc in current_allocations if alloc['project_id'] != project_id_to_cancel]
        active_model['allocations'] = new_allocations
        self.log_audit_event("Sandbox Simulation", f"Simulated resource reallocation from canceled project '{project_id_to_cancel}'.")


    def toggle_sandbox(self):
        """Toggles the sandbox mode on or off, creating or clearing the sandbox data."""
        current_mode = st.session_state.get('sandbox_mode', False)
        new_mode = not current_mode
        st.session_state['sandbox_mode'] = new_mode
        
        if new_mode:
            # Entering sandbox: create a deep copy of live data to isolate changes
            st.session_state[self._PMO_SANDBOX_KEY] = copy.deepcopy(st.session_state[self._PMO_LIVE_DATA_KEY])
            self.log_audit_event("Sandbox Simulation", "Sandbox mode activated. A deep copy of live data was created for simulation.")
        else:
            # Exiting sandbox: clear the sandbox data
            st.session_state[self._PMO_SANDBOX_KEY] = None
