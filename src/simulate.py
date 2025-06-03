# src/simulate.py

from pathlib import Path
import pandas as pd
import random

def generate_simulation_csv(output_path: Path = Path("out/simulation_log.csv")):
    """
    Generates the simulation_log.csv file in the `out/` directory.
    If out/ does not exist, it creates it. Returns the DataFrame for further use.
    """

    # ── 1)  PUBLIC QUARTERLY DATA  ──────────────────────────────────────────────────
    PS5_UNITS_Q = [
        4.5, 3.3,                              # FY20  Q3-Q4 (launch)
        2.3, 3.3, 3.9, 2.0,                    # FY21  Q1-Q4
        2.4, 3.3, 7.1, 6.3,                    # FY22  Q1-Q4
        3.3, 4.9, 8.2, 4.5,                    # FY23  Q1-Q4
        2.4, 3.8, 9.5, 2.8                     # FY24  Q1-Q4
    ]

    PS4_UNITS_Q = [
        3.2, 2.8, 6.0, 1.4,                    # FY19  Q1-Q4
        1.9, 1.5, 1.4, 1.0,                    # FY20  Q1-Q4
        0.5, 0.2, 0.2, 0.1                     # FY21  Q1-Q4
    ]

    MILESTONES = {
        "2021-07-18": 10,   # PS5 sell-through (M)
        "2022-12-31": 30,
        "2023-07-16": 40,
        "2023-12-09": 50,
        "2024-04-30": 56,   # sell-through
        "2025-03-31": 77.7  # sell-in
    }

    PSN_MAU_ACTUAL = {
        10: 108, 11: 107, 12: 123, 13: 118,    # FY23  Q1-Q4
        14: 116, 15: 116, 16: 129, 17: 124     # FY24  Q1-Q4
    }

    # Quarter-end dates aligned to PS5_UNITS_Q (use pandas PeriodIndex → Timestamp)
    DATES = pd.period_range("2020Q4", periods=len(PS5_UNITS_Q), freq="Q").to_timestamp("Q")

    # Parameters for simulation (you can tweak these or even make them arguments)
    P_MIG = 0.05     # Probability that an active PS4 migrates to PS5 in a quarter
    P_RETAIN = 0.9   # Probability that an active PS5 remains active quarter to quarter
    NOISE_SD = 2.0   # Standard deviation for Gaussian noise added to MU

    # Initial pools:  
    # We back out an approximate starting PS4 pool so that (PS4 + PS5 at Q0) ≈ MAU at 2020Q4 (108 M).
    initial_ps4_pool = 110.0  # a rough guess in millions  
    initial_ps5_pool = 0.0

    records = []
    ps4_pool = initial_ps4_pool
    ps5_pool = initial_ps5_pool

    for i, date in enumerate(DATES):
        new_ps5_units = PS5_UNITS_Q[i]  # supply arriving this quarter
        # Assume a fraction of new supply immediately becomes active
        immediate_adopters = new_ps5_units * 0.8
        ps5_pool = ps5_pool * P_RETAIN + immediate_adopters

        # Migration from PS4 → PS5
        migrating = ps4_pool * P_MIG
        ps4_pool = ps4_pool - migrating

        # Add migrating users to PS5 pool
        ps5_pool += migrating

        # Simulated MAU = (remaining PS4 pool + active PS5 pool) plus Gaussian noise
        simulated_mau = ps4_pool + ps5_pool + random.gauss(0, NOISE_SD)

        # Grab “actual” reported MAU if available
        actual_index = 10 + i  # maps PSN_MAU_ACTUAL keys (10 → Q1FY23, 17→Q4FY24)
        actual_mau = PSN_MAU_ACTUAL.get(actual_index, None)

        error_mau = simulated_mau - actual_mau if actual_mau is not None else None

        records.append({
            "date": date,
            "Active_PS4": round(ps4_pool, 2),
            "Active_PS5": round(ps5_pool, 2),
            "Simulated_MAU": round(simulated_mau, 2),
            "Actual_MAU": actual_mau,
            "Error_MAU": round(error_mau, 2) if error_mau is not None else None
        })

    df = pd.DataFrame(records)
    # Ensure the output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    return df


if __name__ == "__main__":
    # If someone runs `python src/simulate.py` directly, this will create the CSV.
    generate_simulation_csv()
