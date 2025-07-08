# pmo_command_center/utils/plot_utils.py
"""
Contains reusable, high-level plotting functions for creating the various
dashboards in the sPMO Command Center. This module is designed to produce
elegant, insightful, and commercial-grade visualizations, including those
for machine learning model interpretation.
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import date

def create_portfolio_bubble_chart(df: pd.DataFrame) -> go.Figure:
    """Creates an interactive bubble chart for the project portfolio."""
    status_colors = {"On Track": "#2ca02c", "Needs Monitoring": "#ff7f0e", "At Risk": "#d62728", "Completed": "#7f7f7f"}
    fig = px.scatter(df, x="strategic_value", y="risk_score", size="budget_usd", color="health_status",
                     hover_name="name", text="id", size_max=60, color_discrete_map=status_colors,
                     custom_data=['pm', 'phase', 'budget_usd', 'risk_score', 'strategic_value', 'project_type', 'regulatory_path'])
    fig.update_traces(
        hovertemplate="<b>%{hover_name}</b><br>" + "--------------------<br>" +
                      "<b>PM:</b> %{customdata[0]} | <b>Phase:</b> %{customdata[1]} | <b>Type:</b> %{customdata[5]}<br>" +
                      "<b>Budget:</b> $%{customdata[2]:,.0f}<br>" + "<b>Reg. Path:</b> %{customdata[6]}<br>" +
                      "<b>Risk Score:</b> %{customdata[3]} | <b>Strategic Value:</b> %{customdata[4]}<extra></extra>")
    fig.update_layout(title="<b>Project Portfolio: Strategic Value vs. Risk</b>", xaxis_title="Strategic Value (Higher is Better)",
                      yaxis_title="Risk Score (Higher is Worse)", xaxis=dict(range=[0, 10.5], dtick=1),
                      yaxis=dict(range=[0, 10.5], dtick=1), height=500, legend_title="Health Status")
    return fig

def create_gate_variance_plot(df: pd.DataFrame) -> go.Figure:
    """Creates a bar chart showing the variance between planned and actual gate dates."""
    df = df.copy()
    df['planned_date'] = pd.to_datetime(df['planned_date'])
    df['actual_date'] = pd.to_datetime(df['actual_date'])
    df_filtered = df.dropna(subset=['actual_date'])
    if df_filtered.empty:
        return go.Figure().update_layout(title="No completed gates to analyze.", xaxis_visible=False, yaxis_visible=False,
                                         annotations=[dict(text="No Data", xref="paper", yref="paper", showarrow=False, font=dict(size=20))])
    df_filtered['variance_days'] = (df_filtered['actual_date'] - df_filtered['planned_date']).dt.days
    avg_variance = df_filtered.groupby('gate_name')['variance_days'].mean().reset_index().sort_values('variance_days')
    fig = px.bar(avg_variance, x='gate_name', y='variance_days', title='Average Gate Schedule Variance (Actual vs. Planned)',
                 labels={'gate_name': 'Phase Gate', 'variance_days': 'Average Variance (Days)'},
                 color='variance_days', color_continuous_scale='RdYlGn_r', text='variance_days')
    fig.update_traces(texttemplate='%{text}d', textposition='outside')
    fig.update_layout(coloraxis_showscale=False, xaxis={'categoryorder':'total descending'})
    fig.add_hline(y=0, line_width=2, line_dash="dash", line_color="black")
    return fig

def create_financial_burn_chart(df: pd.DataFrame, title: str, anomaly_dates: list = None) -> go.Figure:
    """Creates a financial burn chart, with optional markers for anomalies."""
    if df.empty:
        return go.Figure().update_layout(title_text=f"No Financial Data for {title}", xaxis_visible=False, yaxis_visible=False)
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    today = pd.to_datetime(date.today())
    pivot_df = df.pivot_table(index='date', columns='type', values='amount', aggfunc='sum').fillna(0).cumsum().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=pivot_df['date'], y=pivot_df.get('Planned', pd.Series(dtype='float64')),
                             mode='lines', name='Planned Burn', line=dict(color='grey', dash='dash')))
    actuals_to_date = pivot_df[pivot_df['date'] <= today]
    fig.add_trace(go.Scatter(x=actuals_to_date['date'], y=actuals_to_date.get('Actuals', pd.Series(dtype='float64')),
                             mode='lines', name='Actual Burn', line=dict(color='crimson', width=3)))
    if anomaly_dates:
        anomaly_df = actuals_to_date[actuals_to_date['date'].isin(pd.to_datetime(anomaly_dates))]
        fig.add_trace(go.Scatter(x=anomaly_df['date'], y=anomaly_df['Actuals'], mode='markers', name='Anomaly Detected',
                                 marker=dict(symbol='x', color='purple', size=12, line=dict(width=2))))
    fig.update_layout(title=f"<b>{title}</b>", xaxis_title="Date", yaxis_title="Cumulative Spend (USD)",
                      yaxis_tickformat='$,.0f', legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    return fig

def create_risk_contribution_plot(contribution_df: pd.DataFrame, title: str) -> go.Figure:
    """Creates an interpretable bar chart for ML risk model contributions."""
    contribution_df['color'] = contribution_df['contribution'].apply(lambda x: '#d62728' if x > 0 else '#2ca02c') # Red for risk, green for safety
    fig = px.bar(contribution_df.sort_values('contribution'), x='contribution', y='feature', orientation='h',
                 title=title, labels={'contribution': "Impact on Risk (Log-Odds)", 'feature': 'Risk Factor'},
                 text='contribution')
    fig.update_traces(marker_color=contribution_df['color'], texttemplate='%{text:.3f}', textposition='outside')
    fig.update_layout(showlegend=False, yaxis_title=None)
    fig.add_vline(x=0, line_width=1, line_dash="dash", line_color="black")
    return fig

def create_resource_forecast_plot(history_df: pd.DataFrame, forecast_df: pd.DataFrame) -> go.Figure:
    """Plots historical resource demand against an ML forecast with confidence intervals."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=history_df.index, y=history_df['demand_hours'], mode='lines', name='Historical Demand', line=dict(color='#1f77b4')))
    fig.add_trace(go.Scatter(x=forecast_df.index, y=forecast_df['yhat'], mode='lines', name='Forecast', line=dict(color='crimson', dash='dash')))
    fig.add_trace(go.Scatter(x=forecast_df.index, y=forecast_df['yhat_upper'], fill=None, mode='lines', line_color='rgba(255,0,0,0.2)', showlegend=False))
    fig.add_trace(go.Scatter(x=forecast_df.index, y=forecast_df['yhat_lower'], fill='tonexty', mode='lines', line_color='rgba(255,0,0,0.2)', name='95% Confidence Interval'))
    fig.update_layout(title="<b>Functional Resource Demand Forecast</b>", xaxis_title="Date", yaxis_title="Required Hours per Month",
                      legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    return fig

def create_project_cluster_plot(df: pd.DataFrame, x_axis: str, y_axis: str) -> go.Figure:
    """Creates a scatter plot to visualize project clusters."""
    fig = px.scatter(
        df,
        x=x_axis,
        y=y_axis,
        color='cluster',
        symbol='project_type',
        hover_name='name',
        title='Project Archetypes Identified by Clustering',
        labels={'cluster': 'Project Archetype'}
    )
    fig.update_traces(marker=dict(size=12, line=dict(width=1, color='DarkSlateGrey')))
    return fig
