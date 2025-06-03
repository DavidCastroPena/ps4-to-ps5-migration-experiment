# app.py

import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path


# --- 1) Ensure simulated CSV exists ---
CSV_PATH = Path("out/simulation_log.csv")

if not CSV_PATH.exists():
    st.warning("No simulation CSV found—generating now. This may take a few seconds…")
    # Dynamically import and call the simulation function
    from src.simulate import generate_simulation_csv

    # This will create "out/simulation_log.csv" on the spot
    df = generate_simulation_csv(CSV_PATH)
    st.success("Simulation data generated successfully!")
else:
    # If it already exists (e.g., local run or prior build), just read it
    df = pd.read_csv(CSV_PATH)

# --- DAILY‐LEVEL DATA LOADING / GENERATION ---
DAILY_CSV = Path("out/daily_simulation.csv")
if not DAILY_CSV.exists():
    from src.simulate_daily import generate_daily_simulation_csv
    df_daily = generate_daily_simulation_csv(output_path=DAILY_CSV)
else:
    df_daily = pd.read_csv(DAILY_CSV)

# --- 2) Sidebar: Metric selection ---
st.sidebar.title("Dashboard Options")

view_type = st.sidebar.radio(
    "Dataset Type:",
    ("Quarterly", "Daily")
)

if view_type == "Quarterly":
    metric = st.sidebar.radio(
        "Choose metric:",
        ("Simulated MAU", "Active PS4", "Active PS5", "Error vs. Actual MAU")
    )
    show_cuped = st.sidebar.checkbox("Show CUPED analysis", value=False)
else:
    # For daily view, we'll show A/B metrics automatically
    metric = None
    show_cuped = False

# --- 3) Main visualization logic ---
if view_type == "Quarterly":
    st.title("PS4 → PS5 Migration (Quarterly View)")
    st.markdown("""
        This dashboard shows quarterly simulation results and compares against Sony's reported MAU.
        - **Simulated MAU**: Total active users (PS4 + PS5)
        - **Active PS4/PS5**: Platform-specific active users
        - **Error**: Difference from actual reported MAU
    """)
    
    # Quarterly visualization logic
    if metric == "Simulated MAU":
        fig = px.line(
            df, 
            x="date",
            y="Simulated_MAU",
            title="Simulated MAU vs Actual"
        )
        if "Actual_MAU" in df.columns:
            fig.add_scatter(
                x=df["date"],
                y=df["Actual_MAU"],
                mode="markers",
                marker=dict(color="red", size=8),
                name="Sony Reported MAU"
            )
        st.plotly_chart(fig, use_container_width=True)
    
    elif metric == "Active PS4":
        fig = px.line(
            df,
            x="date", 
            y="Active_PS4",
            title="PS4 Active Users"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    elif metric == "Active PS5":
        fig = px.line(
            df,
            x="date",
            y="Active_PS5",
            title="PS5 Active Users"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    else:  # Error vs Actual
        fig = px.line(
            df.dropna(subset=["Error_MAU"]),
            x="date",
            y="Error_MAU",
            title="Simulation Error vs Actual MAU"
        )
        st.plotly_chart(fig, use_container_width=True)

else:  # Daily view
    st.title("PS4 → PS5 Migration A/B Test (Daily View)")
    st.markdown("""
        Daily-level A/B test simulation showing Control vs Treatment groups:
        - 50/50 split of initial PS4 user base
        - Treatment group receives migration boost after 2023-01-01
        - Shows cumulative migrations and conversion rates
    """)
    
    # Compute cumulative metrics
    df_daily["Cumulative_Mig_Control"] = df_daily["Migrated_Control"].cumsum()
    df_daily["Cumulative_Mig_Treatment"] = df_daily["Migrated_Treatment"].cumsum() 
    
    # Plot cumulative migrations
    fig = px.line(
        df_daily,
        x="date",
        y=["Cumulative_Mig_Control", "Cumulative_Mig_Treatment"],
        labels={"value": "Cumulative Migrations (M)", "variable": "Group"},
        title="PS4 → PS5 Migrations by Group"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Show conversion metrics
    latest = df_daily.iloc[-1]
    initial_per_group = 113.5 / 2  # Initial PS4 base split 50/50
    
    conv_control = latest["Cumulative_Mig_Control"] / initial_per_group
    conv_treatment = latest["Cumulative_Mig_Treatment"] / initial_per_group
    uplift = ((conv_treatment - conv_control) / conv_control) * 100
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Control Conv.", f"{conv_control:.1%}")
    col2.metric("Treatment Conv.", f"{conv_treatment:.1%}")
    col3.metric("Relative Uplift", f"{uplift:+.1f}%")

# Show CUPED section if enabled (Quarterly view only)
if view_type == "Quarterly" and show_cuped:
    st.markdown("---")
    st.subheader("CUPED Analysis")
    st.info("""
        **CUPED** (Controlled-experiment Using Pre-Existing Data) could be used here to:
        - Reduce variance in treatment effect estimates
        - Incorporate pre-treatment data as covariates
        - Improve statistical power
    """)
