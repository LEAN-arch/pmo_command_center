# werfen_pmo_command_center/utils/pmo_session_state_manager.py
"""
Manages the application's session state, simulating a rich and realistic IVD project
portfolio for the Werfen Autoimmunity sPMO Director. This model is the data
foundation for all strategic, financial, resource, and compliance dashboards.
"""
import logging
import random
from datetime import date, timedelta
from typing import Any, Dict, List
import streamlit as st
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

def _create_werfen_spmo_model(version: float) -> Dict[str, Any]:
    """
    Generates a comprehensive, interconnected dataset simulating a Werfen Autoimmunity
    portfolio. It includes NPD and LCM projects, granular milestones, financials,
    IVD-specific risks, resources by function, and QMS metrics.
    """
    np.random.seed(42)
    random.seed(42)
    base_date = date.today() - timedelta(days=500)

    # --- 1. Strategic Goals ---
    strategic_goals = [
        {"id": "SG-01", "goal": "Expand Autoimmunity Assay Menu", "description": "Launch new, high-value assays to grow market share in core areas."},
        {"id": "SG-02", "goal": "Achieve Full IVDR Compliance", "description": "Ensure all relevant on-market products meet new European IVD regulations to maintain market access."},
        {"id": "SG-03", "goal": "Develop Point-of-Care (POC) Platform", "description": "Enter new market segments with a decentralized testing platform."},
        {"id": "SG-04", "goal": "Improve Operational Efficiency", "description": "Reduce COGS and improve manufacturing throughput for key product lines."},
    ]

    # --- 2. Projects ---
    projects = [
        {"id": "NPD-001", "name": "AcuStar NeoSTAT IL-6 Assay", "project_type": "NPD", "phase": "Development", "pm": "John Smith", "strategic_goal_id": "SG-01",
         "strategic_value": 9, "risk_score": 7, "health_status": "At Risk", "regulatory_path": "510(k)",
         "budget_usd": 5000000, "actuals_usd": 4100000, "start_date": base_date, "end_date": base_date + timedelta(days=730), "completion_pct": 65},
        {"id": "NPD-002", "name": "GEM Premier 6000 Connectivity Module", "project_type": "NPD", "phase": "V&V", "pm": "Jane Doe", "strategic_goal_id": "SG-04",
         "strategic_value": 7, "risk_score": 4, "health_status": "On Track", "regulatory_path": "Letter to File",
         "budget_usd": 2500000, "actuals_usd": 1200000, "start_date": base_date + timedelta(days=180), "end_date": base_date + timedelta(days=910), "completion_pct": 40},
        {"id": "LCM-001", "name": "QUANTA-Lyser 4.0 Software Update", "project_type": "LCM", "phase": "Completed", "pm": "Mike Ross", "strategic_goal_id": "SG-04",
         "strategic_value": 4, "risk_score": 2, "health_status": "Completed", "regulatory_path": "N/A",
         "budget_usd": 500000, "actuals_usd": 450000, "start_date": base_date + timedelta(days=300), "end_date": base_date + timedelta(days=450), "completion_pct": 100},
        {"id": "NPD-003", "name": "NextGen Hemostasis Reagent", "project_type": "NPD", "phase": "Feasibility", "pm": "Sofia Chen", "strategic_goal_id": "SG-01",
         "strategic_value": 8, "risk_score": 8, "health_status": "Needs Monitoring", "regulatory_path": "PMA",
         "budget_usd": 8500000, "actuals_usd": 750000, "start_date": base_date + timedelta(days=330), "end_date": base_date + timedelta(days=1200), "completion_pct": 10},
        {"id": "LCM-002", "name": "Aptiva IVDR Compliance Project", "project_type": "LCM", "phase": "Remediation", "pm": "David Lee", "strategic_goal_id": "SG-02",
         "strategic_value": 10, "risk_score": 6, "health_status": "At Risk", "regulatory_path": "IVDR Class C",
         "budget_usd": 3200000, "actuals_usd": 2950000, "start_date": base_date + timedelta(days=90), "end_date": base_date + timedelta(days=540), "completion_pct": 95}
    ]

    # --- 3. Resources by Function ---
    resources = [
        {"name": "Alice Weber", "role": "Instrument R&D", "cost_per_hour": 110, "capacity_hours_week": 40},
        {"name": "Bob Chen", "role": "Software R&D", "cost_per_hour": 100, "capacity_hours_week": 40},
        {"name": "Charlie Day", "role": "Assay R&D", "cost_per_hour": 95, "capacity_hours_week": 40},
        {"name": "Diana Evans", "role": "RA/QA", "cost_per_hour": 120, "capacity_hours_week": 40},
        {"name": "Frank Green", "role": "Software R&D", "cost_per_hour": 115, "capacity_hours_week": 40},
        {"name": "Grace Hopper", "role": "Clinical Affairs", "cost_per_hour": 125, "capacity_hours_week": 40},
        {"name": "Henry Ford", "role": "Operations", "cost_per_hour": 90, "capacity_hours_week": 40},
    ]

    # --- 4. Resource Allocations ---
    allocations = [
        {"project_id": "NPD-001", "resource_name": "Charlie Day", "allocated_hours_week": 20},
        {"project_id": "NPD-001", "resource_name": "Diana Evans", "allocated_hours_week": 10},
        {"project_id": "NPD-002", "resource_name": "Alice Weber", "allocated_hours_week": 25},
        {"project_id": "NPD-002", "resource_name": "Bob Chen", "allocated_hours_week": 40},
        {"project_id": "LCM-001", "resource_name": "Bob Chen", "allocated_hours_week": 10},
        {"project_id": "NPD-003", "resource_name": "Charlie Day", "allocated_hours_week": 20},
        {"project_id": "NPD-003", "resource_name": "Grace Hopper", "allocated_hours_week": 20},
        {"project_id": "LCM-002", "resource_name": "Diana Evans", "allocated_hours_week": 30},
        {"project_id": "LCM-002", "resource_name": "Henry Ford", "allocated_hours_week": 20},
    ]

    # --- 5. Project-Specific Details (Milestones, Risks, Changes) ---
    milestones = [
        {"project_id": "NPD-001", "milestone": "Assay Design Lock", "due_date": base_date + timedelta(days=300), "status": "Completed"},
        {"project_id": "NPD-001", "milestone": "V&V Start", "due_date": base_date + timedelta(days=450), "status": "At Risk"},
        {"project_id": "NPD-001", "milestone": "510(k) Submission", "due_date": base_date + timedelta(days=700), "status": "Pending"},
        {"project_id": "NPD-002", "milestone": "Prototype Complete", "due_date": base_date + timedelta(days=400), "status": "Completed"},
        {"project_id": "NPD-002", "milestone": "SW V&V Complete", "due_date": base_date + timedelta(days=600), "status": "On Track"},
        {"project_id": "LCM-002", "milestone": "Technical File Remediation", "due_date": base_date + timedelta(days=400), "status": "Completed"},
        {"project_id": "LCM-002", "milestone": "Notified Body Submission", "due_date": base_date + timedelta(days=500), "status": "Completed"},
    ]
    
    project_risks = [
        {"risk_id": "R-NPD001-01", "project_id": "NPD-001", "description": "Key sensor supplier fails to meet quality specs.", "probability": 4, "impact": 5, "status": "Mitigating"},
        {"risk_id": "R-LCM002-01", "project_id": "LCM-002", "description": "IVDR Notified Body requests additional clinical data.", "probability": 3, "impact": 5, "status": "Monitoring"},
        {"risk_id": "R-NPD003-01", "project_id": "NPD-003", "description": "Novel biomarker shows instability in feasibility studies.", "probability": 5, "impact": 4, "status": "Action Plan Dev"},
        {"risk_id": "R-NPD002-01", "project_id": "NPD-002", "description": "Firmware integration with LIS is more complex than anticipated.", "probability": 2, "impact": 3, "status": "Mitigating"},
    ]
    
    change_controls = [
        {"dcr_id": "DCR-24-001", "project_id": "NPD-001", "description": "Change primary antibody supplier due to performance issues.", "status": "Approved"},
        {"dcr_id": "DCR-24-002", "project_id": "NPD-002", "description": "Update embedded OS to new version for security patch.", "status": "In Review"},
    ]
    
    # --- 6. Data for PMO Methodology & Maturity ---
    phase_gate_data = [
        {"project_id": "NPD-001", "gate_name": "Gate 2: Feasibility", "planned_date": base_date + timedelta(days=180), "actual_date": base_date + timedelta(days=190), "status": "Approved"},
        {"project_id": "NPD-001", "gate_name": "Gate 3: Development", "planned_date": base_date + timedelta(days=400), "actual_date": base_date + timedelta(days=450), "status": "Approved"},
        {"project_id": "NPD-002", "gate_name": "Gate 2: Feasibility", "planned_date": base_date + timedelta(days=360), "actual_date": base_date + timedelta(days=360), "status": "Approved"},
        {"project_id": "LCM-001", "gate_name": "Gate 3: Development", "planned_date": base_date + timedelta(days=390), "actual_date": base_date + timedelta(days=385), "status": "Approved"},
    ]

    # --- 7. QMS & Compliance Data ---
    qms_kpis = {
        "open_capas": 8, "overdue_capas": 2,
        "post_market_complaints_ytd": 112,
        "overdue_training_records": 15,
        "internal_audit_findings_open": 5,
    }

    # --- 8. Cross-Entity Collaboration ---
    collaborations = [
        {"project_id": "NPD-003", "collaborating_entity": "Werfen R&D Center - Barcelona", "type": "Technology Transfer", "status": "Active"},
        {"project_id": "LCM-002", "collaborating_entity": "Werfen Regulatory - Germany", "type": "Regulatory Support", "status": "Active"},
    ]
    
    # --- 9. Financials (Time-Series Data) ---
    financials = []
    for p in projects:
        project_duration_months = max(1, (p['end_date'] - p['start_date']).days / 30.0)
        months_elapsed = max(0, (date.today() - p['start_date']).days / 30.0)
        
        # Don't generate future spend for completed projects
        if p['health_status'] == 'Completed':
            months_elapsed = project_duration_months

        if months_elapsed > 0:
            for i in range(int(project_duration_months)):
                month_date = p['start_date'] + timedelta(days=i*30)
                planned_spend = p['budget_usd'] / project_duration_months
                
                # Only generate actuals for past/current months
                if i < months_elapsed:
                    # Simulate some variability and over/under spending
                    spend_factor = 1.2 if p['health_status'] == 'At Risk' else 1.0
                    actual_spend = planned_spend * np.random.uniform(0.9, 1.1) * spend_factor
                else:
                    actual_spend = 0

                financials.append({"project_id": p['id'], "date": month_date, "type": "Planned", "amount": planned_spend})
                financials.append({"project_id": p['id'], "date": month_date, "type": "Actuals", "amount": actual_spend})

    return {
        "data_version": version,
        "strategic_goals": strategic_goals,
        "projects": projects,
        "resources": resources,
        "allocations": allocations,
        "milestones": milestones,
        "project_risks": project_risks,
        "change_controls": change_controls,
        "phase_gate_data": phase_gate_data,
        "qms_kpis": qms_kpis,
        "collaborations": collaborations,
        "financials": financials,
    }


class SPMOSessionStateManager:
    """Handles the initialization and access of the application's session state."""
    _PMO_DATA_KEY = "werfen_spmo_data_v4"
    _CURRENT_DATA_VERSION = 4.0 # Definitive sPMO Refactor

    def __init__(self):
        """Initializes the session state, loading the mock data if necessary."""
        session_data = st.session_state.get(self._PMO_DATA_KEY)
        if not session_data or session_data.get("data_version") != self._CURRENT_DATA_VERSION:
            logger.info(f"Initializing session state with Werfen sPMO data model v{self._CURRENT_DATA_VERSION}.")
            with st.spinner("Generating Werfen Autoimmunity sPMO Simulation..."):
                st.session_state[self._PMO_DATA_KEY] = _create_werfen_spmo_model(self._CURRENT_DATA_VERSION)

    def get_data(self, key: str) -> Any:
        """Safely retrieves data from the session state dictionary."""
        return st.session_state.get(self._PMO_DATA_KEY, {}).get(key, [])
