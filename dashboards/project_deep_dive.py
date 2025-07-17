# pmo_command_center/dashboards/project_deep_dive.py
"""
This module provides a detailed, single-project view. It now includes a
machine learning model to predict schedule risk and explain the key drivers,
integrates EVM metrics, and provides a full RAID log view, transforming it
into a proactive risk and performance management tool.
"""
import streamlit as st
import pandas as pd
from sklearn.linear_model import LogisticRegression
from utils.pmo_session_state_manager import SPMOSessionStateManager
from utils.plot_utils import create_financial_burn_chart, create_risk_contribution_plot

@st.cache_data
def get_trained_risk_model(_projects_df: pd.DataFrame):
    """Trains a logistic regression model on historical data to predict delays."""
    df = _projects_df.copy()
    df['duration_days'] = (pd.to_datetime(df['end_date']) - pd.to_datetime(df['start_date'])).dt.days
    df['is_npd'] = (df['project_type'] == 'NPD').astype(int)

    train_df = df[df['final_outcome'].notna()].copy()
    if len(train_df) < 5 or train_df['target'].nunique() < 2:
        return None, None # Not enough data or classes to train

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

    # --- Data Loading ---
    projects = ssm.get_data("projects")
    milestones, raid_logs, change_controls, financials = (ssm.get_data(k) for k in ["milestones", "raid_logs", "change_controls", "financials"])

    if not projects:
        st.warning("No project data available.")
        return

    proj_df = pd.DataFrame(projects)
    active_proj_df = proj_df[proj_df['health_status'] != 'Completed'].copy()

    # --- Model Training ---
    risk_model, features = get_trained_risk_model(proj_df)

    # --- Project Selection ---
    project_names = active_proj_df['name'].tolist()
    if not project_names:
        st.info("No active projects available for analysis.")
        return
        
    selected_project_name = st.selectbox("Select an Active Project to Analyze", options=project_names)
    if not selected_project_name:
        return

    selected_project = active_proj_df[active_proj_df['name'] == selected_project_name].iloc[0]
    project_id = selected_project['id']

    st.divider()
    st.subheader(f"Analysis for: {selected_project_name} ({project_id})")
    st.markdown(f"**Description:** *{selected_project['description']}*")

    # --- Top-Level Analysis: Predictions & Performance ---
    col1, col2 = st.columns(2)

    with col1:
        st.info("#### 🧠 AI-Powered Schedule Risk", icon="🤖")
        if risk_model:
            with st.container(border=True, height=350):
                project_features = selected_project[features].values.reshape(1, -1)
                prediction_proba = risk_model.predict_proba(project_features)[0][1] # Probability of 'Delayed'
                st.metric("Predicted Likelihood of Project Delay", f"{prediction_proba:.1%}")

                if prediction_proba > 0.6:
                    st.error("High risk of delay detected.", icon="🚨")
                elif prediction_proba > 0.3:
                    st.warning("Moderate risk of delay.", icon="⚠️")
                else:
                    st.success("Low risk of delay predicted.", icon="✅")

                st.caption("This model, trained on historical data, predicts the likelihood this project will be delayed based on its characteristics.")
        else:
            st.warning("Not enough historical data to train a predictive risk model.", icon="⚠️")

    with col2:
        st.info("#### 📈 Earned Value Performance", icon="📊")
        with st.container(border=True, height=350):
            kpi_cols = st.columns(2)
            kpi_cols[0].metric("Cost Performance Index (CPI)", f"{selected_project['cpi']:.2f}", help=">1.0 is Favorable (Under Budget)")
            kpi_cols[1].metric("Schedule Perf. Index (SPI)", f"{selected_project['spi']:.2f}", help=">1.0 is Favorable (Ahead of Schedule)")
            st.caption("Objective metrics for cost and schedule efficiency. Consistently below 1.0 indicates systemic project issues.")

    # --- Detailed Tabs ---
    st.divider()
    detail_tabs = st.tabs(["**Risk Drivers & RAID Log**", "**Financials**", "**Milestones**", "**Change Control**"])

    with detail_tabs[0]:
        st.subheader("Key Drivers of Predicted Risk")
        if risk_model:
            coefficients = risk_model.coef_[0]
            contributions = coefficients * project_features[0]
            contribution_df = pd.DataFrame({'feature': features, 'contribution': contributions})
            fig_contrib = create_risk_contribution_plot(contribution_df, "Why the AI Model Made Its Prediction")
            st.plotly_chart(fig_contrib, use_container_width=True)
            st.caption("Features with positive bars (red) are increasing the risk of delay, while negative bars (green) are decreasing it. This allows for targeted risk mitigation.")
        else:
            st.info("No predictive model available to determine risk drivers.")
        
        st.subheader(f"RAID Log for {selected_project_name}")
        raid_df = pd.DataFrame(raid_logs)
        project_raid = raid_df[raid_df['project_id'] == project_id]
        st.dataframe(project_raid[['log_id', 'type', 'description', 'owner', 'status', 'due_date']], use_container_width=True, hide_index=True)

    with detail_tabs[1]:
        st.subheader("Financial Performance")
        financial_df = pd.DataFrame(financials)
        project_financials = financial_df[financial_df['project_id'] == project_id]
        if not project_financials.empty:
            burn_chart_fig = create_financial_burn_chart(project_financials, "Project Financial Burn")
            st.plotly_chart(burn_chart_fig, use_container_width=True)
        else:
            st.info("No detailed financial data available for this project.")

    with detail_tabs[2]:
        st.subheader("Key Milestones")
        milestone_df = pd.DataFrame(milestones)
        project_milestones = milestone_df[milestone_df['project_id'] == project_id]
        st.dataframe(project_milestones[['milestone', 'due_date', 'status']], use_container_width=True, hide_index=True)

    with detail_tabs[3]:
        st.subheader("Design Change Controls")
        st.caption("Tracking changes per **21 CFR 820.30(i)**.")
        change_df = pd.DataFrame(change_controls)
        project_changes = change_df[change_df['project_id'] == project_id]
        st.dataframe(project_changes[['dcr_id', 'description', 'status']], use_container_width=True, hide_index=True)
