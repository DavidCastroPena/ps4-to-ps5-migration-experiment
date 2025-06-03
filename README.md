#  Analyzing PlayStation User Migration from an Experimentation Standpoint: from Data ingestion → User's simulation → Experiments to Dashboards

##Check demo here 
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ps4-to-ps5-migration-experiment-wxjgvx35ksxosdztq6bjgf.streamlit.app/)

---
![Image](https://github.com/user-attachments/assets/ad3f3811-7235-4fb0-af99-5a9df5084dae)

---

## Overview

This repository demonstrates an **end-to-end experimentation platform** simulating how PlayStation 4 users migrate to PlayStation 5. It includes:

- **Data Provenance**: All public data sources (Sony’s quarterly hardware “sell-in” and “sell-through” volumes, PSN MAU anchors, etc.)  
- **Quarterly Simulation**:  
  - Simulates active PS4/PS5 user pools and produces a synthetic MAU curve (quarterly).  
  - Overlays actual PSN MAU points (SONY’s reported MAU) for validation.  
- **Daily A/B-Test + CUPED**:  
  - Splits the PS4 base 50/50 into Control vs Treatment.  
  - Treatment group receives a higher migration probability after Jan 1, 2023 (simulating a marketing campaign).  
  - Applies CUPED variance-reduction using “yesterday’s PS4 pool” as a covariate.  
- **Streamlit Dashboard**:  
  - Toggle between **Quarterly** and **Daily** views.  
  - Visualize simulated vs actual metrics, A/B experiment results, and CUPED adjustments in an interactive web app.

This project is a strong demonstration of how an Experiments/Measurement team might prototype and communicate key findings to stakeholders.

---

## Data Provenance

All underlying data used in this simulation and dashboard are **publicly available** from Sony Interactive Entertainment’s “Business Data & Sales” pages and official press releases:

1. **PS5 Quarterly “Sell-in” Volumes** (in millions of units):  
   | Fiscal Year | Q1 (Apr–Jun) | Q2 (Jul–Sep) | Q3 (Oct–Dec) | Q4 (Jan–Mar) | FY Total | Source                                                  |
   | :---------: | :----------: | :----------: | :----------: | :----------: | :------- | :------------------------------------------------------ |
   | **FY20**    | —            | —            | **4.5**      | **3.3**      | **7.8**  | Sony Interactive Entertainment (Launch Quarter)         |
   | **FY21**    | **2.3**      | **3.3**      | **3.9**      | **2.0**      | **11.5** | Sony Interactive Entertainment (Annual Report FY21)     |
   | **FY22**    | **2.4**      | **3.3**      | **7.1**      | **6.3**      | **19.1** | Sony Interactive Entertainment (Annual Report FY22)     |
   | **FY23**    | **3.3**      | **4.9**      | **8.2**      | **4.5**      | **20.9** | Sony Interactive Entertainment (Annual Report FY23)     |
   | **FY24**    | **2.4**      | **3.8**      | **9.5**      | **2.8**      | **18.5** | Sony Interactive Entertainment (As of April 30, 2024)   |

2. **PS4 Quarterly “Sell-in” Volumes** (tail years; in millions):  
   | Fiscal Year | Q1  | Q2  | Q3  | Q4  | FY Total | Source                                                      |
   | :---------: | :-: | :-: | :-: | :-: | :------: | :---------------------------------------------------------- |
   | **FY19**    | 3.2 | 2.8 | 6.0 | 1.4 | 13.5     | Sony Interactive Entertainment (FY19 Annual)                |
   | **FY20**    | 1.9 | 1.5 | 1.4 | 1.0 | 5.7      | Sony Interactive Entertainment (FY20 Annual)                |
   | **FY21**    | 0.5 | 0.2 | 0.2 | 0.1 | 1.0      | Sony Interactive Entertainment (FY21 Annual — tail of PS4)  |

   We retain PS4 “sell-in” through FY21 to model the **shrinking supply** of new PS4 consoles, which in turn influences the size of the PS4 active user pool.

3. **Installed-Base Milestones (Sell-through)**  
   These are **anchor points** used to sanity-check cumulative curves – not direct inputs to the core simulation loops, but used to validate cumulative outputs:
   | Platform | Metric      | Date         | Units (M) | Source                     |
   | :------: | :---------- | :----------- | :-------: | :------------------------- |
   | **PS5**  | Sell-through| 18 Jul 2021   | 10 M      | Sony Press Release (Jul 2021) |
   |          |             | 31 Dec 2022  | 30 M      | Sony Press Release (Dec 2022) |
   |          |             | 16 Jul 2023  | 40 M      | Sony Press Release (Jul 2023) |
   |          |             | 9 Dec 2023   | 50 M      | Sony Press Release (Dec 2023) |
   |          |             | 30 Apr 2024  | 56 M      | Sony Press Release (Apr 2024) |
   |          |             | 31 Mar 2025  | 77.7 M    | Sony Q4 FY24/25 Business Data |

   | Platform | Metric      | Date         | Units (M) | Source                                      |
   | :------: | :---------- | :----------- | :-------: | :------------------------------------------ |
   | **PS4**  | Sell-through| 30 Sep 2020  | 113.5 M   | Sony Press Release (Sep 2020)               |
   |          | Sell-in     | 30 Jun 2022  | 117 M     | Sony Business Data (FY22 Q2 PS4 “sell-in”)  |

4. **PSN MAU (Monthly Active Users, in millions)**  
   Sony published quarterly MAU figures for fiscal years 2023 and 2024:  
   | Fiscal Year | Quarter | MAU (M) | Source                                         |
   | :---------: | :-----: | :-----: | :--------------------------------------------- |
   | **FY23**    | Q1      | 108 M   | Sony Business Data (FY23 Q1)                   |
   |             | Q2      | 107 M   | Sony Business Data (FY23 Q2)                   |
   |             | Q3      | 123 M   | Sony Business Data (FY23 Q3)                   |
   |             | Q4      | 118 M   | Sony Business Data (FY23 Q4)                   |
   | **FY24**    | Q1      | 116 M   | Sony Business Data (FY24 Q1)                   |
   |             | Q2      | 116 M   | Sony Business Data (FY24 Q2)                   |
   |             | Q3      | 129 M   | Sony Business Data (FY24 Q3)                   |
   |             | Q4      | 124 M   | Sony Business Data (FY24 Q4 / as of 31 Mar 2025)|

   These actual MAU points (FY23–FY24) are overlaid as red markers on top of our quarterly simulation for validation.

---

## Interpreting the Dashboard & CUPED Analysis

Below is a guide on how to read the key charts and metrics in our Streamlit dashboard, and specifically how to interpret the CUPED‐adjusted results in the Daily view. You can include this section in your `README.md` under a header like “Interpreting the Dashboard.”

---

### Quarterly View Interpretation

When you select **“Quarterly”** in the sidebar, the dashboard displays four main panels:

1. **Simulated MAU vs Sony Reported MAU**  
   - **Blue Line**: Plots our simulated MAU (sum of active PS4 + active PS5, plus small Gaussian noise) for each quarter.  
   - **Red Dots**: Sony’s publicly reported MAU figures (FY23 Q1 → FY24 Q4). Only quarters with actual data show a red dot at the true MAU value (e.g., 108 M in FY23 Q1, 107 M in FY23 Q2, etc.).  
   - **How to Read It**:  
     - If the blue line closely tracks the red dots, our simulation matches real‐world MAU trends.  
     - Vertical gaps between blue and red indicate residual errors (shown in the “Error vs Actual MAU” panel).  

2. **Active PS4 Pool (per quarter)**  
   - Shows the simulated PS4 user base (in millions) over time.  
   - **Interpretation**: A gradual decline represents PS4 owners migrating to PS5 (or churning out).

3. **Active PS5 Pool (per quarter)**  
   - Shows the simulated PS5 user base (in millions).  
   - **Interpretation**: A rising curve, from zero in FY20 Q4 to around 56 M by FY24 Q2, roughly matching Sony’s published milestones (10 M by July 2021, 30 M by Dec 2022, etc.).

4. **Error vs Actual MAU**  
   - Plots `(Simulated_MAU − Actual_MAU)` for quarters where `Actual_MAU` exists.  
   - **Interpretation**:  
     - Residual near zero means our assumptions (5% migration, 90% retention, etc.) align well with reality.  
     - Large spikes (positive or negative) suggest tuning parameters may be needed.

> **Quick takeaway:** The quarterly panels validate our high‐level model and show how well it aligns with Sony’s real MAU data.

---

### Daily A/B Experiment Interpretation

When you switch to **“Daily”**, the dashboard auto‐generates (or loads) a CSV covering 2020-11-01 → 2025-06-30 and splits the PS4 base 50/50 into **Control** and **Treatment**. Key parts:

1. **Raw Cumulative Migrations (Control vs Treatment)**  
   - **Blue Line (Control):** Cumulative sum of daily migrations from `PS4_Control → PS5_Control`, using a baseline daily migration probability of (5 % per quarter ÷ 91 days).  
   - **Orange Line (Treatment):** Same until 2023-01-01; afterwards, Treatment’s daily probability is 50 % higher to simulate a campaign.  
   - **How to Read It:**  
     - Before 2023-01-01, both lines overlap (same migration rate).  
     - After 2023-01-01, the orange line rises faster, showing the treatment effect.  
     - The vertical gap at any date is the raw “lift” (absolute difference in migrated users).  

2. **Raw Conversion & Lift Metrics**  
   Under the chart, three metrics display:
   1. **Control Conversion (%):**  
      ```
      (Total Migrated_Control in millions) ÷ (Initial PS4_Control ← 56.75 M) × 100
      ```
   2. **Treatment Conversion (%):**  
      ```
      (Total Migrated_Treatment in millions) ÷ (Initial PS4_Treatment ← 56.75 M) × 100
      ```
   3. **Lift (Raw %):**  
      ```
      ((Treatment Conversion – Control Conversion) ÷ Control Conversion) × 100
      ```
   - **Interpretation:**  
     - If Control Conversion = 63 % and Treatment Conversion = 71 %, then Raw Lift ≈ (71 – 63) ÷ 63 × 100 ≈ 12.7 %. That means the campaign boosted migration by ~12.7 % relative to baseline.  

> **Quick takeaway:** The raw daily A/B chart shows exactly when and how much Treatment outperforms Control, but it still contains day-to-day noise.

---

### CUPED Variance-Reduction Interpretation

To reduce noise and isolate the true treatment effect, we apply **CUPED** using **“yesterday’s PS4 pool”** as the covariate:

1. **Covariate Definition**  
   - For each group (Control/Treatment), define:
     ```
     X_group(t) = PS4_group(t − 1)
     ```
   - Rationale: A larger PS4 pool yesterday generally leads to more migrations today. This correlation makes “PS4 pool at t − 1” a strong predictor of “migrated at t.”

2. **Pre-Campaign Period**  
   - Days < 2023-01-01 form the pre-campaign window. Compute:
     ```
     X_bar_pre_group = mean of X_group(t) for t < 2023-01-01
     ```

3. **Post-Campaign Period**  
   - Days ≥ 2023-01-01 form the post-campaign window. For each group:
     - Let Y_post_group(t) = Migrated_group(t).
     - Let X_post_group(t) = X_group(t).
     - Compute
       ```
       theta_group 
         = Covariance( X_post_group, Y_post_group ) ÷ Variance( X_post_group ).
       ```
     - Intuition: θ quantifies “additional migrations per extra million PS4 owners yesterday.”

4. **Compute CUPED-Adjusted Migrations**  
   - For each post-campaign day t:
     ```
     Migrated_CUPED_group(t)
       = Y_post_group(t)
         − theta_group × ( X_group(t) − X_bar_pre_group ).
     ```
   - We subtract the component of “today’s migrations” that’s explained by “yesterday’s PS4 pool deviation from its pre-campaign mean.”

5. **Plot Cumulative CUPED Curves**  
   - Take the cumulative sum of `Migrated_CUPED_group(t)` for each group:
     ```
     Cumul_CUPED_group(t) = sum_{d=first day to t} Migrated_CUPED_group(d)
     ```
   - **Chart Behavior:**  
     - Compared to raw curves, CUPED lines are smoother.  
     - The vertical gap between the two CUPED curves more clearly shows the pure treatment effect (with less noise).


6. **CUPED Conversion & Lift Metrics**  
   Under the CUPED chart, a second row of three metrics shows:
   1. **Control Conversion (CUPED %):**  
      ```
      (Final Cumul_CUPED_Control in millions) ÷ (Initial PS4_Control ← 56.75 M) × 100
      ```
   2. **Treatment Conversion (CUPED %):**  
      ```
      (Final Cumul_CUPED_Treatment in millions) ÷ (Initial PS4_Treatment ← 56.75 M) × 100
      ```
   3. **Lift (CUPED %):**  
      ```
      ((Treatment_CUPED % – Control_CUPED %) ÷ Control_CUPED %) × 100
      ```
   - **Interpretation:**  
     - Because CUPED removes variability explained by yesterday’s PS4 pool, the resulting lift is more stable and often more accurate.  

> **Key takeaway:** CUPED helps you “subtract out” predictable day-to-day fluctuations, so you see a clearer, more statistically precise treatment effect.

---

## Putting It All Together

1. **Quarterly View** validates that our supply + migration model reproduces known MAU milestones.  
2. **Daily Raw A/B View** shows exactly when the Treatment group pulls away, but is noisy.  
3. **CUPED View** yields smoother curves and a clearer lift percentage by controlling for yesterday’s PS4 pool.

> **For hiring managers:** This dashboard demonstrates a full experimentation workflow—
> sourcing data → simulating cohorts → designing an A/B test → applying CUPED variance reduction → delivering an interactive report.  
> You can point to the CUPED logic to show that you understand how to choose a strong covariate (PS4 pool) and compute θ to isolate the incremental campaign effect.

