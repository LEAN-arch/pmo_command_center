# pmo_command_center/utils/plot_utils.py
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_portfolio_bubble_chart(df: pd.DataFrame) -> go.Figure:
    """Creates an interactive bubble chart for the project portfolio."""
    status_colors = {"On Track": "green", "Needs Monitoring": "orange", "At Risk": "red"}
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
        color_continuous_scale="Reds"
    )
    fig.update_layout(
        title="<b>Resource Allocation Heatmap (Hours per Week)</b>",
        height=400,
    )
    return fig
