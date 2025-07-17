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
    """Initializes the mock data cache if it's empty."""
    if _DATA_CACHE:
        return

    base_date = date.today() - timedelta(days=730)

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
        {"name": "Klaus Schmidt", "role": "Systems Engineering", "cost_per_hour": 130, "capacity_hours_week": 40, "location": "Germany"},
        {"name": "Lena Vogel", "role": "Instrument R&D", "cost_per_hour": 115, "capacity_hours_week": 40, "location": "Germany"},
    ]
    _DATA_CACHE['pmo_team'] = [
        {"name": "John Smith", "role": "Project Manager", "performance_score": 4.5, "certification_status": "PMP, CSM", "development_path": "Agile Leadership Training"},
        {"name": "Jane Doe", "role": "Project Manager", "performance_score": 4.8, "certification_status": "PMP", "development_path": "Advanced Risk Management"},
        {"name": "Sofia Chen", "role": "Project Manager", "performance_score": 4.2, "certification_status": "PMP", "development_path": "Financial Modeling for PMs"},
        {"name": "David Lee", "role": "Program Manager", "performance_score": 4.9, "certification_status": "PgMP, PMP", "development_path": "Executive Leadership Program"},
    ]
    _DATA_CACHE['pmo_department_budget'] = {
        "year": date.today().year,
        "budget_items": [
            {"category": "Staffing", "budget": 850000, "actuals": 835000, "forecast": 855000},
            {"category": "Training & Certifications", "budget": 50000, "actuals": 45000, "forecast": 55000},
            {"category": "Tooling & Software", "budget": 75000, "actuals": 80000, "forecast": 80000},
            {"category": "Compliance & Audit Support", "budget": 25000, "actuals": 15000, "forecast": 20000},
        ]
    }
    _DATA_CACHE['process_adherence'] = [
        {"quarter": "Q1 2023", "metric": "On-Time Gate Completion", "value": 85},{"quarter": "Q2 2023", "metric": "On-Time Gate Completion", "value": 88},{"quarter": "Q3 2023", "metric": "On-Time Gate Completion", "value": 91},{"quarter": "Q4 2023", "metric": "On-Time Gate Completion", "value": 90},
        {"quarter": "Q1 2023", "metric": "RAID Log Timely Updates", "value": 75},{"quarter": "Q2 2023", "metric": "RAID Log Timely Updates", "value": 82},{"quarter": "Q3 2023", "metric": "RAID Log Timely Updates", "value": 85},{"quarter": "Q4 2023", "metric": "RAID Log Timely Updates", "value": 92},
        {"quarter": "Q1 2023", "metric": "DHF Completeness at Gate", "value": 90},{"quarter": "Q2 2023", "metric": "DHF Completeness at Gate", "value": 94},{"quarter": "Q3 2023", "metric": "DHF Completeness at Gate", "value": 95},{"quarter": "Q4 2023", "metric": "DHF Completeness at Gate", "value": 97},
    ]
    _DATA_CACHE['strategic_goals'] = [
        {"id": "SG-01", "goal": "Win High-Throughput Rheumatology Segment"},
        {"id": "SG-02", "goal": "Achieve Full IVDR Compliance"},
        {"id": "SG-03", "goal": "Reduce COGS by 15% on Aptiva Line"},
        {"id": "SG-04", "goal": "Expand Connectivity & Data Solutions"}
    ]
    
    _DATA_CACHE['projects'] = [
        {"id": "NPD-003", "name": "NextGen Aptiva Instrument", "description": "A next-generation, high-throughput instrument for the Aptiva line.", "project_type": "NPD", "phase": "Concept", "pm": "Sofia Chen", "strategic_goal_id": "SG-01", "complexity": 5, "team_size": 5, "strategic_value": 10, "risk_score": 8, "health_status": "On Track", "regulatory_path": "PMA", "budget_usd": 15000000, "actuals_usd": 100000, "pv_usd": 150000, "ev_usd": 150000, "start_date": (date.today() - timedelta(days=30)).isoformat(), "end_date": (date.today() + timedelta(days=1400)).isoformat(), "final_outcome": None},
        {"id": "NPD-001", "name": "Aptiva Celiac Disease Panel", "description": "Next-generation assay for Celiac Disease on the Aptiva platform.", "project_type": "NPD", "phase": "Development", "pm": "John Smith", "strategic_goal_id": "SG-01", "complexity": 5, "team_size": 12, "strategic_value": 9, "risk_score": 7, "health_status": "At Risk", "regulatory_path": "510(k)", "budget_usd": 5000000, "actuals_usd": 4100000, "pv_usd": 4000000, "ev_usd": 3800000, "start_date": (base_date + timedelta(days=230)).isoformat(), "end_date": (base_date + timedelta(days=960)).isoformat(), "final_outcome": None},
        {"id": "NPD-002", "name": "BIO-FLASH Connectivity Module", "description": "Middleware solution for connecting BIO-FLASH instruments to LIS systems.", "project_type": "NPD", "phase": "Verification & Validation", "pm": "Jane Doe", "strategic_goal_id": "SG-04", "complexity": 3, "team_size": 8, "strategic_value": 7, "risk_score": 4, "health_status": "On Track", "regulatory_path": "Letter to File", "budget_usd": 2500000, "actuals_usd": 1200000, "pv_usd": 1000000, "ev_usd": 1100000, "start_date": (base_date + timedelta(days=380)).isoformat(), "end_date": (base_date + timedelta(days=1110)).isoformat(), "final_outcome": None},
        {"id": "NPD-004", "name": "AI-Powered Diagnostics Module", "description": "A software module using ML to aid in result interpretation.", "project_type": "NPD", "phase": "Regulatory Approval", "pm": "David Lee", "strategic_goal_id": "SG-01", "complexity": 4, "team_size": 6, "strategic_value": 9, "risk_score": 5, "health_status": "Needs Monitoring", "regulatory_path": "De Novo", "budget_usd": 3500000, "actuals_usd": 3000000, "pv_usd": 3100000, "ev_usd": 3000000, "start_date": (base_date + timedelta(days=50)).isoformat(), "end_date": (date.today() + timedelta(days=180)).isoformat(), "final_outcome": None},
        {"id": "LCM-002", "name": "QUANTA Flash IVDR Remediation", "description": "Remediate QUANTA Flash product line to meet new IVDR requirements.", "project_type": "LCM", "phase": "Remediation", "pm": "David Lee", "strategic_goal_id": "SG-02", "complexity": 4, "team_size": 10, "strategic_value": 8, "risk_score": 6, "health_status": "Needs Monitoring", "regulatory_path": "IVDR", "budget_usd": 3000000, "actuals_usd": 2000000, "pv_usd": 1800000, "ev_usd": 1700000, "start_date": (base_date + timedelta(days=150)).isoformat(), "end_date": (base_date + timedelta(days=880)).isoformat(), "final_outcome": None},
        {"id": "COGS-001", "name": "Aptiva Reagent Kitting Automation", "description": "Implement automation in manufacturing to reduce cost of goods sold.", "project_type": "COGS", "phase": "Development", "pm": "Sofia Chen", "strategic_goal_id": "SG-03", "complexity": 2, "team_size": 6, "strategic_value": 5, "risk_score": 3, "health_status": "On Track", "regulatory_path": "N/A", "budget_usd": 1500000, "actuals_usd": 500000, "pv_usd": 450000, "ev_usd": 550000, "start_date": (base_date + timedelta(days=420)).isoformat(), "end_date": (base_date + timedelta(days=1200)).isoformat(), "final_outcome": None},
        {"id": "NPD-H01", "name": "Aptiva Hashimoto's Panel", "description": "Historical project for ML model training.", "project_type": "NPD", "phase": "Completed", "pm": "John Smith", "strategic_goal_id": "SG-01", "complexity": 4, "team_size": 10, "strategic_value": 8, "risk_score": 8, "health_status": "Completed", "regulatory_path": "510(k)", "budget_usd": 4000000, "actuals_usd": 4500000, "pv_usd": 4000000, "ev_usd": 4000000, "start_date": (base_date).isoformat(), "end_date": (base_date + timedelta(days=700)).isoformat(), "final_outcome": "Delayed"},
        {"id": "LCM-H01", "name": "BIO-FLASH Reagent Stability Update", "description": "Historical project for ML model training.", "project_type": "LCM", "phase": "Completed", "pm": "Jane Doe", "strategic_goal_id": "SG-04", "complexity": 2, "team_size": 5, "strategic_value": 6, "risk_score": 2, "health_status": "Completed", "regulatory_path": "Letter to File", "budget_usd": 800000, "actuals_usd": 750000, "pv_usd": 800000, "ev_usd": 800000, "start_date": (base_date + timedelta(days=100)).isoformat(), "end_date": (base_date + timedelta(days=400)).isoformat(), "final_outcome": "On Time"},
    ]
    
    _DATA_CACHE['dhf_documents'] = [
        {"doc_id": "DHF-N001-01", "project_id": "NPD-001", "doc_type": "Design & Development Plan", "status": "Approved", "owner": "John Smith", "gate": "Development"},
        {"doc_id": "DHF-N001-02", "project_id": "NPD-001", "doc_type": "User Needs & Requirements", "status": "Approved", "owner": "Alice Weber", "gate": "Development"},
        {"doc_id": "DHF-N001-03", "project_id": "NPD-001", "doc_type": "Risk Management File", "status": "In Review", "owner": "Diana Evans", "gate": "V&V"},
        {"doc_id": "DHF-N002-01", "project_id": "NPD-002", "doc_type": "Design & Development Plan", "status": "Approved", "owner": "Jane Doe", "gate": "Development"},
        {"doc_id": "DHF-N002-02", "project_id": "NPD-002", "doc_type": "Software Development Plan", "status": "Approved", "owner": "Bob Chen", "gate": "Development"},
        {"doc_id": "DHF-L002-01", "project_id": "LCM-002", "doc_type": "IVDR Gap Analysis", "status": "Approved", "owner": "David Lee", "gate": "Remediation"},
    ]
    _DATA_CACHE['on_market_products'] = [
        {"product_name": "Aptiva® System & Reagents", "open_capas": 3, "complaint_rate_ytd": 0.35},
        {"product_name": "QUANTA Flash® Reagents", "open_capas": 2, "complaint_rate_ytd": 0.15},
        {"product_name": "BIO-FLASH® System & Reagents", "open_capas": 1, "complaint_rate_ytd": 0.21},
    ]
    _DATA_CACHE['qms_kpis'] = { "open_capas": 8, "overdue_capas": 2, "internal_audit_findings_open": 5, "overdue_training_records": 12 }
    _DATA_CACHE['raid_logs'] = [
        {"log_id": "R-001", "project_id": "NPD-001", "type": "Risk", "description": "Key sensor supplier fails to meet quality specs.", "owner": "Henry Ford", "status": "Mitigating", "due_date": (date.today() + timedelta(days=30)).isoformat(), "probability": 4, "impact": 5},
        {"log_id": "I-001", "project_id": "LCM-002", "type": "Issue", "description": "Notified Body has requested additional clinical evidence.", "owner": "Diana Evans", "status": "Active", "due_date": (date.today() + timedelta(days=60)).isoformat()},
        {"log_id": "D-001", "project_id": "NPD-002", "type": "Decision", "description": "Proceed with TLS 1.3 for data transmission security.", "owner": "Jane Doe", "status": "Closed", "due_date": (date.today() - timedelta(days=20)).isoformat()},
    ]
    _DATA_CACHE['milestones'] = [
        {"project_id": "NPD-001", "milestone": "V&V Start", "due_date": (base_date + timedelta(days=450)).isoformat(), "status": "At Risk"},
        {"project_id": "NPD-001", "milestone": "Design Freeze", "due_date": (base_date + timedelta(days=400)).isoformat(), "status": "Completed"},
        {"project_id": "NPD-002", "milestone": "System Integration Test", "due_date": (date.today() + timedelta(days=90)).isoformat(), "status": "On Track"},
    ]
    _DATA_CACHE['allocations'] = [
        {"project_id": "NPD-001", "resource_name": "Charlie Day", "allocated_hours_week": 20}, {"project_id": "NPD-001", "resource_name": "Alice Weber", "allocated_hours_week": 40}, {"project_id": "NPD-001", "resource_name": "Bob Chen", "allocated_hours_week": 10},
        {"project_id": "NPD-002", "resource_name": "Frank Green", "allocated_hours_week": 40}, {"project_id": "NPD-002", "resource_name": "Isabel Garcia", "allocated_hours_week": 30},
        {"project_id": "LCM-002", "resource_name": "Diana Evans", "allocated_hours_week": 20}, {"project_id": "LCM-002", "resource_name": "Javier Morales", "allocated_hours_week": 40},
        {"project_id": "COGS-001", "resource_name": "Henry Ford", "allocated_hours_week": 30},
        {"project_id": "NPD-003", "resource_name": "Lena Vogel", "allocated_hours_week": 20}, {"project_id": "NPD-003", "resource_name": "Klaus Schmidt", "allocated_hours_week": 30},
        {"project_id": "NPD-004", "resource_name": "Diana Evans", "allocated_hours_week": 20}, {"project_id": "NPD-004", "resource_name": "Grace Hopper", "allocated_hours_week": 40},
    ]
    _DATA_CACHE['collaborations'] = [
        {"project_id": "NPD-001", "collaborating_entity": "R&D Center - Barcelona", "type": "Technology Transfer", "status": "Active"},
        {"project_id": "LCM-002", "collaborating_entity": "Regulatory - Germany", "type": "IVDR Submission Support", "status": "Active"},
    ]
    _DATA_CACHE['change_controls'] = [
        {"dcr_id": "DCR-24-001", "project_id": "NPD-001", "description": "Change primary antibody supplier", "status": "Pending Review"},
        {"dcr_id": "DCR-24-002", "project_id": "NPD-002", "description": "Update encryption library from v1.2 to v1.3", "status": "Approved"},
    ]
    _DATA_CACHE['traceability_matrix'] = [
        {"project_id": "NPD-001", "source": "User Need 1: Detect Celiac antibodies", "target": "Assay Req 1.1: Use tTG-IgA antigen", "value": 1},
        {"project_id": "NPD-001", "source": "Assay Req 1.1: Use tTG-IgA antigen", "target": "V&V Protocol 1.1", "value": 1},
        {"project_id": "NPD-002", "source": "User Need 1: Secure Data Tx", "target": "SW Req 1.1: Use TLS 1.3", "value": 1},
    ]
    _DATA_CACHE['phase_gate_data'] = [
        {"project_id": "NPD-H01", "gate_name": "Gate 2: Feasibility", "planned_date": (base_date + timedelta(days=180)).isoformat(), "actual_date": (base_date + timedelta(days=190)).isoformat()},
        {"project_id": "NPD-H01", "gate_name": "Gate 3: Development", "planned_date": (base_date + timedelta(days=450)).isoformat(), "actual_date": (base_date + timedelta(days=480)).isoformat()},
        {"project_id": "LCM-H01", "gate_name": "Gate 2: Feasibility", "planned_date": (base_date + timedelta(days=160)).isoformat(), "actual_date": (base_date + timedelta(days=160)).isoformat()},
    ]
    financials = []
    for p in _DATA_CACHE['projects']:
        if p['health_status'] != 'Completed':
            p_start_date, p_end_date = pd.to_datetime(p['start_date']), pd.to_datetime(p['end_date'])
            p_duration = (p_end_date - p_start_date).days
            if p_duration > 0:
                for i in range(1, 6):
                    point_date = p_start_date + timedelta(days=(p_duration / 5) * i)
                    planned_amount = p['budget_usd'] * (i / 5)
                    financials.append({"project_id": p['id'], "date": point_date.isoformat(), "type": "Planned", "amount": planned_amount})
                    if point_date.date() < date.today():
                         financials.append({"project_id": p['id'], "date": point_date.isoformat(), "type": "Actuals", "amount": p['actuals_usd'] * (i / 5) * random.uniform(0.9, 1.1)})
    _DATA_CACHE['financials'] = financials
    demand_history = []
    roles_in_pool = {res['role'] for res in _DATA_CACHE['enterprise_resources']}
    role_demand_profiles = {"Assay R&D": {"base": 160, "trend": 5},"Software R&D": {"base": 120, "trend": 3},"Instrument R&D": {"base": 100, "trend": 2},"RA/QA": {"base": 80, "trend": 4},"Clinical Affairs": {"base": 50, "trend": 1},"Operations": {"base": 70, "trend": 0},"Systems Engineering": {"base": 60, "trend": 3},}
    for role in roles_in_pool:
        profile = role_demand_profiles.get(role, {"base": 40, "trend": 1})
        for i in range(24, 0, -1):
            d = date.today() - timedelta(days=i*30)
            demand = profile['base'] + i * profile['trend'] + random.randint(-20, 20)
            demand_history.append({"date": d.isoformat(), "role": role, "demand_hours": max(0, demand)})
    _DATA_CACHE['resource_demand_history'] = demand_history

def get_projects_from_erp(): _initialize_data_cache(); return _DATA_CACHE.get('projects', [])
def get_financials_from_erp(): _initialize_data_cache(); return _DATA_CACHE.get('financials', [])
def get_pmo_budget_from_finance(): _initialize_data_cache(); return _DATA_CACHE.get('pmo_department_budget', {})
def get_dhf_from_qms(): _initialize_data_cache(); return _DATA_CACHE.get('dhf_documents', [])
def get_qms_kpis(): _initialize_data_cache(); return _DATA_CACHE.get('qms_kpis', {})
def get_on_market_products_from_qms(): _initialize_data_cache(); return _DATA_CACHE.get('on_market_products', [])
def get_traceability_from_alm(): _initialize_data_cache(); return _DATA_CACHE.get('traceability_matrix', [])
def get_process_adherence_from_alm(): _initialize_data_cache(); return _DATA_CACHE.get('process_adherence', [])
def get_enterprise_resources_from_hris(): _initialize_data_cache(); return _DATA_CACHE.get('enterprise_resources', [])
def get_pmo_team_from_hris(): _initialize_data_cache(); return _DATA_CACHE.get('pmo_team', [])
def get_allocations_from_planning_tool(): _initialize_data_cache(); return _DATA_CACHE.get('allocations', [])
def get_resource_demand_history(): _initialize_data_cache(); return _DATA_CACHE.get('resource_demand_history', [])
def get_strategic_goals(): _initialize_data_cache(); return _DATA_CACHE.get('strategic_goals', [])
def get_raid_logs(): _initialize_data_cache(); return _DATA_CACHE.get('raid_logs', [])
def get_milestones(): _initialize_data_cache(); return _DATA_CACHE.get('milestones', [])
def get_change_controls(): _initialize_data_cache(); return _DATA_CACHE.get('change_controls', [])
def get_collaborations(): _initialize_data_cache(); return _DATA_CACHE.get('collaborations', [])
def get_phase_gate_data(): _initialize_data_cache(); return _DATA_CACHE.get('phase_gate_data', [])
