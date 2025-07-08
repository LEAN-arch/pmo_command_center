# pmo_command_center/utils/plot_utils.py
"""
Contains reusable, high-level plotting functions for creating the various
dashboards in the sPMO Command Center.
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_portfolio_bubble_chart(df: pd.DataFrame) -> go.Figure:
    """Creates an interactive bubble chart for the project portfolio."""
    status_colors = {"On Track": "#2ca02c", "Needs Monitoring": "#ff7f0e", "At Risk": "#d62728", "Completed": "#7f7f7f"}
    fig = px.scatter(
        df,
        x="strategic_value",
        y="risk_score",
        size="budget_usd",
        color="health_status",
        hover_name="name",
        text="id",
        size_max=60,
        color_discrete_map=status_colors,
        custom_data=['pm', 'phase', 'budget_usd', 'risk_score', 'strategic_value', 'project_type', 'regulatory_path']
    )
    fig.update_traces(
        hovertemplate="<b>%{hover_name}</b><br>" +
                      "--------------------<br>" +
                      "<b>PM:</b> %{customdata[0]} | <b>Phase:</b> %{customdata[1]} | <b>Type:</b> %{customdata[5]}<br>" +
                      "<b>Budget:</b> $%{customdata[2]:,.0f}<br>" +
                      "<b>Reg. Path:</b> %{customdata[6]}<br>" +
                      "<b>Risk Score:</b> %{customdata[3]} | <b>Strategic Value:</b> %{customdata[4]}<extra></extra>"
    )
    fig.update_layout(
        title="<b>Project Portfolio: Strategic Value vs. Risk</b>",
        xaxis_title="Strategic Value (Higher is Better)",
        yaxis_title="Risk Score (Higher is Worse)",
        xaxis=dict(range=[0, 10.5], dtick=1),
        yaxis=dict(range=[0, 10.5], dtick=1),
        height=500,
        legend_title="Health Status"
    )
    return fig

def create_resource_heatmap(df: pd.DataFrame, utilization_df: pd.DataFrame) -> go.Figure:
    """Creates a heatmap of resource allocation, colored by utilization."""
    pivot_df = df.pivot(index='resource_name', columns='project_id', values='allocated_hours_week').fillna(0)
    
    hover_text = []
    for r_name in pivot_df.index:
        row_text = []
        util_pct = utilization_df.loc[utilization_df['name'] == r_name, 'utilization_pct'].iloc[0]
        for p_name in pivot_df.columns:
            alloc_hours = pivot_df.loc[r_name, p_name]
            row_text.append(f"<b>{r_name} on {p_name}</b><br>Hours: {alloc_hours}<br>Total Utilization: {util_pct:.0f}%")
        hover_text.append(row_text)

    fig = go.Figure(data=go.Heatmap(
        z=pivot_df.values,
        x=pivot_df.columns,
        y=pivot_df.index,
        colorscale='Reds',
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover_text
    ))

    fig.update_layout(
        title="<b>Resource Allocation Heatmap (Hours per Week)</b>",
        xaxis_title="Project ID",
        yaxis_title="Resource",
        height=500
    )
    return fig

def create_gate_variance_plot(df: pd.DataFrame) -> go.Figure:
    """Creates a bar chart showing the variance between planned and actual gate dates."""
    df['planned_date'] = pd.to_datetime(df['planned_date'])
    df['actual_date'] = pd.to_datetime(df['actual_date'])
    df_filtered = df.dropna(subset=['actual_date'])

    if df_filtered.empty:
        fig = go.Figure().update_layout(
            title="No completed gates to analyze.",
            xaxis_visible=False, yaxis_visible=False,
            annotations=[dict(text="No Data", xref="paper", yref="paper", showarrow=False, font=dict(size=20))]
        )
        return fig

    df_filtered['variance_days'] = (df_filtered['actual_date'] - df_filtered['planned_date']).dt.days
    avg_variance = df_filtered.groupby('gate_name')['variance_days'].mean().reset_index().sort_values('variance_days')

    fig = px.bar(
        avg_variance,
        x='gate_name',
        y='variance_days',
        title='Average Gate Schedule Variance (Actual vs. Planned)',
        labels={'gate_name': 'Phase Gate', 'variance_days': 'Average Variance (Days)'},
        color='variance_days',
        color_continuous_scale='RdYlGn_r',
        text='variance_days'
    )
    fig.update_traces(texttemplate='%{text}d', textposition='outside')
    fig.update_layout(
        coloraxis_showscale=False,
        xaxis={'categoryorder':'total descending'}
    )
    fig.add_hline(y=0, line_width=2, line_dash="dash", line_color="black")
    return fig

def create_financial_burn_chart(df: pd.DataFrame, title: str) -> go.Figure:
    """Creates a financial burn-down/up chart for a project or portfolio."""
    df['date'] = pd.to_datetime(df['date'])
    
    # Ensure we only plot up to today for actuals
    today = pd.to_datetime(date.today())
    actuals_df = df[df['type'] == 'Actuals'].copy()
    actuals_df = actuals_df[actuals_df['date'] <= today]
    
    pivot_planned = df[df['type'] == 'Planned'].groupby('date')['amount'].sum().cumsum().reset_index()
    pivot_actuals = actuals_df.groupby('date')['amount'].sum().cumsum().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=pivot_planned['date'], y=pivot_planned['amount'],
        mode='lines', name='Planned Burn', line=dict(color='grey', dash='dash')
    ))
    fig.add_trace(go.Scatter(
        x=pivot_actuals['date'], y=pivot_actuals['amount'],
        mode='lines', name='Actual Burn', line=dict(color='crimson', width=3)
    ))

    fig.update_layout(
        title=f"<b>{title}</b>",
        xaxis_title="Date",
        yaxis_title="Cumulative Spend (USD)",
        yaxis_tickformat='$,.0f',
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    return fig
