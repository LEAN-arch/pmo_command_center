# Autoimmunity Division - sPMO Command Center

## Overview

The **sPMO Command Center** is a comprehensive, strategic portfolio management application designed for the Werfen Autoimmunity division's PMO Director. It serves as a central, data-driven hub for executive oversight, proactive risk management, and strategic decision-making in a highly regulated medical device environment.

This tool transcends traditional reporting dashboards by integrating predictive analytics, prescriptive optimization, and interactive workflow capabilities. It empowers the PMO to evolve into a strategic partner to the business, ensuring project execution is perfectly aligned with corporate goals.

## Core Features

The application is structured around a series of integrated workspaces, each designed to support a key accountability of the PMO Director.

### 1. 📊 Executive Portfolio Dashboard
The main landing page providing a 360-degree, at-a-glance view of the entire portfolio.
- **Objective Portfolio Health Score:** A budget-weighted KPI combining CPI, SPI, and risk for an unbiased measure of health.
- **Strategic Landscape Chart:** An interactive bubble chart that visualizes all projects based on strategic value, risk, and budget.
- **QMS Health Integration:** Displays critical Quality Management System KPIs (e.g., open CAPAs) alongside project metrics.

### 2. 🎯 Strategic Scenario Planning & Optimization
An interactive suite for high-level strategic planning and decision support.
- **'What-If' Sandbox:** Activate a sandbox to simulate the impact of canceling or accelerating projects. All dashboards in the application dynamically update to reflect the simulation without affecting live data.
- **Prescriptive Portfolio Optimizer:** A powerful analytics engine that recommends the optimal project portfolio. Users define a strategic objective (e.g., Maximize Value) and constraints (budget, resources), and the engine uses linear programming to find the best set of projects to fund.
- **Strategic Roadmap:** A Gantt-style timeline of all active projects, color-coded by the strategic goals they support.

### 3. 🧬 PLM & Design Control Cockpit
A cornerstone dashboard for managing the product lifecycle in a regulated environment.
- **Realistic R&D Pipeline:** A Kanban-style view of the entire product development process, from `Concept` to `Launch`.
- **21 CFR 820.30 Compliance:** Proactively monitors Design History File (DHF) completeness to prevent late-stage documentation issues.
- **Requirements Traceability:** Visualizes the links from user needs to V&V protocols using Sankey diagrams.
- **On-Market Product Health:** Tracks post-market quality data for commercialized products.

### 4. 📈 PMO Health & Maturity
A consolidated dashboard for managing the PMO's own operational excellence.
- **Departmental Budgeting:** Tools for managing the PMO's internal budget for staffing, training, and tooling.
- **Team Management:** Tracks PMO headcount, roles, assignments, performance scores, and development paths.
- **Process Performance & Adherence:** Measures the effectiveness of the PMO methodology through metrics like gate-schedule variance, cycle time, and adherence to key processes (e.g., RAID log updates).

### 5. 🔎 Project Deep Dive & Predictive Analysis
A granular, single-project view for detailed analysis and workflow management.
- **AI-Powered Predictions:** Forecasts the likelihood of schedule delays and the final project cost (EAC).
- **Explainable AI (XAI):** Provides a chart explaining *why* the AI model made its risk prediction, showing the contributing factors.
- **Integrated Change Control Workflow:** An interactive module to review and approve pending Design Change Requests (DCRs) directly within the application (in Sandbox mode).

### 6. ⚖️ Governance & Reporting
Centralizes key governance artifacts and communication tools.
- **Portfolio RAID Log:** A filterable, portfolio-wide view of all Risks, Assumptions, Issues, and Decisions.
- **One-Click Reporting Toolkit:** Generate professional, board-ready PowerPoint decks and detailed single-project status reports with a single click.
- **Compliance Audit Trail:** An immutable, chronological log of all significant actions taken within the application, essential for **21 CFR Part 11** compliance.

## Technical Architecture

- **Framework:** Streamlit
- **Data & Analytics:** Pandas, NumPy
- **Machine Learning:** Scikit-learn (Regression), Prophet (Time-Series Forecasting)
- **Optimization:** PuLP (Linear Programming)
- **Visualization:** Plotly
- **Reporting:** python-pptx
