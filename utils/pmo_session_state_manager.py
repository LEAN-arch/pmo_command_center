# pmo_command_center/utils/pmo_session_state_manager.py
"""
Manages the application's session state, simulating a realistic IVD project
portfolio for the Werfen Autoimmunity PMO Director. This version includes
detailed phase-gate data, financial tracking, and QMS metrics to support
strategic oversight and process maturity analysis.
"""
import logging
import random
from datetime import date, timedelta
from typing import Any, Dict, List
import streamlit as st
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

def _create_werfen_pmo_model(version: int) -> Dict[str, Any]:
    """
    Generates an interconnected dataset simulating a Werfen Autoimmunity portfolio.
    It includes NPD and LCM projects, IVD-specific risks, resources, and QMS metrics.
    """
    np.random.seed(42)
    random.seed(42)
    base_date = date.today() - timedelta(days=500)

    projects = [
        {"id": "NPD-001", "name": "AcuStar NeoSTAT IL-6 Assay", "project_type": "NPD", "phase": "Development", "pm": "John Smith",
         "strategic_value": 9, "risk_score": 7, "health_status": "At Risk", "regulatory_path": "510(k)",
         "budget_usd": 5000000, "actuals_usd": 4100000, "start_date": base_date, "end_date": base_date + timedelta(days=730), "completion_pct": 65},
        {"id": "NPD-002", "name": "GEM Premier 6000 Connectivity Module", "project_type": "NPD", "phase": "V&V", "pm": "Jane Doe",
         "strategic_value": 7, "risk_score": 4, "health_status": "On Track", "regulatory_path": "Letter to File",
         "budget_usd": 2500000, "actuals_usd": 1200000, "start_date": base_date + timedelta(days=180), "end_date": base_date + timedelta(days=910), "completion_pct": 40},
        {"id": "LCM-001", "name": "QUANTA-Lyser 4.0 Software Update", "project_type": "LCM", "phase": "Completed", "pm": "Mike Ross",
         "strategic_value": 4, "risk_score": 2, "health_status": "Completed", "regulatory_path": "N/A",
         "budget_usd": 500000, "actuals_usd": 450000, "start_date": base_date + timedelta(days=300), "end_date": base_date + timedelta(days=450), "completion_pct": 100},
        {"id": "NPD-003", "name": "NextGen Hemostasis Reagent", "project_type": "NPD", "phase": "Feasibility", "pm": "Sofia Chen",
         "strategic_value": 8, "risk_score": 8, "health_status": "Needs Monitoring", "regulatory_path": "PMA",
         "budget_usd": 8500000, "actuals_usd": 750000, "start_date": base_date + timedelta(days=330), "end_date": base_date + timedelta(days=1200), "completion_pct": 10},
        {"id": "LCM-002", "name": "Aptiva IVDR Compliance Project", "project_type": "LCM", "phase": "Remediation", "pm": "David Lee",
         "strategic_value": 10, "risk_score": 6, "health_status": "At Risk", "regulatory_path": "IVDR Class C",
         "budget_usd": 3200000, "actuals_usd": 2950000, "start_date": base_date + timedelta(days=90), "end_date": base_date + timedelta(days=540), "completion_pct": 95}
    ]

    resources = [
        {"name": "Alice Weber", "role": "Instrument Engineer", "cost_per_hour": 110, "capacity_hours_week": 40},
        {"name": "Bob Chen", "role": "Software Engineer (Embedded)", "cost_per_hour": 100, "capacity_hours_week": 40},
        {"name": "Charlie Day", "role": "Assay Development Scientist", "cost_per_hour": 95, "capacity_hours_week": 40},
        {"name": "Diana Evans", "role": "RA/QA Specialist", "cost_per_hour": 120, "capacity_hours_week": 40},
        {"name": "Frank Green", "role": "Bioinformatician", "cost_per_hour": 115, "capacity_hours_week": 40},
        {"name": "Grace Hopper", "role": "Clinical Affairs", "cost_per_hour": 125, "capacity_hours_week": 40},
        {"name": "Henry Ford", "role": "Manufacturing Engineer", "cost_per_hour": 90, "capacity_hours_week": 40}
    ]

    allocations = [
        {"project_id": "NPD-001", "resource_name": "Charlie Day", "allocated_hours_week": 20},
        {"project_id": "NPD-001", "resource_name": "Diana Evans", "allocated_hours_week": 10},
        {"project_id": "NPD-002", "resource_name": "Alice Weber", "allocated_hours_week": 25},
        {"project_id": "NPD-002", "resource_name": "Bob Chen", "allocated_hours_week": 40},
        {"project_id": "LCM-001", "resource_name": "Bob Chen", "allocated_hours_week": 10}, # Creates over-allocation for Bob
        {"project_id": "NPD-003", "resource_name": "Charlie Day", "allocated_hours_week": 20}, # Creates over-allocation for Charlie
        {"project_id": "NPD-003", "resource_name": "Grace Hopper", "allocated_hours_week": 20},
        {"project_id": "LCM-002", "resource_name": "Diana Evans", "allocated_hours_week": 30}, # Creates over-allocation for Diana
        {"project_id": "LCM-002", "resource_name": "Henry Ford", "allocated_hours_week": 20},
    ]

    # --- Data for PMO Methodology & Maturity Dashboard ---
    phase_gate_data = [
        # Project 1: Started on time, but some later gates are delayed
        {"project_id": "NPD-001", "gate_name": "Gate 1: Concept", "planned_date": base_date + timedelta(days=60), "actual_date": base_date + timedelta(days=60), "status": "Approved"},
        {"project_id": "NPD-001", "gate_name": "Gate 2: Feasibility", "planned_date": base_date + timedelta(days=180), "actual_date": base_date + timedelta(days=190), "status": "Approved"},
        {"project_id": "NPD-001", "gate_name": "Gate 3: Development", "planned_date": base_date + timedelta(days=400), "actual_date": base_date + timedelta(days=450), "status": "Approved"},
        {"project_id": "NPD-001", "gate_name": "Gate 4: V&V", "planned_date": base_date + timedelta(days=600), "actual_date": None, "status": "Pending"},
        # Project 2: On track
        {"project_id": "NPD-002", "gate_name": "Gate 1: Concept", "planned_date": base_date + timedelta(days=240), "actual_date": base_date + timedelta(days=245), "status": "Approved"},
        {"project_id": "NPD-002", "gate_name": "Gate 2: Feasibility", "planned_date": base_date + timedelta(days=360), "actual_date": base_date + timedelta(days=360), "status": "Approved"},
        # Project 5: Remediation project with aggressive, tight gates
        {"project_id": "LCM-002", "gate_name": "Gap Analysis Complete", "planned_date": base_date + timedelta(days=150), "actual_date": base_date + timedelta(days=180), "status": "Approved"},
        {"project_id": "LCM-002", "gate_name": "Tech File Updated", "planned_date": base_date + timedelta(days=360), "actual_date": base_date + timedelta(days=400), "status": "Approved"},
    ]

    # --- QMS & Compliance Data for Risk Dashboard ---
    qms_kpis = {
        "open_capas": 8, "overdue_capas": 2,
        "post_market_complaints_ytd": 112,
        "overdue_training_records": 15,
        "internal_audit_findings_open": 5,
    }
    
    # Financial data with more detail for each project
    financials = []
    for p in projects:
        # Simulate monthly spend
        project_duration_months = (p['end_date'] - p['start_date']).days / 30.0
        months_elapsed = (date.today() - p['start_date']).days / 30.0
        if months_elapsed > 0:
            for i in range(int(months_elapsed)):
                month_date = p['start_date'] + timedelta(days=i*30)
                # Simulate some variability in monthly spend
                monthly_spend = (p['budget_usd'] / project_duration_months) * np.random.uniform(0.8, 1.2)
                financials.append({
                    "project_id": p['id'],
                    "date": month_date,
                    "type": "Actuals",
                    "amount": monthly_spend
                })
                financials.append({
                    "project_id": p['id'],
                    "date": month_date,
                    "type": "Planned",
                    "amount": p['budget_usd'] / project_duration_months
                })

    return {
        "data_version": version,
        "projects": projects,
        "resources": resources,
        "allocations": allocations,
        "phase_gate_data": phase_gate_data,
        "qms_kpis": qms_kpis,
        "financials": financials,
    }


class PMOSessionStateManager:
    """Handles the initialization and access of the application's session state."""
    _PMO_DATA_KEY = "werfen_pmo_data_v3"
    _CURRENT_DATA_VERSION = 3.0 # Werfen IVD Enhanced Refactor

    def __init__(self):
        """Initializes the session state, loading the mock data if necessary."""
        session_data = st.session_state.get(self._PMO_DATA_KEY)
        if not session_data or session_data.get("data_version") != self._CURRENT_DATA_VERSION:
            logger.info(f"Initializing session state with Werfen PMO data model v{self._CURRENT_DATA_VERSION}.")
            with st.spinner("Generating Werfen Autoimmunity Portfolio Simulation..."):
                st.session_state[self._PMO_DATA_KEY] = _create_werfen_pmo_model(self._CURRENT_DATA_VERSION)

    def get_data(self, key: str) -> Any:
        """Safely retrieves data from the session state dictionary."""
        return st.session_state.get(self._PMO_DATA_KEY, {}).get(key, [])
