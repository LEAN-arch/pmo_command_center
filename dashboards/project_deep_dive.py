# pmo_command_center/dashboards/project_deep_dive.py
"""
This module provides a detailed, single-project view. It now includes a
machine learning model to predict schedule risk and explain the key drivers,
transforming it into a proactive risk management tool.
"""
import streamlit as st
import pandas as pd
from sklearn.linear_model import LogisticRegression
from utils.pmo_session_state_manager import SPMOSessionStateManager
from utils.plot_utils import create_financial_burn_chart, create_risk_contribution_plot

@st.cache_data
def get_trained_risk_model(projects_df: pd.DataFrame):
    """Trains a logistic regression model on historical data to predict delays."""
    df = projects_df.copy()
    
    # Feature Engineering
    df['duration_days'] = (pd.to_datetime(df['end_date']) - pd.to_datetime(df['start_date'])).dt.days
    df['is_npd'] = (df['project_type'] == 'NPD').astype(int)
    
    # Use only completed projects with a known outcome for training
    train_df = df[df['final_outcome'].notna()].copy()
    
    if len(train_df) < 5 or train_df['final_outcome'].nunique() < 2:
        return None, None # Not enough data to train a model
        
    train_df['target'] = (train_df['final_outcome'] == 'Delayed').astype(int)
    
    features = ['duration_days', 'risk_score', 'complexity', 'team_size', 'is_npd']
    X_train = train_df[features]
    y_train = train_df['target']
    
    model = LogisticRegression(random_state=42, class_weight='balanced')
    model.fit(X_train, y_train)
    
    return model, features

def render_project_deep_dive(ssm: SPMOSessionStateManager):
    """Renders an interactive dashboard for analyzing a single project."""
    st.header("🔎 Project Deep Dive & Predictive Risk Analysis")
    st.caption("Select a project to analyze its status and view ML-powered predictions for potential schedule risk.")

    projects = ssm.get_data("projects")
    # ... (load other data as before)
    milestones = ssm.get_data("milestones")
    project_risks = ssm.get_data("project_risks")
    change_controls = ssm.get_data("change_controls")
    financials = ssm.get_data("financials")

    if not projects:
        st.warning("No project data available.")
        return

    proj_df = pd.DataFrame(projects)
    
    # Train the ML model
    risk_model, features = get_trained_risk_model(proj_df)

    # --- Project Selector ---
    project_names = proj_df[proj_df['final_outcome'].isna()]['name'].tolist() # Only show active projects
    selected_project_name = st.selectbox("Select an Active Project to Analyze", options=project_names)
    
    if not selected_project_name:
        st.info("Select an active project to begin analysis.")
        return

    selected_project = proj_df[proj_df['name'] == selected_project_name].iloc[0]
    project_id = selected_project['id']

    st.divider()
    st.subheader(f"Analysis for: {selected_project_name} ({project_id})")
    
    # --- ML Risk Prediction Section ---
    if risk_model:
        st.info("#### 🧠 AI-Powered Schedule Risk Forecast")
        project_features = selected_project[features].values.reshape(1, -1)
        prediction_proba = risk_model.predict_proba(project_features)[0][1] # Probability of 'Delayed'
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Predicted Likelihood of Delay", f"{prediction_proba:.1%}")
            if prediction_proba > 0.6:
                st.error("High risk of delay detected. Review contributing factors.", icon="🚨")
            elif prediction_proba > 0.3:
                st.warning("Moderate risk of delay. Monitor closely.", icon="⚠️")
            else:
                st.success("Low risk of delay predicted.", icon="✅")
        with col2:
            # Explain the prediction
            coefficients = risk_model.coef_[0]
            contributions = coefficients * project_features[0]
            contribution_df = pd.DataFrame({'feature': features, 'contribution': contributions})
            
            fig_contrib = create_risk_contribution_plot(contribution_df, "Key Drivers of Schedule Risk for This Project")
            st.plotly_chart(fig_contrib, use_container_width=True)
            st.caption("Positive values increase the predicted risk of delay; negative values decrease it.")

    st.divider()

    # --- Tabbed View for Standard Details ---
    detail_tabs = st.tabs(["**Financials & Budget**", "**Milestones**", "**Risks**", "**Change Control**"])

    with detail_tabs[0]:
        # (Financials tab content remains the same as previous version)
        st.subheader("Financial Performance")
        financial_df = pd.DataFrame(financials)
        project_financials = financial_df[financial_df['project_id'] == project_id]
        if not project_financials.empty:
            burn_chart_fig = create_financial_burn_chart(project_financials, "Project Financial Burn")
            st.plotly_chart(burn_chart_fig, use_container_width=True)

    with detail_tabs[1]:
        # (Milestones tab content remains the same)
        st.subheader("Key Milestones")
        milestone_df = pd.DataFrame(milestones)
        project_milestones = milestone_df[milestone_df['project_id'] == project_id]
        st.dataframe(project_milestones[['milestone', 'due_date', 'status']], use_container_width=True, hide_index=True)

    with detail_tabs[2]:
        # (Risks tab content remains the same)
        st.subheader("Project-Specific Risks")
        risk_df = pd.DataFrame(project_risks)
        project_risk_data = risk_df[risk_df['project_id'] == project_id]
        st.dataframe(project_risk_data[['risk_id', 'description', 'probability', 'impact', 'status']], use_container_width=True, hide_index=True)

    with detail_tabs[3]:
        # (Change Control tab content remains the same)
        st.subheader("Design Change Controls")
        change_df = pd.DataFrame(change_controls)
        project_changes = change_df[change_df['project_id'] == project_id]
        st.dataframe(project_changes[['dcr_id', 'description', 'status']], use_container_width=True, hide_index=True)
