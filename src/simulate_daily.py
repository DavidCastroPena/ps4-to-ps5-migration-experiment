# src/simulate_daily.py

import pandas as pd
import numpy as np
from pathlib import Path

def generate_daily_simulation_csv(
    output_path: Path = Path("out/daily_simulation.csv"),
    initial_ps4: float = 113.5,    # Initial active PS4 user base (M) as of 2020-09-30
    campaign_start: str = "2023-01-01",
):
    """
    Generates a daily‐level migration simulation (PS4 → PS5) from 2020-11-01 to 2025-06-30.
    Includes an A/B test component: Control vs Treatment with an uplift in migration
    probability for Treatment after campaign_start.

    Outputs a CSV with columns:
      date, PS4_Control, PS4_Treatment, PS5_Control, PS5_Treatment,
      Migrated_Control, Migrated_Treatment, New_PS5_Supply,
      PS4_Total, PS5_Total, MAU_Simulated

    Returns the DataFrame.
    """

    # 1) Create a daily date range - Update the start date to match Q3 2020
    dates = pd.date_range(start="2020-07-01", end="2025-06-30", freq="D")

    # 2) Split the initial PS4 pool into Control and Treatment (50/50)
    ps4_c = np.zeros(len(dates))
    ps4_t = np.zeros(len(dates))
    ps5_c = np.zeros(len(dates))
    ps5_t = np.zeros(len(dates))
    mig_c = np.zeros(len(dates))
    mig_t = np.zeros(len(dates))
    new_ps5 = np.zeros(len(dates))

    # Start at day 0:
    ps4_c[0] = initial_ps4 / 2
    ps4_t[0] = initial_ps4 / 2
    ps5_c[0] = 0.0
    ps5_t[0] = 0.0

    # 3) Define baseline migration probabilities (convert quarterly 5% → daily)
    quarter_days = 91  # Approx # of days in a fiscal quarter
    p_mig_control = 0.05 / quarter_days

    # Treatment uplift (50% higher) after campaign_start
    p_mig_treatment_before = p_mig_control
    p_mig_treatment_after = p_mig_control * 1.5

    campaign_dt = pd.Timestamp(campaign_start)

    # 4) Daily retention of PS5 (90% per quarter → daily root)
    p_retain_daily = 0.9 ** (1 / quarter_days)

    # 5) PS5 sell‐in data (quarterly in millions)
    ps5_quarterly = [
        4.5, 3.3,   # FY20-Q3, Q4
        2.3, 3.3, 3.9, 2.0,   # FY21
        2.4, 3.3, 7.1, 6.3,   # FY22
        3.3, 4.9, 8.2, 4.5,   # FY23
        2.4, 3.8, 9.5, 2.8    # FY24
    ]
    quarter_starts = (
        pd.period_range("2020Q3", periods=len(ps5_quarterly), freq="Q")
        .to_timestamp(how="start")
    )

    # Build a Series of daily PS5 supply by uniformly distributing each quarter's sell‐in
    daily_supply = pd.Series(0.0, index=dates)
    for sellin, q_start in zip(ps5_quarterly, quarter_starts):
        q_end = (q_start + pd.offsets.QuarterEnd(0))
        q_range = pd.date_range(start=q_start, end=q_end, freq="D")
        per_day = sellin / len(q_range)
        daily_supply.loc[q_range] += per_day

    # 6) Simulate day‐by‐day
    for i in range(1, len(dates)):
        date = dates[i]
        prev_c4 = ps4_c[i - 1]
        prev_t4 = ps4_t[i - 1]
        prev_c5 = ps5_c[i - 1]
        prev_t5 = ps5_t[i - 1]

        # Choose treatment migration rate based on campaign start
        if date >= campaign_dt:
            p_mig_t = p_mig_treatment_after
        else:
            p_mig_t = p_mig_treatment_before

        # Migrations from PS4 → PS5
        mig_today_c = prev_c4 * p_mig_control
        mig_today_t = prev_t4 * p_mig_t

        # Update PS4 pools
        new_c4 = prev_c4 - mig_today_c
        new_t4 = prev_t4 - mig_today_t

        # Retain PS5 from previous day
        retained_c5 = prev_c5 * p_retain_daily
        retained_t5 = prev_t5 * p_retain_daily

        # Distribute new PS5 supply proportionally to existing PS5 pool sizes
        supply = daily_supply.loc[date]
        total_retained = retained_c5 + retained_t5
        if total_retained <= 0:
            new_c5_from_supply = supply / 2
            new_t5_from_supply = supply / 2
        else:
            new_c5_from_supply = supply * (retained_c5 / total_retained)
            new_t5_from_supply = supply * (retained_t5 / total_retained)

        # Update PS5 pools
        new_c5 = retained_c5 + mig_today_c + new_c5_from_supply
        new_t5 = retained_t5 + mig_today_t + new_t5_from_supply

        # Store
        ps4_c[i] = new_c4
        ps4_t[i] = new_t4
        ps5_c[i] = new_c5
        ps5_t[i] = new_t5
        mig_c[i] = mig_today_c
        mig_t[i] = mig_today_t
        new_ps5[i] = supply

    # 7) Build DataFrame
    df = pd.DataFrame({
        "date": dates,
        "PS4_Control": ps4_c,
        "PS4_Treatment": ps4_t,
        "PS5_Control": ps5_c,
        "PS5_Treatment": ps5_t,
        "Migrated_Control": mig_c,
        "Migrated_Treatment": mig_t,
        "New_PS5_Supply": new_ps5
    })
    df["PS4_Total"] = df["PS4_Control"] + df["PS4_Treatment"]
    df["PS5_Total"] = df["PS5_Control"] + df["PS5_Treatment"]
    df["MAU_Simulated"] = df["PS4_Total"] + df["PS5_Total"]

    # 8) Ensure output directory exists and write CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    return df


if __name__ == "__main__":
    # Running this script directly will generate "out/daily_simulation.csv"
    generate_daily_simulation_csv()
