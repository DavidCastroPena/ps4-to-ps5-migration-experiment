import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ── Load the simulation CSV ─────────────────────────────────────────
csv_path = Path("out/simulation_log.csv")
if not csv_path.exists():
    st.error("⚠️  Run `python src/simulate.py` first to create simulation_log.csv")
    st.stop()

df = pd.read_csv(csv_path)
df["date"] = pd.to_datetime(df["date"])

# ── Sidebar controls ───────────────────────────────────────────────
st.sidebar.header("Controls")
metric_lookup = {
    "Simulated MAU": "Simulated_MAU",
    "Active PS4 users": "Active_PS4",
    "Active PS5 users": "Active_PS5",
    "Error vs actual MAU (M)": "Error_MAU"
}
metric_label = st.sidebar.selectbox("Metric to plot", list(metric_lookup))
col = metric_lookup[metric_label]

# ── Main chart ─────────────────────────────────────────────────────
title = f"{metric_label} over time"
fig = px.line(df, x="date", y=col, title=title)
fig.update_layout(hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

# ── CUPED placeholder ──────────────────────────────────────────────
if st.checkbox("Show CUPED example"):
    st.info("CUPED variance reduction would go here.")
