# PS4 → PS5 Migration Experimentation Platform

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

## Quarterly Simulation

### Quarterly View Interpretation

When you select **“Quarterly”** in the sidebar, the dashboard displays four main panels:

1. **Simulated MAU vs Sony Reported MAU**  
   - **Blue Line**: This plots our simulated **MAU** (monthly active users) for each quarter, calculated as the sum of the active PS4 pool + active PS5 pool, plus a small Gaussian noise term.  
   - **Red Dots**: These are Sony’s publicly reported MAU figures (FY23 Q1 → FY24 Q4). We filter out missing values so that only quarters where Sony released data show a red dot at the exact MAU value (e.g., 108 M in FY23 Q1, 107 M in FY23 Q2, etc.).  
   - **How to Read It**:  
     - If the blue line closely tracks the red dots, it means our simulation accurately reproduces real‐world MAU trends.  
     - Vertical gaps between the blue line and red dots indicate residual errors (which are shown explicitly in the “Error vs Actual MAU” panel).  

2. **Active PS4 Pool (per quarter)**  
   - Plots just the simulated PS4 user base (in millions) over time.  
   - **Interpretation**: You’ll see a steady decline as PS4 owners either migrate to PS5 or churn out of the MAU total. This panel helps confirm that our assumed quarterly migration rate (5% of PS4 pool) is driving a realistic drop in PS4 activity.

3. **Active PS5 Pool (per quarter)**  
   - Plots the simulated PS5 user base (in millions) over the same quarters.  
   - **Interpretation**: This should climb from zero in FY20 Q4 up to around ~56 M by FY24 Q2, roughly matching Sony’s “sell-through” milestones (e.g., 10 M by July 2021, 30 M by December 2022, 56 M by April 2024). If your blue line roughly overlaps those published anchor points, the simulation is aggregating supply + migration correctly.

4. **Error vs Actual MAU**  
   - Plots the residual (`Simulated_MAU − Actual_MAU`) for each quarter where `Actual_MAU` is available.  
   - **Interpretation**:  
     - A residual near zero in FY23–FY24 indicates that, after adding noise, our simulation is centered around the true MAU.  
     - Any large positive or negative spike means our assumed migration or retention parameters might need tuning.  

> **Quick takeaway**: The quarterly panels let you validate that the high‐level supply‐and‐migration model reproduces real MAU data, and also provides transparency into PS4/PS5 pool dynamics over time.

---

### Daily A/B Experiment Interpretation

When you switch to **“Daily”**, the dashboard automatically generates (or loads) a day‐by‐day CSV covering 2020-11-01 → 2025-06-30 and splits the PS4 base 50/50 into **Control** and **Treatment**. Key parts:

1. **Raw Cumulative Migrations (Control vs Treatment)**  
   - **Blue Line (Control)**: Cumulative sum of daily migrations from PS4_Control → PS5_Control, using a baseline daily migration probability (5% per quarter ÷ ~91 days).  
   - **Orange Line (Treatment)**: Cumulative sum for the Treatment group, which uses the same baseline probability until 2023-01-01, then switches to a 50% higher daily rate (simulating a marketing campaign).  
   - **Reading the chart**:  
     - Up until 2023-01-01, the two lines track almost identically (both groups have identical migration probabilities).  
     - After 2023-01-01, the orange Treatment line curves upward more steeply, indicating the treatment effect.  
     - The vertical distance between the two lines at any date is the raw “lift” (absolute difference in migrated users) due to the campaign.  
     - The final gap at 2025-06-30 shows the total additional migrated users in Treatment vs Control.

2. **Raw Conversion & Lift Metrics**  
   - Under the chart, you see three metrics (in a row):  
     1. **Control Conversion (%)**:  
        \[
          \frac{\text{Total Migrated\_Control (M)}}{\text{Initial PS4_Control (56.75 M)}} × 100
        \]  
     2. **Treatment Conversion (%)**:  
        \[
          \frac{\text{Total Migrated\_Treatment (M)}}{\text{Initial PS4_Treatment (56.75 M)}} × 100
        \]  
     3. **Lift (Raw %)**:  
        \[
          \frac{\text{Treatment Conversion – Control Conversion}}{\text{Control Conversion}} × 100
        \]  
   - **Interpretation**:  
     - If Control Conv is, say, 63%, and Treatment Conv is 71%, then raw Lift ≈ 12.7%. That means the campaign increased the fraction of PS4 users migrating to PS5 by about 12.7% relative to the baseline.  

> **Quick takeaway**: The raw daily A/B chart shows exactly when and how much the Treatment group outperformed the Control, but it still contains day‐to‐day noise from random migration events and fluctuating PS4 pools.

---

### CUPED Variance-Reduction Interpretation

To reduce day-to-day volatility and better isolate the true treatment effect, we apply **CUPED** using **“yesterday’s PS4 pool”** as the covariate:

1. **Covariate Definition**  
   - For each group (Control, Treatment), we define  
     \[
       X_{\text{group}}(t) \;=\; \text{PS4\_group}(t-1).
     \]  
   - Rationale: If you had more PS4 owners yesterday, you’re expected to see more migrations today. This strong correlation makes “PS4 pool at \(t-1\)” a good predictor of “migrated at \(t\).”

2. **Pre-Campaign Period**  
   - All days **before** 2023-01-01 form the pre-campaign window. We calculate  
     \[
       \bar{X}_{\text{group, pre}} \;=\; \text{mean of }X_{\text{group}}(t)\;\text{for }t<2023-01-01.
     \]

3. **Post-Campaign Period**  
   - All days **on or after** 2023-01-01 form the post-window. For each group:  
     - Let \(Y_{\text{post}}(t) = \text{Migrated\_group}(t)\).  
     - Let \(X_{\text{post}}(t) = X_{\text{group}}(t)\).  
     - Compute  
       \[
         \theta_{\text{group}} 
         = \frac{\mathrm{Cov}\bigl(X_{\text{post}},\,Y_{\text{post}}\bigr)}{\mathrm{Var}\bigl(X_{\text{post}}\bigr)}.
       \]  
     - Roughly speaking, \(\theta\) captures how many additional migrations you get for each extra million PS4 owners yesterday.

4. **Construct CUPED-Adjusted Migrations**  
   - For each post-campaign day \(t:\)  
     \[
       \text{Migrated\_CUPED\_group}(t) 
         = Y_{\text{post}}(t) 
           \;-\;\theta_{\text{group}}\,\bigl(X_{\text{group}}(t) \;-\;\bar{X}_{\text{group, pre}}\bigr).
     \]  
   - Intuitively, we subtract out the portion of today’s migration that can be “explained” by yesterday’s PS4 pool deviating from its pre-campaign mean.

5. **Cumulative CUPED Curves**  
   - We then plot the cumulative sum of these “Migrated_CUPED” values for Control vs Treatment:  
     \[
       \sum_{d=1}^t \text{Migrated\_CUPED\_group}(d).
     \]  
   - **Chart Behavior**:  
     - Compared to the raw curves, the CUPED lines are noticeably **smoother**—they eliminate day-to-day noise.  
     - The vertical gap between the two CUPED curves (Control vs Treatment) is cleaner, showing the “pure” campaign effect.  

<details>
<summary>Illustrative CUPED Chart (Example)</summary>

![CUPED Adjusted Cumulative Migrations](assets/daily_cuped.png)

</details>

6. **CUPED Conversion & Lift Metrics**  
   - Under the CUPED chart, you’ll see another row of three metrics:  
     1. **Control Conversion (CUPED %)**  
     2. **Treatment Conversion (CUPED %)**  
     3. **Lift (CUPED %)**  
   - These use the final cumulative CUPED values (for each group) divided by the initial PS4 pool (56.75 M).  
   - **Interpretation**:  
     - Because CUPED removes fluctuations caused by changes in yesterday’s PS4 pool, the resulting lift % is often more precise (and sometimes slightly higher or lower) than the raw lift.  
     - In practice, this helps data scientists reach statistical significance faster by reducing variance.

---

## Putting It All Together

1. **Quarterly View** validates that our high‐level supply + retention + migration model reproduces known MAU milestones. If the blue vs red lines track well, you know the simulation parameters (e.g. 5% quarterly migration, 90% retention) are reasonable.

2. **Daily Raw A/B View** shows exactly when the Treatment campaign drives extra PS5 migrations relative to Control—but it can be noisy, since each day’s migrations depend on a random draw from a large pool.

3. **CUPED View** filters out most of that noise by controlling for yesterday’s PS4 pool size. The result is a smoother cumulative curve where the true treatment effect (orange vs blue gap) is easier to interpret and quantify. The “Lift (CUPED %)” metric at the bottom encapsulates the net effect of the campaign after variance reduction.

> **Key takeaway for hiring managers**:  
> This dashboard demonstrates every step of a real‐world experiment pipeline:  
> - **Data sourcing & simulation** (quarterly sell-in, MAU anchors).  
> - **Experiment design** (50/50 random split, treatment uplift on 2023-01-01).  
> - **Variance reduction (CUPED)** for clearer insights.  
> - **Interactive reporting** (Streamlit).  
>
> You can point at the CUPED view to show that you understand how to choose a strong covariate (yesterday’s PS4 pool), compute \(\theta\), and present a variance-reduced treatment effect in a concise chart.  
>
> When a product or marketing partner asks, “What is the true incremental lift of our campaign?”—this is the exact workflow you would follow








