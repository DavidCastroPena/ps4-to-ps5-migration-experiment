from pathlib import Path
import pandas as pd, random

# ── 1) PUBLIC QUARTERLY DATA ────────────────────────────────────────────────
PS5_UNITS_Q = [4.5,3.3, 2.3,3.3,3.9,2.0, 2.4,3.3,7.1,6.3, 3.3,4.9,8.2,4.5, 2.4,3.8,9.5,2.8]
PSN_MAU_ACTUAL = {10:108,11:107,12:123,13:118,14:116,15:116,16:129,17:124}
DATES = pd.period_range("2020Q4", periods=len(PS5_UNITS_Q), freq="Q").to_timestamp("Q")

# ── 2) PARAMETERS (tweak freely) ────────────────────────────────────────────
N0_PS4, P_MIG, RETIRE_Q, SEASONAL = 60_000_000, 0.60, 0.06, 0.05

# ── 3) SIMULATION LOOP ─────────────────────────────────────────────────────
ps4 = ['x'] * N0_PS4      # dummy placeholders
ps5 = []
rows = []

for idx, (dt, units_m) in enumerate(zip(DATES, PS5_UNITS_Q)):
    shipped   = int(units_m * 1_000_000)
    migrants  = min(int(shipped * P_MIG), len(ps4))
    new_users = shipped - migrants

    ps5 += [ps4.pop() for _ in range(migrants)]  # move migrants
    ps5 += ['n'] * new_users                     # add new entrants
    ps4 = [u for u in ps4 if random.random() > RETIRE_Q]  # PS4 churn

    mau = len(ps4) + len(ps5)
    if dt.quarter == 4:                          # Oct-Dec uplift
        mau = int(mau * (1 + SEASONAL))

    rows.append(dict(
        date=dt.date(),
        idx=idx,
        PS5_units_m=units_m,
        Active_PS4=len(ps4),
        Active_PS5=len(ps5),
        Simulated_MAU=mau,
        Actual_MAU=PSN_MAU_ACTUAL.get(idx),
        Error_MAU=((mau - PSN_MAU_ACTUAL[idx]*1_000_000)/1_000_000
                   if idx in PSN_MAU_ACTUAL else None)
    ))

# ── 4) WRITE CSV ───────────────────────────────────────────────────────────
out_dir = Path("out")
out_dir.mkdir(exist_ok=True)
csv_path = out_dir / "simulation_log.csv"
pd.DataFrame(rows).to_csv(csv_path, index=False)
print(f"✓  Saved {csv_path}")
