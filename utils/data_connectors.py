# pmo_command_center/utils/data_connectors.py
"""
Data Connector Abstraction Layer for the sPMO Command Center.

This module simulates connections to real-time enterprise systems. In a production
environment, these functions would be replaced with actual API clients to connect
to systems like SAP (ERP), Veeva/MasterControl (QMS), Jira (ALM), and Workday (HRIS).
"""
import pandas as pd
from datetime import date, timedelta
import random
import numpy as np

# In-memory cache to simulate data persistence across the app
_DATA_CACHE = {}

def _initialize_data_cache():
    """Generates and caches the full simulated dataset if it doesn't exist."""
    if _DATA_CACHE:
        return

    base_date = date.today() - timedelta(days=730)

    # --- Strategic Goals ---
    _DATA_CACHE['strategic_goals'] = [
        {"id": "SG-01", "goal": "Win High-Throughput Rheumatology Segment", "description": "Launch new, high-value assays to capture the high-volume rheumatology testing market."},
        {"id": "SG-02", "goal": "Achieve Full IVDR Compliance", "description": "Ensure all relevant on-market products meet new European IVD regulations to maintain market access."},
        {"id": "SG-03", "goal": "Expand Clinical Utility of BIO-FLASH", "description": "Develop novel biomarkers and applications for the BIO-FLASH platform to enter new clinical areas."},
        {"id": "SG-04", "goal": "Improve Operational Efficiency & COGS", "description": "Reduce COGS and improve manufacturing throughput for key product lines like Aptiva."},
    ]

    # --- Projects (Simulating ERP Data) ---
    _DATA_CACHE['projects'] = [
        {"id": "NPD-001", "name": "Aptiva Celiac Disease Panel", "project_type": "NPD", "phase": "Development", "pm": "John Smith", "strategic_goal_id": "SG-01", "complexity": 5, "team_size": 12,
         "description": "A next-generation panel for Celiac Disease diagnosis on the Aptiva platform.", "strategic_value": 9, "risk_score": 7, "health_status": "At Risk", "regulatory_path": "510(k)",
         "budget_usd": 5000000, "actuals_usd": 4100000, "pv_usd": 3250000, "ev_usd": 3000000, "start_date": base_date + timedelta(days=230), "end_date": base_date + timedelta(days=960), "completion_pct": 65, "final_outcome": None},
        {"id": "NPD-002", "name": "BIO-FLASH Connectivity Module", "project_type": "NPD", "phase": "V&V", "pm": "Jane Doe", "strategic_goal_id": "SG-04", "complexity": 3, "team_size": 8,
         "description": "A new hardware and software module for cloud-based data integration.", "strategic_value": 7, "risk_score": 4, "health_status": "On Track", "regulatory_path": "Letter to File",
         "budget_usd": 2500000, "actuals_usd": 1200000, "pv_usd": 1000000, "ev_usd": 1100000, "start_date": base_date + timedelta(days=380), "end_date": base_date + timedelta(days=1110), "completion_pct": 40, "final_outcome": None},
        {"id": "NPD-003", "name": "NextGen Vasculitis Biomarker", "project_type": "NPD", "phase": "Feasibility", "pm": "Sofia Chen", "strategic_goal_id": "SG-03", "complexity": 5, "team_size": 10,
         "description": "A research-intensive project to develop a novel biomarker on QUANTA Flash.", "strategic_value": 8, "risk_score": 8, "health_status": "Needs Monitoring", "regulatory_path": "PMA",
         "budget_usd": 8500000, "actuals_usd": 750000, "pv_usd": 850000, "ev_usd": 700000, "start_date": base_date + timedelta(days=530), "end_date": base_date + timedelta(days=1400), "completion_pct": 10, "final_outcome": None},
        {"id": "LCM-002", "name": "QUANTA-Lyser IVDR Compliance", "project_type": "LCM", "phase": "Remediation", "pm": "David Lee", "strategic_goal_id": "SG-02", "complexity": 4, "team_size": 15,
         "description": "A large-scale remediation project to update the QUANTA-Lyser technical file.", "strategic_value": 10, "risk_score": 6, "health_status": "At Risk", "regulatory_path": "IVDR Class C",
         "budget_usd": 3200000, "actuals_usd": 2950000, "pv_usd": 3040000, "ev_usd": 2800000, "start_date": base_date + timedelta(days=290), "end_date": base_date + timedelta(days=740), "completion_pct": 95, "final_outcome": None},
        {"id": "NPD-H02", "name": "QUANTA Flash® cANCA Assay", "project_type": "NPD", "phase": "Completed", "pm": "John Smith", "strategic_goal_id": "SG-01", "complexity": 3, "team_size": 7,
         "description": "Historical assay development project.", "strategic_value": 8, "risk_score": 3, "health_status": "Completed", "regulatory_path": "510(k)",
         "budget_usd": 3000000, "actuals_usd": 2800000, "pv_usd": 3000000, "ev_usd": 3000000, "start_date": base_date, "end_date": base_date + timedelta(days=550), "completion_pct": 100, "final_outcome": "On-Time"},
    ]
    # --- DHF Documents (Simulating QMS Data) ---
    _DATA_CACHE['dhf_documents'] = [
        {"doc_id": "DHF-N001-01", "project_id": "NPD-001", "doc_type": "Design & Development Plan", "status": "Approved", "owner": "John Smith", "gate": "Development"},
        {"doc_id": "DHF-N001-02", "project_id": "NPD-001", "doc_type": "User Needs & Requirements", "status": "Approved", "owner": "John Smith", "gate": "Development"},
        {"doc_id": "DHF-N001-03", "project_id": "NPD-001", "doc_type": "Risk Management File", "status": "Approved", "owner": "Diana Evans", "gate": "V&V"},
        {"doc_id": "DHF-N001-04", "project_id": "NPD-001", "doc_type": "V&V Master Plan", "status": "Approved", "owner": "Charlie Day", "gate": "V&V"},
        {"doc_id": "DHF-N002-01", "project_id": "NPD-002", "doc_type": "Design & Development Plan", "status": "Approved", "owner": "Jane Doe", "gate": "Development"},
        {"doc_id": "DHF-N002-02", "project_id": "NPD-002", "doc_type": "Software Requirements Spec", "status": "Approved", "owner": "Bob Chen", "gate": "Development"},
        {"doc_id": "DHF-N002-03", "project_id": "NPD-002", "doc_type": "Risk Management File", "status": "In Review", "owner": "Diana Evans", "gate": "V&V"},
    ]
    # --- Resources (Simulating HRIS Data) ---
    _DATA_CACHE['resources'] = [
        {"name": "Alice Weber", "role": "Instrument R&D", "cost_per_hour": 110, "capacity_hours_week": 40},
        {"name": "Bob Chen", "role": "Software R&D", "cost_per_hour": 100, "capacity_hours_week": 40},
        {"name": "Charlie Day", "role": "Assay R&D", "cost_per_hour": 95, "capacity_hours_week": 40},
        {"name": "Diana Evans", "role": "RA/QA", "cost_per_hour": 120, "capacity_hours_week": 40},
        {"name": "Frank Green", "role": "Software R&D", "cost_per_hour": 115, "capacity_hours_week": 40},
        {"name": "Grace Hopper", "role": "Clinical Affairs", "cost_per_hour": 125, "capacity_hours_week": 40},
        {"name": "Henry Ford", "role": "Operations", "cost_per_hour": 90, "capacity_hours_week": 40},
    ]
    # --- Other Data Models ---
    _DATA_CACHE['on_market_products'] = [{"product_name": "Aptiva® System & Reagents", "open_capas": 3, "complaint_rate_ytd": 0.35}, {"product_name": "BIO-FLASH® System", "open_capas": 2, "complaint_rate_ytd": 0.22}]
    _DATA_CACHE['qms_kpis'] = {"open_capas": 8, "overdue_capas": 2}
    _DATA_CACHE['raid_logs'] = [{"log_id": "R-001", "project_id": "NPD-001", "type": "Risk", "description": "Key sensor supplier fails to meet quality specs.", "owner": "Henry Ford", "status": "Mitigating", "due_date": (date.today() + timedelta(days=30)).isoformat()}]
    _DATA_CACHE['milestones'] = [{"project_id": "NPD-001", "milestone": "V&V Start", "due_date": (base_date + timedelta(days=450)).isoformat(), "status": "At Risk"}]
    _DATA_CACHE['allocations'] = [{"project_id": "NPD-001", "resource_name": "Charlie Day", "allocated_hours_week": 20}, {"project_id": "NPD-002", "resource_name": "Bob Chen", "allocated_hours_week": 40}]
    _DATA_CACHE['collaborations'] = [{"project_id": "NPD-003", "collaborating_entity": "R&D Center - Barcelona", "type": "Technology Transfer", "status": "Active"}]
    _DATA_CACHE['change_controls'] = [{"dcr_id": "DCR-24-001", "project_id": "NPD-001", "description": "Change primary antibody supplier", "status": "Approved"}]
    _DATA_CACHE['traceability_matrix'] = [{"project_id": "NPD-002", "source": "User Need 1: Secure Data Tx", "target": "SW Req 1.1: Use TLS 1.3", "value": 1}]
    _DATA_CACHE['phase_gate_data'] = [{"project_id": "NPD-H02", "gate_name": "Gate 3: Development", "planned_date": (base_date + timedelta(days=400)).isoformat(), "actual_date": (base_date + timedelta(days=450)).isoformat()}]
    # Simulate Financials and Resource History
    financials = []
    for p in _DATA_CACHE['projects']:
        project_duration_months = max(1, (pd.to_datetime(p['end_date']) - pd.to_datetime(p['start_date'])).days / 30.0)
        for i in range(int(project_duration_months)):
            month_date = pd.to_datetime(p['start_date']) + pd.DateOffset(months=i)
            if month_date > pd.to_datetime(date.today()): continue
            planned_spend = p['budget_usd'] / project_duration_months
            actual_spend = planned_spend * np.random.uniform(0.9, 1.1)
            financials.append({"project_id": p['id'], "date": month_date.isoformat(), "type": "Actuals", "amount": actual_spend})
    _DATA_CACHE['financials'] = financials
    
    resource_demand_history = []
    for role in ["Instrument R&D", "Software R&D", "Assay R&D", "RA/QA"]:
        for i in range(24):
            month_date = base_date + timedelta(days=i*30)
            demand = 150 + i * 5 + 50 * np.sin(2 * np.pi * i / 12) + random.randint(-20, 20)
            resource_demand_history.append({"date": month_date.isoformat(), "role": role, "demand_hours": max(0, demand)})
    _DATA_CACHE['resource_demand_history'] = resource_demand_history

def get_projects_from_erp():
    """Simulates fetching project master data and financials from an ERP like SAP."""
    _initialize_data_cache()
    return _DATA_CACHE.get('projects', [])

def get_financials_from_erp():
    """Simulates fetching detailed financial transactions."""
    _initialize_data_cache()
    return _DATA_CACHE.get('financials', [])

def get_dhf_from_qms():
    """Simulates fetching DHF document statuses from a QMS like Veeva."""
    _initialize_data_cache()
    return _DATA_CACHE.get('dhf_documents', [])

def get_qms_kpis():
    """Simulates fetching high-level QMS metrics."""
    _initialize_data_cache()
    return _DATA_CACHE.get('qms_kpis', {})

def get_on_market_products_from_qms():
    """Simulates fetching on-market product quality data."""
    _initialize_data_cache()
    return _DATA_CACHE.get('on_market_products', [])

def get_traceability_from_alm():
    """Simulates fetching requirements traceability from a tool like Jira or Jama."""
    _initialize_data_cache()
    return _DATA_CACHE.get('traceability_matrix', [])

def get_resources_from_hris():
    """Simulates fetching resource data from an HRIS like Workday."""
    _initialize_data_cache()
    return _DATA_CACHE.get('resources', [])

def get_allocations_from_planning_tool():
    """Simulates fetching resource allocations."""
    _initialize_data_cache()
    return _DATA_CACHE.get('allocations', [])

def get_resource_demand_history():
    """Simulates fetching historical resource timesheet data."""
    _initialize_data_cache()
    return _DATA_CACHE.get('resource_demand_history', [])

# --- Static or less frequently updated data ---
def get_strategic_goals():
    _initialize_data_cache()
    return _DATA_CACHE.get('strategic_goals', [])

def get_raid_logs():
    _initialize_data_cache()
    return _DATA_CACHE.get('raid_logs', [])

def get_milestones():
    _initialize_data_cache()
    return _DATA_CACHE.get('milestones', [])
    
def get_change_controls():
    _initialize_data_cache()
    return _DATA_CACHE.get('change_controls', [])

def get_collaborations():
    _initialize_data_cache()
    return _DATA_CACHE.get('collaborations', [])

def get_phase_gate_data():
    _initialize_data_cache()
    return _DATA_CACHE.get('phase_gate_data', [])
