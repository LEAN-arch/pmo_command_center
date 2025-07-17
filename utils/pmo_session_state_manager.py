# pmo_command_center/utils/pmo_session_state_manager.py
"""
Manages the application's session state, simulating a rich and realistic IVD project
portfolio for the Werfen Autoimmunity sPMO Director. This model is the data
foundation for all strategic, financial, resource, and compliance dashboards,
now enhanced to a commercial-grade level with expanded data models.
"""
import logging
import random
from datetime import date, timedelta
from typing import Any, Dict
import streamlit as st
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

def _create_spmo_model(version: float) -> Dict[str, Any]:
    """
    Generates a comprehensive, interconnected dataset simulating a Werfen Autoimmunity
    portfolio. This commercial-grade version includes data for DHF, RAID logs,
    EVM, and on-market products to power advanced dashboard features.
    """
    np.random.seed(42)
    random.seed(42)
    base_date = date.today() - timedelta(days=730)  # History starts 2 years ago

    # --- 1. Strategic Goals ---
    strategic_goals = [
        {"id": "SG-01", "goal": "Win High-Throughput Rheumatology Segment", "description": "Launch new, high-value assays to capture the high-volume rheumatology testing market."},
        {"id": "SG-02", "goal": "Achieve Full IVDR Compliance", "description": "Ensure all relevant on-market products meet new European IVD regulations to maintain market access."},
        {"id": "SG-03", "goal": "Expand Clinical Utility of BIO-FLASH", "description": "Develop novel biomarkers and applications for the BIO-FLASH platform to enter new clinical areas."},
        {"id": "SG-04", "goal": "Improve Operational Efficiency & COGS", "description": "Reduce COGS and improve manufacturing throughput for key product lines like Aptiva."},
    ]

    # --- 2. Projects (Enhanced with EVM and Historical Data for ML) ---
    projects = [
        # Active Projects
        {"id": "NPD-001", "name": "Aptiva Celiac Disease Panel", "project_type": "NPD", "phase": "Development", "pm": "John Smith", "strategic_goal_id": "SG-01", "complexity": 5, "team_size": 12,
         "description": "A next-generation panel for Celiac Disease diagnosis on the Aptiva platform, targeting high-throughput labs.", "strategic_value": 9, "risk_score": 7, "health_status": "At Risk", "regulatory_path": "510(k)",
         "budget_usd": 5000000, "actuals_usd": 4100000, "pv_usd": 3250000, "ev_usd": 3000000, "start_date": base_date + timedelta(days=230), "end_date": base_date + timedelta(days=960), "completion_pct": 65, "final_outcome": None},
        {"id": "NPD-002", "name": "BIO-FLASH Connectivity Module", "project_type": "NPD", "phase": "V&V", "pm": "Jane Doe", "strategic_goal_id": "SG-04", "complexity": 3, "team_size": 8,
         "description": "A new hardware and software module to enable secure, cloud-based data integration for the BIO-FLASH instrument.", "strategic_value": 7, "risk_score": 4, "health_status": "On Track", "regulatory_path": "Letter to File",
         "budget_usd": 2500000, "actuals_usd": 1200000, "pv_usd": 1000000, "ev_usd": 1100000, "start_date": base_date + timedelta(days=380), "end_date": base_date + timedelta(days=1110), "completion_pct": 40, "final_outcome": None},
        {"id": "NPD-003", "name": "NextGen Vasculitis Biomarker", "project_type": "NPD", "phase": "Feasibility", "pm": "Sofia Chen", "strategic_goal_id": "SG-03", "complexity": 5, "team_size": 10,
         "description": "A research-intensive project to develop a novel biomarker for a new vasculitis testing paradigm on QUANTA Flash.", "strategic_value": 8, "risk_score": 8, "health_status": "Needs Monitoring", "regulatory_path": "PMA",
         "budget_usd": 8500000, "actuals_usd": 750000, "pv_usd": 850000, "ev_usd": 700000, "start_date": base_date + timedelta(days=530), "end_date": base_date + timedelta(days=1400), "completion_pct": 10, "final_outcome": None},
        {"id": "LCM-002", "name": "QUANTA-Lyser IVDR Compliance", "project_type": "LCM", "phase": "Remediation", "pm": "David Lee", "strategic_goal_id": "SG-02", "complexity": 4, "team_size": 15,
         "description": "A large-scale remediation project to update the QUANTA-Lyser technical file and QMS evidence to meet new European IVDR requirements.", "strategic_value": 10, "risk_score": 6, "health_status": "At Risk", "regulatory_path": "IVDR Class C",
         "budget_usd": 3200000, "actuals_usd": 2950000, "pv_usd": 3040000, "ev_usd": 2800000, "start_date": base_date + timedelta(days=290), "end_date": base_date + timedelta(days=740), "completion_pct": 95, "final_outcome": None},
        # Historical Projects for ML Training
        {"id": "LCM-H01", "name": "QUANTA-Lyser 4.0 Software Update", "project_type": "LCM", "phase": "Completed", "pm": "Mike Ross", "strategic_goal_id": "SG-04", "complexity": 2, "team_size": 5,
         "description": "Lifecycle management project to update the QUANTA-Lyser software with new security patches and minor feature enhancements.", "strategic_value": 4, "risk_score": 2, "health_status": "Completed", "regulatory_path": "N/A",
         "budget_usd": 500000, "actuals_usd": 450000, "pv_usd": 500000, "ev_usd": 500000, "start_date": base_date, "end_date": base_date + timedelta(days=150), "completion_pct": 100, "final_outcome": "On-Time"},
        {"id": "NPD-H01", "name": "BioPlex 2200 Connectivity", "project_type": "NPD", "phase": "Completed", "pm": "Jane Doe", "strategic_goal_id": "SG-04", "complexity": 4, "team_size": 9,
         "description": "Historical project for LIS2-A2 interface development.", "strategic_value": 6, "risk_score": 5, "health_status": "Completed", "regulatory_path": "Letter to File",
         "budget_usd": 1800000, "actuals_usd": 2100000, "pv_usd": 1800000, "ev_usd": 1800000, "start_date": base_date, "end_date": base_date + timedelta(days=400), "completion_pct": 100, "final_outcome": "Delayed"},
        {"id": "NPD-H02", "name": "QUANTA Flash® cANCA Assay", "project_type": "NPD", "phase": "Completed", "pm": "John Smith", "strategic_goal_id": "SG-01", "complexity": 3, "team_size": 7,
         "description": "Historical assay development project.", "strategic_value": 8, "risk_score": 3, "health_status": "Completed", "regulatory_path": "510(k)",
         "budget_usd": 3000000, "actuals_usd": 2800000, "pv_usd": 3000000, "ev_usd": 3000000, "start_date": base_date, "end_date": base_date + timedelta(days=550), "completion_pct": 100, "final_outcome": "On-Time"},
    ]

    # --- 10++ Feature: On-Market Product Data ---
    on_market_products = [
        {"product_name": "Aptiva® System & Reagents", "open_capas": 3, "complaint_rate_ytd": 0.35, "sustaining_project_status": "On Track - SW v2.1 Patch"},
        {"product_name": "QUANTA Flash® Reagents", "open_capas": 1, "complaint_rate_ytd": 0.15, "sustaining_project_status": "Monitoring Supplier"},
        {"product_name": "BIO-FLASH® System", "open_capas": 2, "complaint_rate_ytd": 0.22, "sustaining_project_status": "At Risk - Optics Upgrade"},
        {"product_name": "NOVA View® System", "open_capas": 0, "complaint_rate_ytd": 0.08, "sustaining_project_status": "On Track"},
    ]

    # --- 3. Resources ---
    resources = [
        {"name": "Alice Weber", "role": "Instrument R&D", "cost_per_hour": 110, "capacity_hours_week": 40},
        {"name": "Bob Chen", "role": "Software R&D", "cost_per_hour": 100, "capacity_hours_week": 40},
        {"name": "Charlie Day", "role": "Assay R&D", "cost_per_hour": 95, "capacity_hours_week": 40},
        {"name": "Diana Evans", "role": "RA/QA", "cost_per_hour": 120, "capacity_hours_week": 40},
        {"name": "Frank Green", "role": "Software R&D", "cost_per_hour": 115, "capacity_hours_week": 40},
        {"name": "Grace Hopper", "role": "Clinical Affairs", "cost_per_hour": 125, "capacity_hours_week": 40},
        {"name": "Henry Ford", "role": "Operations", "cost_per_hour": 90, "capacity_hours_week": 40},
    ]
    allocations = [
        {"project_id": "NPD-001", "resource_name": "Charlie Day", "allocated_hours_week": 20}, {"project_id": "NPD-001", "resource_name": "Diana Evans", "allocated_hours_week": 10},
        {"project_id": "NPD-002", "resource_name": "Alice Weber", "allocated_hours_week": 25}, {"project_id": "NPD-002", "resource_name": "Bob Chen", "allocated_hours_week": 40},
        {"project_id": "NPD-003", "resource_name": "Charlie Day", "allocated_hours_week": 20}, {"project_id": "NPD-003", "resource_name": "Grace Hopper", "allocated_hours_week": 20},
        {"project_id": "LCM-002", "resource_name": "Diana Evans", "allocated_hours_week": 30}, {"project_id": "LCM-002", "resource_name": "Henry Ford", "allocated_hours_week": 20},
    ]

    # --- 4. Milestones & Change Controls ---
    milestones = [
        {"project_id": "NPD-001", "milestone": "Assay Design Lock", "due_date": (base_date + timedelta(days=300)).isoformat(), "status": "Completed"},
        {"project_id": "NPD-001", "milestone": "V&V Start", "due_date": (base_date + timedelta(days=450)).isoformat(), "status": "At Risk"},
        {"project_id": "NPD-001", "milestone": "510(k) Submission", "due_date": (base_date + timedelta(days=700)).isoformat(), "status": "Pending"},
        {"project_id": "NPD-002", "milestone": "Prototype Complete", "due_date": (base_date + timedelta(days=400)).isoformat(), "status": "Completed"},
    ]
    
    # *** FIX 1: RESTORE THE CHANGE CONTROLS DATA ***
    change_controls = [
        {"dcr_id": "DCR-24-001", "project_id": "NPD-001", "description": "Change primary antibody supplier due to performance issues.", "status": "Approved"},
        {"dcr_id": "DCR-24-002", "project_id": "NPD-002", "description": "Update embedded OS to new version for security patch.", "status": "In Review"},
    ]
    
    # --- 5. Centralized RAID Log ---
    raid_logs = [
        {"log_id": "R-001", "project_id": "NPD-001", "type": "Risk", "description": "Key sensor supplier fails to meet quality specs.", "owner": "Henry Ford", "status": "Mitigating", "due_date": (date.today() + timedelta(days=30)).isoformat()},
        {"log_id": "I-001", "project_id": "NPD-001", "type": "Issue", "description": "Test batch #3 showed unexpected cross-reactivity.", "owner": "Charlie Day", "status": "In Progress", "due_date": (date.today() + timedelta(days=7)).isoformat()},
        {"log_id": "D-001", "project_id": "NPD-001", "type": "Decision", "description": "Proceed with alternative antibody supplier (Vendor B).", "owner": "John Smith", "status": "Closed", "due_date": (date.today() - timedelta(days=10)).isoformat()},
        {"log_id": "R-002", "project_id": "LCM-002", "type": "Risk", "description": "IVDR Notified Body requests additional clinical data.", "owner": "Diana Evans", "status": "Monitoring", "due_date": (date.today() + timedelta(days=60)).isoformat()},
        {"log_id": "A-001", "project_id": "NPD-003", "type": "Assumption", "description": "Novel biomarker chemistry is stable at scale.", "owner": "Sofia Chen", "status": "Open", "due_date": (date.today() + timedelta(days=120)).isoformat()},
    ]

    # --- 6. DHF and Traceability Data ---
    dhf_documents = [
        {"doc_id": "DHF-N001-01", "project_id": "NPD-001", "doc_type": "Design & Development Plan", "status": "Approved", "owner": "John Smith"},
        {"doc_id": "DHF-N001-02", "project_id": "NPD-001", "doc_type": "User Needs & Requirements", "status": "Approved", "owner": "John Smith"},
        {"doc_id": "DHF-N001-03", "project_id": "NPD-001", "doc_type": "Risk Management File", "status": "In Review", "owner": "Diana Evans"},
        {"doc_id": "DHF-N001-04", "project_id": "NPD-001", "doc_type": "V&V Master Plan", "status": "Draft", "owner": "Charlie Day"},
        {"doc_id": "DHF-N002-01", "project_id": "NPD-002", "doc_type": "Design & Development Plan", "status": "Approved", "owner": "Jane Doe"},
        {"doc_id": "DHF-N002-02", "project_id": "NPD-002", "doc_type": "Software Requirements Spec", "status": "Approved", "owner": "Bob Chen"},
        {"doc_id": "DHF-N002-03", "project_id": "NPD-002", "doc_type": "Risk Management File", "status": "Approved", "owner": "Diana Evans"},
    ]
    traceability_matrix = [
        {"project_id": "NPD-002", "source": "User Need 1: Secure Data Tx", "target": "SW Req 1.1: Use TLS 1.3", "value": 1},
        {"project_id": "NPD-002", "source": "User Need 1: Secure Data Tx", "target": "SW Req 1.2: Encrypt at Rest", "value": 1},
        {"project_id": "NPD-002", "source": "SW Req 1.1: Use TLS 1.3", "target": "Test Case 101: TLS Handshake", "value": 1},
        {"project_id": "NPD-002", "source": "SW Req 1.2: Encrypt at Rest", "target": "Test Case 102: Data Encryption", "value": 1},
    ]

    # --- 7. Full Financials & Phase Gate Data ---
    financials, phase_gate_data = [], []
    for p in projects:
        project_start_date = pd.to_datetime(p['start_date'])
        project_end_date = pd.to_datetime(p['end_date'])
        project_duration_months = max(1, (project_end_date - project_start_date).days / 30.0)
        months_elapsed = max(0, (pd.to_datetime(date.today()) - project_start_date).days / 30.0)
        if p['health_status'] == 'Completed':
            months_elapsed = project_duration_months
        if months_elapsed > 0:
            for i in range(int(project_duration_months)):
                month_date = project_start_date + pd.DateOffset(months=i)
                planned_spend = p['budget_usd'] / project_duration_months
                financials.append({"project_id": p['id'], "date": month_date.isoformat(), "type": "Planned", "category": "R&D Opex", "amount": planned_spend * 0.6})
                financials.append({"project_id": p['id'], "date": month_date.isoformat(), "type": "Planned", "category": "Clinical/Reg", "amount": planned_spend * 0.2})
                financials.append({"project_id": p['id'], "date": month_date.isoformat(), "type": "Planned", "category": "Capex", "amount": planned_spend * 0.1})
                financials.append({"project_id": p['id'], "date": month_date.isoformat(), "type": "Planned", "category": "Other G&A", "amount": planned_spend * 0.1})
                if i < months_elapsed:
                    spend_factor = 1.2 if p['risk_score'] > 6 else 1.0
                    actual_spend_total = planned_spend * np.random.uniform(0.9, 1.1) * spend_factor
                    if p['id'] == 'NPD-001' and i == 10:
                        actual_spend_total += 300000 # anomaly
                    financials.append({"project_id": p['id'], "date": month_date.isoformat(), "type": "Actuals", "category": "R&D Opex", "amount": actual_spend_total * 0.65})
                    financials.append({"project_id": p['id'], "date": month_date.isoformat(), "type": "Actuals", "category": "Clinical/Reg", "amount": actual_spend_total * 0.15})
                    financials.append({"project_id": p['id'], "date": month_date.isoformat(), "type": "Actuals", "category": "Capex", "amount": actual_spend_total * 0.1})
                    financials.append({"project_id": p['id'], "date": month_date.isoformat(), "type": "Actuals", "category": "Other G&A", "amount": actual_spend_total * 0.1})

        # Phase Gate data
        if p['project_type'] == 'NPD':
            phase_gate_data.append({"project_id": p['id'], "gate_name": "Gate 2: Feasibility", "planned_date": (project_start_date + timedelta(days=180)).isoformat(), "actual_date": (project_start_date + timedelta(days=190)).isoformat() if p['id'] != 'NPD-003' else None})
            phase_gate_data.append({"project_id": p['id'], "gate_name": "Gate 3: Development", "planned_date": (project_start_date + timedelta(days=400)).isoformat(), "actual_date": (project_start_date + timedelta(days=450)).isoformat() if p['id'] in ['NPD-001', 'NPD-H02', 'NPD-H01'] else None})

    # --- 8. QMS & Time Series Data ---
    qms_kpis = {"open_capas": 8, "overdue_capas": 2, "internal_audit_findings_open": 5, "overdue_training_records": 12}
    resource_demand_history = []
    for role in ["Instrument R&D", "Software R&D", "Assay R&D", "RA/QA", "Clinical Affairs", "Operations"]:
        for i in range(24):
            month_date = base_date + timedelta(days=i*30)
            base_demand, trend, seasonality, noise = random.randint(80, 250), i * 4, 40 * np.sin(2 * np.pi * i / 12), random.randint(-20, 20)
            demand = base_demand + trend + seasonality + noise
            resource_demand_history.append({"date": month_date.isoformat(), "role": role, "demand_hours": max(0, demand)})

    # --- Final Data Assembly ---
    # Add calculated EVM metrics to projects
    for p in projects:
        p['cpi'] = p['ev_usd'] / p['actuals_usd'] if p['actuals_usd'] > 0 else 0
        p['spi'] = p['ev_usd'] / p['pv_usd'] if p['pv_usd'] > 0 else 0
        p['eac_usd'] = p['budget_usd'] / p['cpi'] if p['cpi'] > 0 else p['budget_usd']

    return {
        "data_version": version, "strategic_goals": strategic_goals, "projects": projects,
        "resources": resources, "allocations": allocations, "milestones": milestones,
        "raid_logs": raid_logs, "qms_kpis": qms_kpis, "financials": financials,
        "on_market_products": on_market_products, "dhf_documents": dhf_documents,
        "traceability_matrix": traceability_matrix, "phase_gate_data": phase_gate_data,
        "resource_demand_history": resource_demand_history,
        # *** FIX 2: ADD CHANGE CONTROLS TO THE RETURNED DICTIONARY ***
        "change_controls": change_controls,
    }


class SPMOSessionStateManager:
    _PMO_DATA_KEY = "pmo_commercial_grade_data_v10"
    _CURRENT_DATA_VERSION = 10.0  # Version bump for commercial grade overhaul

    def __init__(self):
        """Initializes or retrieves the session state for the sPMO data model."""
        if st.session_state.get(self._PMO_DATA_KEY, {}).get("data_version") != self._CURRENT_DATA_VERSION:
            logger.info(f"Initializing session state with commercial-grade sPMO data model v{self._CURRENT_DATA_VERSION}.")
            with st.spinner("Generating Werfen Autoimmunity sPMO Simulation..."):
                st.session_state[self._PMO_DATA_KEY] = _create_spmo_model(self._CURRENT_DATA_VERSION)

    def get_data(self, key: str, default: Any = None) -> Any:
        """Safely retrieves data from the session state model."""
        return st.session_state.get(self._PMO_DATA_KEY, {}).get(key, default if default is not None else [])
