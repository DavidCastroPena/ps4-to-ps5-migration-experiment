# PS4 → PS5 Migration Experimentation Platform

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ps4-to-ps5-migration-experiment-wxjgvx35ksxosdztq6bjgf.streamlit.app/)

---
![Image](https://github.com/user-attachments/assets/bb322a22-eb5f-4fd6-9c3b-ea321aa4af0d)

---

## Project Overview

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

This project is a strong demonstration of how a Sr Data Scientist on an Experiments/Measurement team might prototype and communicate key findings to stakeholders.

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

### Quarterly Data Inputs

- **PS5 “Sell-In” (per quarter)**: \[4.5, 3.3, 2.3, 3.3, 3.9, 2.0, 2.4, 3.3, 7.1, 6.3, 3.3, 4.9, 8.2, 4.5, 2.4, 3.8, 9.5, 2.8\] (millions)  
  - Covers FY20 Q3 → FY24 Q4.

- **PS4 “Sell-In” (per quarter, tail years)**: \[3.2, 2.8, 6.0, 1.4, 1.9, 1.5, 1.4, 1.0, 0.5, 0.2, 0.2, 0.1\] (millions)  
  - Covers FY19 Q1 → FY21 Q4.

- **PSN MAU Actual**:  
  ```python
  PSN_MAU_ACTUAL = {
      10: 108, 11: 107, 12: 123, 13: 118,  # FY23 Q1–Q4
      14: 116, 15: 116, 16: 129, 17: 124   # FY24 Q1–Q4
  }
