# app.py

import os
import numpy as np
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
    st.title("PS4 → PS5 Migration (Daily A/B with CUPED)")
    st.markdown("""
        This view shows daily‐level simulation (Control vs Treatment).  
        Treatment gets a boosted migration rate after 2023-01-01, simulating a campaign.  
        
        We'll compare:  
        1. **Raw** cumulative migrations  
        2. **CUPED‐adjusted** cumulative migrations, using "yesterday's PS4 pool" as the covariate  
        3. Final conversion & uplift metrics, both raw and CUPED‐adjusted
    """)

    # ── 1) Raw cumulative migrations ──
    df_daily["Cumulative_Mig_Control"] = df_daily["Migrated_Control"].cumsum()
    df_daily["Cumulative_Mig_Treatment"] = df_daily["Migrated_Treatment"].cumsum()

    fig_raw = px.line(
        df_daily,
        x="date",
        y=["Cumulative_Mig_Control", "Cumulative_Mig_Treatment"],
        labels={"value": "Cumulative Migrations (M)", "variable": "Group"},
        title="Raw Cumulative PS4→PS5 Migrations: Control vs. Treatment"
    )
    st.plotly_chart(fig_raw, use_container_width=True)

    # ── 2) CUPED adjustment using PS4_Total as covariate ──
    campaign_date = pd.Timestamp("2023-01-01")
    pre_mask = pd.to_datetime(df_daily["date"]) < campaign_date
    post_mask = pd.to_datetime(df_daily["date"]) >= campaign_date

    # Use yesterday's PS4 pool as covariate
    df_daily["X_Control"] = df_daily["PS4_Control"].shift(1)
    df_daily["X_Treatment"] = df_daily["PS4_Treatment"].shift(1)

    # Pre-period means and thetas
    Xc_bar_pre = df_daily.loc[pre_mask, "X_Control"].mean()
    Xt_bar_pre = df_daily.loc[pre_mask, "X_Treatment"].mean()

    # Post-period data with NaN handling
    Yc_post = df_daily.loc[post_mask, "Migrated_Control"]
    Xc_post = df_daily.loc[post_mask, "X_Control"]
    Yt_post = df_daily.loc[post_mask, "Migrated_Treatment"]
    Xt_post = df_daily.loc[post_mask, "X_Treatment"]

    # Compute thetas with NaN handling
    Xc_nonan = Xc_post.dropna()
    Yc_nonan = Yc_post.loc[Xc_nonan.index]
    theta_c = np.cov(Xc_nonan, Yc_nonan, ddof=0)[0, 1] / np.var(Xc_nonan, ddof=0)

    Xt_nonan = Xt_post.dropna()
    Yt_nonan = Yt_post.loc[Xt_nonan.index]
    theta_t = np.cov(Xt_nonan, Yt_nonan, ddof=0)[0, 1] / np.var(Xt_nonan, ddof=0)

    # CUPED adjustments
    df_daily["Migrated_CUPED_Control"] = np.nan
    df_daily["Migrated_CUPED_Treatment"] = np.nan
    
    # Apply CUPED formula
    for idx in df_daily.loc[post_mask].index:
        Xc = df_daily.at[idx, "X_Control"]
        Yc = df_daily.at[idx, "Migrated_Control"]
        if not np.isnan(Xc):
            df_daily.at[idx, "Migrated_CUPED_Control"] = (
                Yc - theta_c * (Xc - Xc_bar_pre)
            )
        
        Xt = df_daily.at[idx, "X_Treatment"]
        Yt = df_daily.at[idx, "Migrated_Treatment"]
        if not np.isnan(Xt):
            df_daily.at[idx, "Migrated_CUPED_Treatment"] = (
                Yt - theta_t * (Xt - Xt_bar_pre)
            )

    # Cumulative CUPED metrics
    df_daily["Cumul_CUPED_Control"] = df_daily["Migrated_CUPED_Control"].cumsum()
    df_daily["Cumul_CUPED_Treatment"] = df_daily["Migrated_CUPED_Treatment"].cumsum()

    # Plot CUPED results
    fig_cuped = px.line(
        df_daily,
        x="date",
        y=["Cumul_CUPED_Control", "Cumul_CUPED_Treatment"],
        labels={"value": "Cumulative CUPED Migrations (M)", "variable": "Group"},
        title="CUPED-Adjusted Cumulative Migrations"
    )
    st.plotly_chart(fig_cuped, use_container_width=True)

    # ── 3) Final metrics comparison ──
    latest = df_daily.iloc[-1]
    init_per_group = 113.5 / 2  # Initial PS4 per group

    # Raw metrics
    conv_c_raw = latest["Cumulative_Mig_Control"] / init_per_group
    conv_t_raw = latest["Cumulative_Mig_Treatment"] / init_per_group
    uplift_raw = ((conv_t_raw - conv_c_raw) / conv_c_raw) * 100

    # CUPED metrics
    last_c_cuped = df_daily["Cumul_CUPED_Control"].dropna().iloc[-1]
    last_t_cuped = df_daily["Cumul_CUPED_Treatment"].dropna().iloc[-1]
    conv_c_cuped = last_c_cuped / init_per_group
    conv_t_cuped = last_t_cuped / init_per_group
    uplift_cuped = ((conv_t_cuped - conv_c_cuped) / conv_c_cuped) * 100

    # Display metrics
    st.subheader("Conversion Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Raw Control", f"{conv_c_raw:.1%}")
    col2.metric("Raw Treatment", f"{conv_t_raw:.1%}")
    col3.metric("Raw Uplift", f"{uplift_raw:+.1f}%")

    col4, col5, col6 = st.columns(3)
    col4.metric("CUPED Control", f"{conv_c_cuped:.1%}")
    col5.metric("CUPED Treatment", f"{conv_t_cuped:.1%}")
    col6.metric("CUPED Uplift", f"{uplift_cuped:+.1f}%")

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
