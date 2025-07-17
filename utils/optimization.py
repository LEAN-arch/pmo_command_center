"""
Portfolio Optimization Engine for the sPMO Command Center.

This module contains the core logic for solving the portfolio selection problem
using linear programming. It uses the PuLP library to recommend an optimal set
of projects based on strategic objectives and resource/budget constraints.
"""
import pandas as pd
from pulp import LpProblem, LpVariable, lpSum, LpMaximize, LpMinimize, PULP_CBC_CMD

def optimize_portfolio(
    projects_df: pd.DataFrame,
    allocations_df: pd.DataFrame,
    resources_df: pd.DataFrame,
    constraints: dict,
    objective: str
) -> (dict, pd.DataFrame):
    """
    Selects the optimal portfolio of projects using linear programming.

    Args:
        projects_df: DataFrame of candidate projects. Must include 'id', 'budget_usd', 
                     'strategic_value', and 'risk_score'.
        allocations_df: DataFrame of resource allocations. Must include 'project_id',
                        'resource_name', and 'allocated_hours_week'.
        resources_df: DataFrame of available resources. Must include 'name' and 'role'.
        constraints: A dictionary with 'max_budget' and 'resource_constraints' (a dict of role: max_hours).
        objective: The goal of the optimization ('Maximize Strategic Value' or 'Minimize Risk').

    Returns:
        A tuple containing:
        - A dictionary with the results of the optimization (e.g., total value, budget, status).
        - A DataFrame of the selected projects.
    """
    if projects_df.empty:
        return {"status": "No projects available to optimize"}, pd.DataFrame()

    # 1. Define the optimization problem
    if objective == 'Maximize Strategic Value':
        prob = LpProblem("Portfolio_Optimization_Maximize_Value", LpMaximize)
    else: # Minimize Risk
        prob = LpProblem("Portfolio_Optimization_Minimize_Risk", LpMinimize)

    # 2. Define Decision Variables
    # A binary variable for each project: 1 if selected, 0 if not.
    project_ids = projects_df['id'].tolist()
    project_vars = LpVariable.dicts("Project", project_ids, 0, 1, 'Binary')

    # 3. Set the Objective Function
    if objective == 'Maximize Strategic Value':
        # Sum of (strategic_value * project_variable) for all projects
        obj_func = lpSum([projects_df.loc[projects_df['id'] == i, 'strategic_value'].iloc[0] * project_vars[i] for i in project_ids])
        prob += obj_func
    else: # Minimize Risk
        # Sum of (risk_score * project_variable) for all projects
        obj_func = lpSum([projects_df.loc[projects_df['id'] == i, 'risk_score'].iloc[0] * project_vars[i] for i in project_ids])
        prob += obj_func
        
    # 4. Add Constraints
    # Budget Constraint
    max_budget = constraints.get('max_budget')
    if max_budget is not None and max_budget > 0:
        prob += lpSum([projects_df.loc[projects_df['id'] == i, 'budget_usd'].iloc[0] * project_vars[i] for i in project_ids]) <= max_budget, "Budget_Constraint"

    # Resource Constraints
    resource_constraints = constraints.get('resource_constraints', {})
    if resource_constraints and not allocations_df.empty and not resources_df.empty:
        # Merge allocations with resource roles for easy lookup
        alloc_res_df = pd.merge(allocations_df, resources_df[['name', 'role']], left_on='resource_name', right_on='name')
        
        for role, max_hours in resource_constraints.items():
            if max_hours is not None and max_hours > 0:
                # Get all allocations for the current role
                role_allocations = alloc_res_df[alloc_res_df['role'] == role]
                if not role_allocations.empty:
                    # Sum of (allocated_hours * project_variable) for the given role must be <= max_hours
                    prob += lpSum([
                        role_allocations.loc[role_allocations['project_id'] == i, 'allocated_hours_week'].sum() * project_vars[i]
                        for i in project_ids if i in role_allocations['project_id'].values
                    ]) <= max_hours, f"Resource_Constraint_{role.replace(' ', '_')}"

    # 5. Solve the problem
    # Using the default CBC solver included with PuLP. It's fast and requires no external installation.
    prob.solve(PULP_CBC_CMD(msg=0)) 

    # 6. Extract and Return Results
    selected_project_ids = [var.name.split('_')[1] for var in prob.variables() if var.varValue == 1]
    
    if not selected_project_ids:
        return {"status": "Infeasible: No projects could be selected under the given constraints."}, pd.DataFrame()
        
    selected_projects_df = projects_df[projects_df['id'].isin(selected_project_ids)].copy()

    # Calculate final portfolio metrics
    total_value = selected_projects_df['strategic_value'].sum()
    total_risk = selected_projects_df['risk_score'].mean() if not selected_projects_df.empty else 0
    total_budget_used = selected_projects_df['budget_usd'].sum()
    
    results_summary = {
        "status": prob.status, # Should be 1 (Optimal)
        "objective_value": prob.objective.value(),
        "total_strategic_value": total_value,
        "average_portfolio_risk": total_risk,
        "total_budget_used": total_budget_used,
        "num_projects_selected": len(selected_project_ids)
    }

    return results_summary, selected_projects_df
