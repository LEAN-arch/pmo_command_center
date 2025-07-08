# pmo_command_center/utils/plot_utils.py
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

def create_resource_heatmap(df: pd.DataFrame) -> go.Figure:
    """Creates a heatmap of resource allocation."""
    pivot_df = df.pivot(index='resource_name', columns='project_id', values='allocated_hours_week').fillna(0)
    fig = px.imshow(
        pivot_df,
        text_auto=True,
        aspect="auto",
        labels=dict(x="Project", y="Resource", color="Hours/Week"),
        color_continuous_scale=px.colors.sequential.Reds
    )
    fig.update_layout(
        title="<b>Resource Allocation Heatmap (Hours per Week)</b>",
        height=400,
    )
    return fig

def create_gate_variance_plot(df: pd.DataFrame) -> go.Figure:
    """Creates a bar chart showing the variance between planned and actual gate dates."""
    df_filtered = df.dropna(subset=['actual_date'])
    if df_filtered.empty:
        return go.Figure().update_layout(title="No completed gates to analyze.")
        
    df_filtered['variance_days'] = (pd.to_datetime(df_filtered['actual_date']) - pd.to_datetime(df_filtered['planned_date'])).dt.days
    avg_variance = df_filtered.groupby('gate_name')['variance_days'].mean().reset_index()

    fig = px.bar(
        avg_variance,
        x='gate_name',
        y='variance_days',
        title='Average Gate Schedule Variance (Actual vs. Planned)',
        labels={'gate_name': 'Phase Gate', 'variance_days': 'Average Variance (Days)'},
        color='variance_days',
        color_continuous_scale='RdYlGn_r',
        text_auto=True
    )
    fig.update_layout(
        coloraxis_showscale=False,
        xaxis={'categoryorder':'total descending'}
    )
    fig.add_hline(y=0, line_width=2, line_dash="dash", line_color="black")
    return fig
