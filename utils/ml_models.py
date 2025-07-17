"""
Centralized Machine Learning Models for the sPMO Command Center.

This module contains functions for training and applying predictive models,
including schedule risk prediction, EAC forecasting, and project archetype clustering.
This modular approach improves maintainability and scalability.
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import streamlit as st

@st.cache_resource
def train_schedule_risk_model(_projects_df: pd.DataFrame):
    """
    Trains a logistic regression model on historical data to predict delays.
    Caches the model object for performance.
    """
    df = _projects_df.copy()
    # Feature Engineering
    df['duration_days'] = (pd.to_datetime(df['end_date']) - pd.to_datetime(df['start_date'])).dt.days
    df['is_npd'] = (df['project_type'] == 'NPD').astype(int)

    # Use only completed projects with a definitive outcome for training
    train_df = df[df['final_outcome'].notna()].copy()
    
    # Define the target variable: 1 if Delayed, 0 if On Time
    train_df['target'] = (train_df['final_outcome'] == 'Delayed').astype(int)

    # Check for minimum data requirements to train a meaningful model
    if len(train_df) < 5 or train_df['target'].nunique() < 2:
        return None, None # Not enough data or only one class present

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
    Caches the model object for performance.
    """
    df = _projects_df.copy()
    
    # Feature Engineering
    df['cpi'] = df.apply(lambda row: row['ev_usd'] / row['actuals_usd'] if row['actuals_usd'] > 0 else 1.0, axis=1)
    df['spi'] = df.apply(lambda row: row['ev_usd'] / row['pv_usd'] if row['pv_usd'] > 0 else 1.0, axis=1)
    df['budget_to_complexity'] = df['budget_usd'] / df['complexity']
    df['team_to_budget'] = df['team_size'] / df['budget_usd']
    
    train_df = df[df['final_outcome'].notna()].copy()
    # Target is the final cost ratio (e.g., 1.1 means 10% overrun)
    train_df['target'] = train_df['actuals_usd'] / train_df['budget_usd']

    if len(train_df) < 5:
        return None, None

    features = ['budget_usd', 'risk_score', 'complexity', 'team_size', 'cpi', 'spi', 'budget_to_complexity', 'team_to_budget']
    
    # Clean data before training
    train_df = train_df.replace([np.inf, -np.inf], np.nan).dropna(subset=features + ['target'])
    X = train_df[features]
    y = train_df['target']

    if len(X) < 5:
        return None, None
        
    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)

    model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
    model.fit(X_train, y_train)
    
    return model, features

@st.cache_data
def get_project_clusters(_proj_df: pd.DataFrame, n_clusters: int):
    """
    Applies K-Means clustering to identify project archetypes.
    Caches the resulting DataFrame.
    """
    features = ['budget_usd', 'risk_score', 'complexity', 'team_size', 'strategic_value']
    df_for_clustering = _proj_df[features].copy()

    if df_for_clustering.empty or len(df_for_clustering) < n_clusters:
        return None

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df_for_clustering)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
    kmeans.fit(scaled_features)

    clustered_df = _proj_df.copy()
    clustered_df['cluster'] = [f"Archetype {i+1}" for i in kmeans.labels_]
    return clustered_df

def predict_project_schedule_risk(model, features: list, project_series: pd.Series):
    """Uses a trained model to predict the probability of a project being delayed."""
    if model is None or features is None:
        return 0.0, None # Default to 0 risk if no model is available

    project_features_df = project_series[features].to_frame().T
    prediction_proba = model.predict_proba(project_features_df)[0][1]

    # Explainable AI: Determine feature contributions
    coefficients = model.coef_[0]
    contributions = coefficients * project_features_df.values[0]
    contribution_df = pd.DataFrame({'feature': features, 'contribution': contributions})
    
    return prediction_proba, contribution_df

def predict_eac(model, features: list, project_series: pd.Series) -> float:
    """Uses a trained model to forecast a project's Estimate at Completion."""
    # Formula-based EAC as a reliable fallback
    cpi = project_series.get('cpi', 1.0)
    formula_eac = project_series['budget_usd'] / cpi if cpi > 0 else project_series['budget_usd']
    
    if model is None or features is None:
        # If no model, return the greater of formula-based EAC or actuals spent
        return max(formula_eac, project_series['actuals_usd'])

    # Ensure features for prediction are handled correctly
    project_features_df = pd.DataFrame([project_series[features]])
    project_features_df = project_features_df.replace([np.inf, -np.inf], 0).fillna(0)

    predicted_burn_ratio = model.predict(project_features_df)[0]
    forecasted_eac = project_series['budget_usd'] * predicted_burn_ratio
    
    # The final prediction should never be less than what's already spent
    return max(forecasted_eac, project_series['actuals_usd'])
