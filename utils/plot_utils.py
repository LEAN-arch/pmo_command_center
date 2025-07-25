"""
Contains reusable, high-level plotting functions for creating the various
dashboards in the sPMO Command Center. This module is designed to produce
elegant, insightful, and commercial-grade visualizations, including those
for machine learning model interpretation and advanced PMO analytics.
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import date

# --- Portfolio & Project Plots ---
def create_portfolio_bubble_chart(df: pd.DataFrame) -> go.Figure:
    """Creates an interactive, executive-level bubble chart to visualize the portfolio."""
    status_colors = {"On Track": "#2ca02c", "Needs Monitoring": "#ff7f0e", "At Risk": "#d62728", "Completed": "#7f7f7f"}
    fig = px.scatter(
        df, x="strategic_value", y="risk_score", size="budget_usd", color="health_status",
        hover_name="name", text="id", size_max=60, color_discrete_map=status_colors,
        custom_data=['pm', 'phase', 'budget_usd', 'risk_score', 'strategic_value', 'project_type', 'regulatory_path']
    )
    fig.update_traces(
        hovertemplate="<b>%{hover_name}</b><br>" + "--------------------<br>" +
                      "<b>PM:</b> %{customdata[0]} | <b>Phase:</b> %{customdata[1]} | <b>Type:</b> %{customdata[5]}<br>" +
                      "<b>Budget:</b> $%{customdata[2]:,.0f}<br>" + "<b>Reg. Path:</b> %{customdata[6]}<br>" +
                      "<b>Risk Score:</b> %{customdata[3]} | <b>Strategic Value:</b> %{customdata[4]}<extra></extra>"
    )
    fig.update_layout(
        title="<b>Project Portfolio: Strategic Value vs. Risk</b>",
        xaxis_title="Strategic Value (Higher is Better)", yaxis_title="Risk Score (Higher is Worse)",
        xaxis=dict(range=[0, 10.5], dtick=1), yaxis=dict(range=[0, 10.5], dtick=1),
        height=500, legend_title="Health Status"
    )
    return fig

def create_risk_contribution_plot(contribution_df: pd.DataFrame, title: str) -> go.Figure:
    """Creates an interpretable bar chart for ML risk model contributions."""
    if contribution_df is None or contribution_df.empty:
        return go.Figure().update_layout(title_text=f"No Contribution Data for {title}", xaxis_visible=False, yaxis_visible=False)
    df = contribution_df.copy()
    df['color'] = df['contribution'].apply(lambda x: '#d62728' if x > 0 else '#2ca02c') # Red for increase, green for decrease
    fig = px.bar(df.sort_values('contribution'), x='contribution', y='feature', orientation='h',
                 title=title, labels={'contribution': "Impact on Risk (Log-Odds)", 'feature': 'Risk Factor'},
                 text='contribution')
    fig.update_traces(marker_color=df['color'], texttemplate='%{text:.3f}', textposition='outside')
    fig.update_layout(showlegend=False, yaxis_title=None)
    fig.add_vline(x=0, line_width=1, line_dash="dash", line_color="black")
    return fig

# --- Financial & EVM Plots ---
def create_financial_burn_chart(df: pd.DataFrame, title: str) -> go.Figure:
    """Creates a cumulative financial burn chart (Planned vs. Actuals)."""
    if df.empty:
        return go.Figure().update_layout(title_text=f"No Financial Data for {title}", xaxis_visible=False, yaxis_visible=False)
    
    df_copy = df.copy()
    df_copy['date'] = pd.to_datetime(df_copy['date'])
    today = pd.to_datetime(date.today())
    
    # Pivot to get planned and actuals in columns, then calculate cumulative sum
    pivot_df = df_copy.pivot_table(index='date', columns='type', values='amount', aggfunc='sum').fillna(0).cumsum().reset_index()
    
    fig = go.Figure()
    # Plot Planned Burn (full duration)
    fig.add_trace(go.Scatter(x=pivot_df['date'], y=pivot_df.get('Planned', pd.Series(dtype='float64')),
                             mode='lines', name='Planned Burn (BAC)', line=dict(color='grey', dash='dash')))
    
    # Plot Actual Burn (only up to today)
    actuals_to_date = pivot_df[pivot_df['date'] <= today]
    fig.add_trace(go.Scatter(x=actuals_to_date['date'], y=actuals_to_date.get('Actuals', pd.Series(dtype='float64')),
                             mode='lines', name='Actual Burn (AC)', line=dict(color='crimson', width=3)))
    
    fig.update_layout(
        title=f"<b>{title}</b>",
        xaxis_title="Date", yaxis_title="Cumulative Spend (USD)", yaxis_tickformat='$,.0f',
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    return fig

def create_evm_performance_chart(df: pd.DataFrame) -> go.Figure:
    """Creates an enhanced bar chart visualizing CPI and SPI for active projects."""
    df_filtered = df[df['health_status'] != 'Completed'].copy()
    if df_filtered.empty:
        return go.Figure().update_layout(title_text="No Active Projects for EVM Analysis", xaxis_visible=False, yaxis_visible=False)

    df_melted = df_filtered.melt(
        id_vars=['name', 'pm', 'budget_usd', 'pv_usd', 'ev_usd', 'actuals_usd'],
        value_vars=['cpi', 'spi'], var_name='metric', value_name='value'
    )
    
    fig = px.bar(
        df_melted, x='name', y='value', color='value',
        color_continuous_scale='RdYlGn', color_continuous_midpoint=1.0,
        facet_col='metric', text='value',
        custom_data=['name', 'pm', 'budget_usd', 'pv_usd', 'ev_usd', 'actuals_usd', 'metric', 'value']
    )
    fig.update_traces(
        texttemplate='%{value:.2f}', textposition='outside',
        hovertemplate="<b>%{customdata[0]}</b><br>" + "--------------------<br>" +
                      "<b>Project Manager:</b> %{customdata[1]}<br>" +
                      "<b>Budget (BAC):</b> $%{customdata[2]:,.0f}<br>" + "--------------------<br>" +
                      "<b>%{customdata[6].upper()}: %{customdata[7]:.2f}</b><br>" +
                      "Planned Value (PV): $%{customdata[3]:,.0f}<br>" + "Earned Value (EV): $%{customdata[4]:,.0f}<br>" +
                      "Actual Cost (AC): $%{customdata[5]:,.0f}<extra></extra>"
    )
    fig.add_hline(y=1.0, line_dash="dash", line_color="black", line_width=2)
    fig.update_layout(
        title_text="<b>Project Performance Analysis (CPI & SPI)</b>",
        yaxis_title="Performance Index (> 1.0 is Favorable)", xaxis_title=None,
        coloraxis_showscale=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500,
    )
    fig.update_yaxes(range=[0.7, 1.3])
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    return fig

# --- Resource & Capacity Plots ---
def create_resource_heatmap(pivot_df: pd.DataFrame, utilization_df: pd.DataFrame) -> go.Figure:
    """Creates a heatmap of resource allocations, optimized for performance."""
    # OPTIMIZATION: Create a dictionary for fast lookups instead of searching df in a loop.
    util_map = pd.Series(utilization_df.utilization_pct.values, index=utilization_df.name).to_dict()

    hover_text = []
    for r_name in pivot_df.index:
        row_text = []
        util_pct = util_map.get(r_name, 0)
        for p_name in pivot_df.columns:
            alloc_hours = pivot_df.loc[r_name, p_name]
            row_text.append(f"<b>{r_name} on {p_name}</b><br>Hours: {alloc_hours}<br>Total Utilization: {util_pct:.0f}%")
        hover_text.append(row_text)
        
    fig = go.Figure(data=go.Heatmap(
        z=pivot_df.values, x=pivot_df.columns, y=pivot_df.index, colorscale='Reds',
        hovertemplate='%{customdata}<extra></extra>', customdata=hover_text,
        text=pivot_df.values.round(0), texttemplate="%{text}"
    ))
    fig.update_layout(
        title="<b>Resource Allocation Heatmap (Hours per Week)</b>",
        xaxis_title="Project ID", yaxis_title="Resource", height=500, yaxis_autorange='reversed'
    )
    return fig

def create_capacity_plan_chart(demand_df: pd.DataFrame, capacity_df: pd.Series, role: str) -> go.Figure:
    """Creates a time-series chart for forecasted demand vs. current capacity."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=demand_df['ds'], y=demand_df['yhat'], mode='lines', name='Forecasted Demand', line=dict(color='crimson', dash='dash')))
    fig.add_trace(go.Scatter(x=demand_df['ds'], y=[capacity_df.get(role, 0)]*len(demand_df), mode='lines', name='Current Capacity', line=dict(color='grey')))
    fig.update_layout(title=f"<b>Capacity Plan: Forecasted Demand vs. Capacity for {role}</b>",
                      xaxis_title="Date", yaxis_title="Required Hours per Month",
                      legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    return fig

# --- Compliance & Governance Plots ---
def create_dhf_completeness_chart(df: pd.DataFrame) -> go.Figure:
    """Creates a horizontal bar chart for DHF completeness."""
    fig = px.bar(
        df.sort_values('completeness_pct'),
        x='completeness_pct', y='name', orientation='h',
        title='DHF Completeness per Project',
        labels={'completeness_pct': 'Completeness (%)', 'name': 'Project'},
        text='completeness_pct'
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='inside', marker_color='#1f77b4')
    fig.update_layout(xaxis=dict(range=[0, 100]), yaxis_title=None)
    return fig

def create_traceability_sankey(df: pd.DataFrame) -> go.Figure:
    """Creates a Sankey diagram for requirements traceability."""
    if df.empty:
        return go.Figure().update_layout(title_text="No Traceability Data for this Project", xaxis_visible=False, yaxis_visible=False)
    all_nodes = pd.unique(df[['source', 'target']].values.ravel('K'))
    node_map = {node: i for i, node in enumerate(all_nodes)}
    fig = go.Figure(data=[go.Sankey(
        node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=all_nodes),
        link=dict(
            source=df['source'].map(node_map),
            target=df['target'].map(node_map),
            value=df['value']
        )
    )])
    fig.update_layout(title_text="<b>Requirements Traceability Flow</b>", font_size=10)
    return fig

def create_gate_variance_plot(df: pd.DataFrame) -> go.Figure:
    """Creates a bar chart showing the average delay for each phase gate."""
    if df.empty:
        return go.Figure().update_layout(
            title_text="No completed gates to analyze.", xaxis_visible=False, yaxis_visible=False,
            annotations=[dict(text="No Data", xref="paper", yref="paper", showarrow=False, font=dict(size=20))]
        )
    df_copy = df.copy()
    df_copy['planned_date'] = pd.to_datetime(df_copy['planned_date'])
    df_copy['actual_date'] = pd.to_datetime(df_copy['actual_date'])
    df_filtered = df_copy.dropna(subset=['actual_date']).copy()
    if df_filtered.empty:
        return go.Figure().update_layout(
            title_text="No completed gates to analyze.", xaxis_visible=False, yaxis_visible=False,
            annotations=[dict(text="No Data", xref="paper", yref="paper", showarrow=False, font=dict(size=20))]
        )
    df_filtered['variance_days'] = (df_filtered['actual_date'] - df_filtered['planned_date']).dt.days
    avg_variance = df_filtered.groupby('gate_name')['variance_days'].mean().reset_index().sort_values('variance_days')
    fig = px.bar(
        avg_variance, x='gate_name', y='variance_days',
        title='Average Gate Schedule Variance (Actual vs. Planned)',
        labels={'gate_name': 'Phase Gate', 'variance_days': 'Average Variance (Days)'},
        color='variance_days', color_continuous_scale='RdYlGn_r', text='variance_days'
    )
    fig.update_traces(texttemplate='%{text}d', textposition='outside')
    fig.update_layout(coloraxis_showscale=False, xaxis={'categoryorder':'total descending'})
    fig.add_hline(y=0, line_width=2, line_dash="dash", line_color="black")
    return fig

def create_project_cluster_plot(df: pd.DataFrame, x_axis: str, y_axis: str) -> go.Figure:
    """Creates a scatter plot for visualizing project clusters (archetypes)."""
    fig = px.scatter(
        df, x=x_axis, y=y_axis, color='cluster', symbol='project_type', hover_name='name',
        title='Project Archetypes Identified by Clustering', labels={'cluster': 'Project Archetype'}
    )
    fig.update_traces(marker=dict(size=12, line=dict(width=1, color='DarkSlateGrey')))
    return fig
