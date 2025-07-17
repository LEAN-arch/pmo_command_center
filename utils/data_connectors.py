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

_DATA_CACHE = {}

def _initialize_data_cache():
    if _DATA_CACHE:
        return

    base_date = date.today() - timedelta(days=730)

    # --- Enterprise-Wide Resource Pool (Simulating HRIS Data) ---
    _DATA_CACHE['enterprise_resources'] = [
        {"name": "Alice Weber", "role": "Instrument R&D", "cost_per_hour": 110, "capacity_hours_week": 40, "location": "San Diego"},
        {"name": "Bob Chen", "role": "Software R&D", "cost_per_hour": 100, "capacity_hours_week": 40, "location": "San Diego"},
        {"name": "Charlie Day", "role": "Assay R&D", "cost_per_hour": 95, "capacity_hours_week": 40, "location": "San Diego"},
        {"name": "Diana Evans", "role": "RA/QA", "cost_per_hour": 120, "capacity_hours_week": 40, "location": "San Diego"},
        {"name": "Frank Green", "role": "Software R&D", "cost_per_hour": 115, "capacity_hours_week": 40, "location": "San Diego"},
        {"name": "Grace Hopper", "role": "Clinical Affairs", "cost_per_hour": 125, "capacity_hours_week": 40, "location": "San Diego"},
        {"name": "Henry Ford", "role": "Operations", "cost_per_hour": 90, "capacity_hours_week": 40, "location": "San Diego"},
        {"name": "Isabel Garcia", "role": "Software R&D", "cost_per_hour": 105, "capacity_hours_week": 40, "location": "Barcelona"},
        {"name": "Javier Morales", "role": "Assay R&D", "cost_per_hour": 90, "capacity_hours_week": 40, "location": "Barcelona"},
    ]

    # --- PMO Team Management Data (Simulating HRIS/Performance Tool) ---
    _DATA_CACHE['pmo_team'] = [
        {"name": "John Smith", "role": "Project Manager", "performance_score": 4.5, "certification_status": "PMP, CSM", "development_path": "Agile Leadership Training", "current_assignments": "NPD-001"},
        {"name": "Jane Doe", "role": "Project Manager", "performance_score": 4.8, "certification_status": "PMP", "development_path": "Advanced Risk Management", "current_assignments": "NPD-002"},
        {"name": "Sofia Chen", "role": "Project Manager", "performance_score": 4.2, "certification_status": "PMP", "development_path": "Financial Modeling for PMs", "current_assignments": "NPD-003"},
        {"name": "David Lee", "role": "Program Manager", "performance_score": 4.9, "certification_status": "PgMP, PMP", "development_path": "Executive Leadership Program", "current_assignments": "LCM-002"},
    ]

    # --- PMO Departmental Budget (Simulating Finance System) ---
    _DATA_CACHE['pmo_department_budget'] = {
        "year": date.today().year,
        "budget_items": [
            {"category": "Staffing", "budget": 850000, "actuals": 835000, "forecast": 855000},
            {"category": "Training & Certifications", "budget": 50000, "actuals": 45000, "forecast": 55000},
            {"category": "Tooling & Software", "budget": 75000, "actuals": 80000, "forecast": 80000},
            {"category": "Compliance & Audit Support", "budget": 25000, "actuals": 15000, "forecast": 20000},
        ]
    }

    # --- Process Adherence Metrics (Simulating Jira/QMS) ---
    _DATA_CACHE['process_adherence'] = [
        {"quarter": "Q1", "metric": "On-Time Gate Completion", "value": 85},
        {"quarter": "Q2", "metric": "On-Time Gate Completion", "value": 88},
        {"quarter": "Q1", "metric": "RAID Log Timely Updates", "value": 75},
        {"quarter": "Q2", "metric": "RAID Log Timely Updates", "value": 82},
        {"quarter": "Q1", "metric": "DHF Completeness at Gate", "value": 90},
        {"quarter": "Q2", "metric": "DHF Completeness at Gate", "value": 94},
    ]

    # --- All other data models from previous version ---
    # (Copied here for completeness)
    _DATA_CACHE['strategic_goals'] = [{"id": "SG-01", "goal": "Win High-Throughput Rheumatology Segment"}, {"id": "SG-02", "goal": "Achieve Full IVDR Compliance"}]
    _DATA_CACHE['projects'] = [{"id": "NPD-001", "name": "Aptiva Celiac Disease Panel", "project_type": "NPD", "phase": "Development", "pm": "John Smith", "strategic_goal_id": "SG-01", "complexity": 5, "team_size": 12, "strategic_value": 9, "risk_score": 7, "health_status": "At Risk", "regulatory_path": "510(k)", "budget_usd": 5000000, "actuals_usd": 4100000, "pv_usd": 3250000, "ev_usd": 3000000, "start_date": base_date + timedelta(days=230), "end_date": base_date + timedelta(days=960), "final_outcome": None}, {"id": "NPD-002", "name": "BIO-FLASH Connectivity Module", "project_type": "NPD", "phase": "V&V", "pm": "Jane Doe", "strategic_goal_id": "SG-04", "complexity": 3, "team_size": 8, "strategic_value": 7, "risk_score": 4, "health_status": "On Track", "regulatory_path": "Letter to File", "budget_usd": 2500000, "actuals_usd": 1200000, "pv_usd": 1000000, "ev_usd": 1100000, "start_date": base_date + timedelta(days=380), "end_date": base_date + timedelta(days=1110), "final_outcome": None}]
    _DATA_CACHE['dhf_documents'] = [{"doc_id": "DHF-N001-01", "project_id": "NPD-001", "doc_type": "Design & Development Plan", "status": "Approved", "owner": "John Smith", "gate": "Development"}, {"doc_id": "DHF-N001-03", "project_id": "NPD-001", "doc_type": "Risk Management File", "status": "Approved", "owner": "Diana Evans", "gate": "V&V"}]
    _DATA_CACHE['on_market_products'] = [{"product_name": "Aptiva® System & Reagents", "open_capas": 3, "complaint_rate_ytd": 0.35}]
    _DATA_CACHE['qms_kpis'] = {"open_capas": 8, "overdue_capas": 2}
    _DATA_CACHE['raid_logs'] = [{"log_id": "R-001", "project_id": "NPD-001", "type": "Risk", "description": "Key sensor supplier fails to meet quality specs.", "owner": "Henry Ford", "status": "Mitigating", "due_date": (date.today() + timedelta(days=30)).isoformat()}]
    _DATA_CACHE['milestones'] = [{"project_id": "NPD-001", "milestone": "V&V Start", "due_date": (base_date + timedelta(days=450)).isoformat(), "status": "At Risk"}]
    _DATA_CACHE['allocations'] = [{"project_id": "NPD-001", "resource_name": "Charlie Day", "allocated_hours_week": 20}]
    _DATA_CACHE['collaborations'] = [{"project_id": "NPD-001", "collaborating_entity": "R&D Center - Barcelona", "type": "Technology Transfer", "status": "Active"}]
    _DATA_CACHE['change_controls'] = [{"dcr_id": "DCR-24-001", "project_id": "NPD-001", "description": "Change primary antibody supplier", "status": "Approved"}]
    _DATA_CACHE['traceability_matrix'] = [{"project_id": "NPD-001", "source": "User Need 1: Secure Data Tx", "target": "SW Req 1.1: Use TLS 1.3", "value": 1}]
    _DATA_CACHE['phase_gate_data'] = [{"project_id": "NPD-001", "gate_name": "Gate 2: Feasibility", "planned_date": (base_date + timedelta(days=180)).isoformat(), "actual_date": (base_date + timedelta(days=190)).isoformat()}]
    _DATA_CACHE['financials'] = [{"project_id": "NPD-001", "date": (base_date + timedelta(days=240)).isoformat(), "type": "Actuals", "amount": 200000}]
    _DATA_CACHE['resource_demand_history'] = [{"date": base_date.isoformat(), "role": "Assay R&D", "demand_hours": 160}]

# --- Connector Functions ---

def get_projects_from_erp():
    _initialize_data_cache(); return _DATA_CACHE.get('projects', [])

def get_financials_from_erp():
    _initialize_data_cache(); return _DATA_CACHE.get('financials', [])

def get_pmo_budget_from_finance():
    _initialize_data_cache(); return _DATA_CACHE.get('pmo_department_budget', {})

def get_dhf_from_qms():
    _initialize_data_cache(); return _DATA_CACHE.get('dhf_documents', [])

def get_qms_kpis():
    _initialize_data_cache(); return _DATA_CACHE.get('qms_kpis', {})

def get_on_market_products_from_qms():
    _initialize_data_cache(); return _DATA_CACHE.get('on_market_products', [])

def get_traceability_from_alm():
    _initialize_data_cache(); return _DATA_CACHE.get('traceability_matrix', [])

def get_process_adherence_from_alm():
    _initialize_data_cache(); return _DATA_CACHE.get('process_adherence', [])

def get_enterprise_resources_from_hris():
    _initialize_data_cache(); return _DATA_CACHE.get('enterprise_resources', [])

def get_pmo_team_from_hris():
    _initialize_data_cache(); return _DATA_CACHE.get('pmo_team', [])

def get_allocations_from_planning_tool():
    _initialize_data_cache(); return _DATA_CACHE.get('allocations', [])

def get_resource_demand_history():
    _initialize_data_cache(); return _DATA_CACHE.get('resource_demand_history', [])

def get_strategic_goals():
    _initialize_data_cache(); return _DATA_CACHE.get('strategic_goals', [])

def get_raid_logs():
    _initialize_data_cache(); return _DATA_CACHE.get('raid_logs', [])

def get_milestones():
    _initialize_data_cache(); return _DATA_CACHE.get('milestones', [])
    
def get_change_controls():
    _initialize_data_cache(); return _DATA_CACHE.get('change_controls', [])

def get_collaborations():
    _initialize_data_cache(); return _DATA_CACHE.get('collaborations', [])

def get_phase_gate_data():
    _initialize_data_cache(); return _DATA_CACHE.get('phase_gate_data', [])
