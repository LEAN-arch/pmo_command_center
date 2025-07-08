# pmo_command_center/utils/pmo_session_state_manager.py
"""
Manages the application's session state, simulating a rich and realistic IVD project
portfolio for the Autoimmunity sPMO Director. This model is the data
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

def _create_spmo_model(version: float) -> Dict[str, Any]:
    """
    Generates a comprehensive, interconnected dataset simulating an Autoimmunity
    portfolio. This version includes historical project data for training ML models.
    """
    np.random.seed(42)
    random.seed(42)
    base_date = date.today() - timedelta(days=730) # Extend history to 2 years

    # --- 1. Strategic Goals ---
    strategic_goals = [
        {"id": "SG-01", "goal": "Expand Autoimmunity Assay Menu", "description": "Launch new, high-value assays to grow market share in core areas."},
        {"id": "SG-02", "goal": "Achieve Full IVDR Compliance", "description": "Ensure all relevant on-market products meet new European IVD regulations to maintain market access."},
        {"id": "SG-03", "goal": "Develop Point-of-Care (POC) Platform", "description": "Enter new market segments with a decentralized testing platform."},
        {"id": "SG-04", "goal": "Improve Operational Efficiency", "description": "Reduce COGS and improve manufacturing throughput for key product lines."},
    ]

    # --- 2. Projects (Current & Historical) ---
    projects = [
        {"id": "NPD-001", "name": "AcuStar NeoSTAT IL-6 Assay", "project_type": "NPD", "phase": "Development", "pm": "John Smith", "strategic_goal_id": "SG-01", "complexity": 5, "team_size": 12,
         "description": "A next-generation quantitative immunoassay for Interleukin-6 for sepsis management.", "strategic_value": 9, "risk_score": 7, "health_status": "At Risk", "regulatory_path": "510(k)",
         "budget_usd": 5000000, "actuals_usd": 4100000, "start_date": base_date + timedelta(days=230), "end_date": base_date + timedelta(days=960), "completion_pct": 65, "final_outcome": None},
        {"id": "NPD-002", "name": "GEM Premier 6000 Connectivity Module", "project_type": "NPD", "phase": "V&V", "pm": "Jane Doe", "strategic_goal_id": "SG-04", "complexity": 3, "team_size": 8,
         "description": "A new hardware and software module to enable secure, cloud-based data integration for the GEM Premier instrument line.", "strategic_value": 7, "risk_score": 4, "health_status": "On Track", "regulatory_path": "Letter to File",
         "budget_usd": 2500000, "actuals_usd": 1200000, "start_date": base_date + timedelta(days=380), "end_date": base_date + timedelta(days=1110), "completion_pct": 40, "final_outcome": None},
        {"id": "NPD-003", "name": "NextGen Hemostasis Reagent", "project_type": "NPD", "phase": "Feasibility", "pm": "Sofia Chen", "strategic_goal_id": "SG-01", "complexity": 5, "team_size": 10,
         "description": "A research-intensive project to develop a novel reagent for a new hemostasis testing paradigm.", "strategic_value": 8, "risk_score": 8, "health_status": "Needs Monitoring", "regulatory_path": "PMA",
         "budget_usd": 8500000, "actuals_usd": 750000, "start_date": base_date + timedelta(days=530), "end_date": base_date + timedelta(days=1400), "completion_pct": 10, "final_outcome": None},
        {"id": "LCM-002", "name": "Aptiva IVDR Compliance Project", "project_type": "LCM", "phase": "Remediation", "pm": "David Lee", "strategic_goal_id": "SG-02", "complexity": 4, "team_size": 15,
         "description": "A large-scale remediation project to update the Aptiva technical file and QMS evidence to meet new European IVDR requirements.", "strategic_value": 10, "risk_score": 6, "health_status": "At Risk", "regulatory_path": "IVDR Class C",
         "budget_usd": 3200000, "actuals_usd": 2950000, "start_date": base_date + timedelta(days=290), "end_date": base_date + timedelta(days=740), "completion_pct": 95, "final_outcome": None},
        {"id": "LCM-001", "name": "QUANTA-Lyser 4.0 Software Update", "project_type": "LCM", "phase": "Completed", "pm": "Mike Ross", "strategic_goal_id": "SG-04", "complexity": 2, "team_size": 5,
         "description": "Lifecycle management project to update the QUANTA-Lyser software with new security patches and minor feature enhancements.", "strategic_value": 4, "risk_score": 2, "health_status": "Completed", "regulatory_path": "N/A",
         "budget_usd": 500000, "actuals_usd": 450000, "start_date": base_date, "end_date": base_date + timedelta(days=150), "completion_pct": 100, "final_outcome": "On-Time"},
        {"id": "NPD-H01", "name": "BioPlex 2200 Connectivity", "project_type": "NPD", "phase": "Completed", "pm": "Jane Doe", "strategic_goal_id": "SG-04", "complexity": 4, "team_size": 9,
         "description": "Historical project for LIS2-A2 interface development.", "strategic_value": 6, "risk_score": 5, "health_status": "Completed", "regulatory_path": "Letter to File",
         "budget_usd": 1800000, "actuals_usd": 2100000, "start_date": base_date, "end_date": base_date + timedelta(days=400), "completion_pct": 100, "final_outcome": "Delayed"},
        {"id": "NPD-H02", "name": "QUANTA Flash® cANCA Assay", "project_type": "NPD", "phase": "Completed", "pm": "John Smith", "strategic_goal_id": "SG-01", "complexity": 3, "team_size": 7,
         "description": "Historical assay development project.", "strategic_value": 8, "risk_score": 3, "health_status": "Completed", "regulatory_path": "510(k)",
         "budget_usd": 3000000, "actuals_usd": 2800000, "start_date": base_date, "end_date": base_date + timedelta(days=550), "completion_pct": 100, "final_outcome": "On-Time"},
    ]

    # --- 3 & 4. Resources & Allocations ---
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
    qms_kpis = {"open_capas": 8, "overdue_capas": 2, "post_market_complaints_ytd": 112, "overdue_training_records": 15, "internal_audit_findings_open": 5}
    
    # --- 8. Cross-Entity Collaboration ---
    collaborations = [
        {"project_id": "NPD-003", "collaborating_entity": "R&D Center - Barcelona", "type": "Technology Transfer", "status": "Active"},
        {"project_id": "LCM-002", "collaborating_entity": "Regulatory - Germany", "type": "Regulatory Support", "status": "Active"},
    ]
    
    # --- 9. Financials (Enhanced with anomalies) ---
    financials = []
    for p in projects:
        project_duration_months = max(1, (p['end_date'] - p['start_date']).days / 30.0)
        months_elapsed = max(0, (date.today() - p['start_date']).days / 30.0)
        if p['health_status'] == 'Completed': months_elapsed = project_duration_months
        if months_elapsed > 0:
            for i in range(int(project_duration_months)):
                month_date = p['start_date'] + timedelta(days=i*30)
                planned_spend = p['budget_usd'] / project_duration_months
                financials.append({"project_id": p['id'], "date": month_date, "type": "Planned", "category": "R&D Opex", "amount": planned_spend * 0.6})
                financials.append({"project_id": p['id'], "date": month_date, "type": "Planned", "category": "Clinical/Reg", "amount": planned_spend * 0.2})
                financials.append({"project_id": p['id'], "date": month_date, "type": "Planned", "category": "Capex", "amount": planned_spend * 0.1})
                financials.append({"project_id": p['id'], "date": month_date, "type": "Planned", "category": "Other G&A", "amount": planned_spend * 0.1})
                if i < months_elapsed:
                    spend_factor = 1.2 if p['health_status'] == 'At Risk' else 1.0
                    actual_spend_total = planned_spend * np.random.uniform(0.9, 1.1) * spend_factor
                    if p['id'] == 'NPD-001' and i == 10: actual_spend_total += 300000 
                    financials.append({"project_id": p['id'], "date": month_date, "type": "Actuals", "category": "R&D Opex", "amount": actual_spend_total * 0.65})
                    financials.append({"project_id": p['id'], "date": month_date, "type": "Actuals", "category": "Clinical/Reg", "amount": actual_spend_total * 0.15})
                    financials.append({"project_id": p['id'], "date": month_date, "type": "Actuals", "category": "Capex", "amount": actual_spend_total * 0.1})
                    financials.append({"project_id": p['id'], "date": month_date, "type": "Actuals", "category": "Other G&A", "amount": actual_spend_total * 0.1})

    # --- 10. Time Series Data for Resource Forecasting ---
    resource_demand_history = []
    for role in ["Instrument R&D", "Software R&D", "Assay R&D", "RA/QA"]:
        for i in range(24):
            month_date = base_date + timedelta(days=i*30)
            base_demand, trend, seasonality, noise = random.randint(100, 300), i * 5, 50 * np.sin(2 * np.pi * i / 12), random.randint(-20, 20)
            demand = base_demand + trend + seasonality + noise
            resource_demand_history.append({"date": month_date, "role": role, "demand_hours": max(0, demand)})

    # <--- FIX: Corrected the return statement to use locally generated variables ---
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
        "resource_demand_history": resource_demand_history,
    }

class SPMOSessionStateManager:
    _PMO_DATA_KEY = "pmo_spmo_data_ml_v6"
    _CURRENT_DATA_VERSION = 6.0 # ML-Enhanced Overhaul

    def __init__(self):
        session_data = st.session_state.get(self._PMO_DATA_KEY)
        if not session_data or session_data.get("data_version") != self._CURRENT_DATA_VERSION:
            logger.info(f"Initializing session state with sPMO data model v{self._CURRENT_DATA_VERSION}.")
            with st.spinner("Generating Autoimmunity Division sPMO Simulation..."):
                st.session_state[self._PMO_DATA_KEY] = _create_spmo_model(self._CURRENT_DATA_VERSION)

    def get_data(self, key: str) -> Any:
        return st.session_state.get(self._PMO_DATA_KEY, {}).get(key, [])
