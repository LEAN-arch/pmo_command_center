# pmo_command_center/utils/ml_models.py
"""
Centralized Machine Learning Models for the sPMO Command Center.

This module contains functions for training and applying predictive models,
including schedule risk prediction and a new model for forecasting the
Estimate at Completion (EAC) for projects. This modular approach improves
maintainability and scalability of the application's AI features.
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
import streamlit as st

@st.cache_resource
def train_schedule_risk_model(_projects_df: pd.DataFrame):
    """
    Trains a logistic regression model on historical data to predict delays.
    Uses @st.cache_resource to cache the trained model object itself.
    """
    df = _projects_df.copy()
    df['duration_days'] = (pd.to_datetime(df['end_date']) - pd.to_datetime(df['start_date'])).dt.days
    df['is_npd'] = (df['project_type'] == 'NPD').astype(int)

    train_df = df[df['final_outcome'].notna()].copy()
    train_df['target'] = (train_df['final_outcome'] == 'Delayed').astype(int)

    if len(train_df) < 5 or train_df['target'].nunique() < 2:
        return None, None # Not enough data or classes to train

    features = ['duration_days', 'risk_score', 'complexity', 'team_size', 'is_npd']
    X_train = train_df[features]
    y_train = train_df['target']

    model = LogisticRegression(random_state=42, class_weight='balanced')
    model.fit(X_train, y_train)
    return model, features

@st.cache_resource
def train_eac_prediction_model(_projects_df: pd.DataFrame):
    """
    Trains a Gradient Boosting Regressor model to predict the final cost overrun/underrun.
    This provides an AI-powered Estimate at Completion (EAC) forecast.
    """
    df = _projects_df.copy()
    
    # Feature Engineering
    df['budget_to_complexity'] = df['budget_usd'] / df['complexity']
    df['team_to_budget'] = df['team_size'] / df['budget_usd']
    
    # Target variable: Final actuals as a percentage of budget
    train_df = df[df['final_outcome'].notna()].copy()
    train_df['target'] = train_df['actuals_usd'] / train_df['budget_usd']

    if len(train_df) < 5:
        return None, None # Not enough historical data

    features = ['budget_usd', 'risk_score', 'complexity', 'team_size', 'cpi', 'spi', 'budget_to_complexity', 'team_to_budget']
    
    # Clean data just in case
    train_df = train_df.replace([np.inf, -np.inf], np.nan).dropna(subset=features + ['target'])

    X = train_df[features]
    y = train_df['target']

    if len(X) < 5:
        return None, None
        
    # Split data for simple validation (not strictly necessary for this app, but good practice)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
    model.fit(X_train, y_train)
    
    return model, features

def predict_project_schedule_risk(model, features: list, project_series: pd.Series):
    """Uses a trained model to predict the probability of a project being delayed."""
    if model is None or features is None:
        return 0.0, None # Return neutral probability and no contribution data

    project_features_df = project_series[features].to_frame().T
    prediction_proba = model.predict_proba(project_features_df)[0][1] # Probability of 'Delayed'

    # Explain the prediction
    coefficients = model.coef_[0]
    contributions = coefficients * project_features_df.values[0]
    contribution_df = pd.DataFrame({'feature': features, 'contribution': contributions})
    
    return prediction_proba, contribution_df

def predict_eac(model, features: list, project_series: pd.Series) -> float:
    """Uses a trained model to forecast a project's Estimate at Completion."""
    if model is None or features is None:
        return project_series.get('eac_usd', 0) # Default to formula-based EAC if model fails

    # Prepare input data, handling potential inf values from CPI/SPI
    project_features_df = project_series[features].to_frame().T.replace([np.inf, -np.inf], 0)
    
    predicted_burn_ratio = model.predict(project_features_df)[0]
    
    # Forecasted EAC is the original budget multiplied by the predicted final burn ratio
    forecasted_eac = project_series['budget_usd'] * predicted_burn_ratio
    
    # As a sanity check, ensure forecasted EAC is at least what has already been spent
    return max(forecasted_eac, project_series['actuals_usd'])
