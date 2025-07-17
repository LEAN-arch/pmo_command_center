# pmo_command_center/dashboards/pmo_financials.py
"""
This module renders the PMO Departmental Financials & Budgeting dashboard.

It provides a dedicated view for the Director, PMO to manage the operational
budget of the PMO itself, including staffing, training, and tooling costs.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.pmo_session_state_manager import SPMOSessionStateManager

def render_pmo_financials_dashboard(ssm: SPMOSessionStateManager):
    """Renders the dashboard for managing the PMO's departmental budget."""
    st.header("💼 PMO Departmental Financials & Budgeting")
    st.caption("Manage the PMO's operational budget, including staffing, training, tooling, and other administrative expenses.")

    # --- Data Loading ---
    pmo_budget_data = ssm.get_data("pmo_department_budget")

    if not pmo_budget_data:
        st.warning("No PMO departmental budget data available.")
        return

    budget_year = pmo_budget_data.get("year", "N/A")
    budget_items_df = pd.DataFrame(pmo_budget_data.get("budget_items", []))

    st.subheader(f"PMO Operational Budget for {budget_year}")

    # --- High-Level KPIs ---
    if not budget_items_df.empty:
        total_budget = budget_items_df['budget'].sum()
        total_actuals = budget_items_df['actuals'].sum()
        total_forecast = budget_items_df['forecast'].sum()

        kpi_cols = st.columns(3)
        kpi_cols[0].metric("Total Annual Budget", f"${total_budget:,.0f}")
        kpi_cols[1].metric("YTD Actuals", f"${total_actuals:,.0f}")
        kpi_cols[2].metric(
            "Full Year Forecast",
            f"${total_forecast:,.0f}",
            delta=f"${(total_forecast - total_budget):,.0f} vs Budget",
            delta_color="inverse"
        )
    else:
        st.info("Budget items not loaded.")

    st.divider()

    # --- Budget vs. Actuals vs. Forecast Chart ---
    st.subheader("Budget Performance by Category")

    if not budget_items_df.empty:
        fig = go.Figure()

        fig.add_trace(go.Bar(
            y=budget_items_df['category'],
            x=budget_items_df['actuals'],
            name='YTD Actuals',
            orientation='h',
            marker=dict(color='rgba(214, 39, 40, 0.8)'),
            text=budget_items_df['actuals'].apply(lambda x: f"${x/1000:.0f}k")
        ))
        
        fig.add_trace(go.Bar(
            y=budget_items_df['category'],
            x=budget_items_df['forecast'],
            name='Full Year Forecast',
            orientation='h',
            marker=dict(color='rgba(255, 127, 14, 0.8)'),
            text=budget_items_df['forecast'].apply(lambda x: f"${x/1000:.0f}k")
        ))

        fig.add_trace(go.Bar(
            y=budget_items_df['category'],
            x=budget_items_df['budget'],
            name='Annual Budget',
            orientation='h',
            marker=dict(color='rgba(44, 160, 44, 0.6)'),
            text=budget_items_df['budget'].apply(lambda x: f"${x/1000:.0f}k")
        ))

        fig.update_layout(
            barmode='group',
            title_text="PMO Operational Spend: Budget vs. Forecast vs. Actuals",
            xaxis_title="Amount (USD)",
            yaxis_title=None,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=400,
            yaxis_autorange='reversed'
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    
    # --- Detailed Budget Table ---
    st.subheader("Detailed Budget Breakdown")
    if not budget_items_df.empty:
        budget_items_df['variance_to_budget'] = budget_items_df['forecast'] - budget_items_df['budget']
        st.dataframe(
            budget_items_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "category": "Expense Category",
                "budget": st.column_config.NumberColumn("Annual Budget", format="$%d"),
                "actuals": st.column_config.NumberColumn("YTD Actuals", format="$%d"),
                "forecast": st.column_config.NumberColumn("Full-Year Forecast", format="$%d"),
                "variance_to_budget": st.column_config.NumberColumn("Forecast Variance", format="$%d")
            }
        )
    else:
        st.info("No detailed budget items to display.")
