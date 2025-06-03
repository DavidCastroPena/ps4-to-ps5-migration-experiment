# app.py

import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

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

# --- 2) Sidebar: Metric selection ---
st.sidebar.title("Select Metric to Plot")
metric = st.sidebar.radio(
    "Choose one:",
    ("Simulated MAU", "Active PS4", "Active PS5", "Error vs. Actual MAU")
)

show_cuped = st.sidebar.checkbox("Show CUPED placeholder", value=False)

# --- 3) Main header & description ---
st.title("PS4 → PS5 Migration Simulation Dashboard")
st.markdown(
    """
This dashboard visualizes a synthetic simulation of how PS4 users might migrate to PS5 over time,
and compares our simulated MAU against Sony’s reported MAU points.  
- **Simulated MAU**: (PS4 pool + PS5 pool) + noise  
- **Active PS4**: our simulated PS4 user base  
- **Active PS5**: our simulated PS5 user base  
- **Error vs. Actual MAU**: the residuals
"""
)

# --- 4) Plot logic ---
if metric == "Simulated MAU":
    fig = px.line(
        df,
        x="date",
        y="Simulated_MAU",
        title="Simulated MAU (vs. Actual Sony MAU points)",
    )
    # Add actual points as overlay if available
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
        title="Simulated Active PS4 User Pool",
    )
    st.plotly_chart(fig, use_container_width=True)

elif metric == "Active PS5":
    fig = px.line(
        df,
        x="date",
        y="Active_PS5",
        title="Simulated Active PS5 User Pool",
    )
    st.plotly_chart(fig, use_container_width=True)

else:  # Error vs. Actual MAU
    fig = px.line(
        df.dropna(subset=["Error_MAU"]),
        x="date",
        y="Error_MAU",
        title="Residual Error: Simulated MAU − Actual MAU",
    )
    st.plotly_chart(fig, use_container_width=True)

# --- 5) Show CUPED placeholder if requested ---
if show_cuped:
    st.markdown("---")
    st.subheader("CUPED Placeholder")
    st.info(
        """
In a true A/B test, you could use **CUPED** to reduce variance by incorporating a baseline covariate.
This section is left as a demonstration of where you would compute variance‐reduced metrics and show the uplift estimates.
"""
    )
