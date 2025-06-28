# FairSCOSCA: Fairness At Arterial Signals - Just Around The Corner

## Introduction 

This is the online repository of **"FairSCOSCA: Fairness At Arterial Signals - Just Around The Corner"** (submitted to the 105th Annual Meeting of the Transportation Research Board (TRB 2026) in Washington DC, USA). 
This repository contains a Python-implementation of the proposed FairSCOSCA algorithm for fairness-enhancing, coordinated, signalized intersection management (traffic lights), as an adaptation to SCOOTS/SCATS.
The repository is based on [SUMO (provided by DLR)](https://eclipse.dev/sumo/).

## Abstract


## Benchmark Controller Parameter

In this case study four different traffic light controllers were compared:
- Pretimed, Fixed-Cycle Controller
- Max-Pressure Controller
- SCOOTS/SCATS (SCOSCA)
- FairSCOSCA_1
- FairSCOSCA_2

The parameters for each control algorithm were determined using Bayesian optimization, with the objective of minimizing the average delay across the network.
Following tables summarize the parameters obtained for SCOSCA, FairSCOSCA_1 and FairSCOSCA_2.

### SCOOTS/SCATS (SCOSCA)
|**Parameter**|**Symbol**|**Avg. Delay**|
|--|--|--|
| Green phase adjustment factor | $\lambda_1$  | 6.62 |
| Cycle length adjustment factor | $\lambda_2$ | 46.71 |
| Offset adjustment factor | $\lambda_3$ | 0.24 |
| Green phase threshold | $\tau_1$ | 0.79 |
| Offset threshold | $\tau_2$ | 0.14 |

### FairSCOSCA_1
|**Parameter**|**Symbol**|**Avg. Delay**|
|--|--|--|
| Green phase adjustment factor | $\lambda_1$  | 14.99 |
| Cycle length adjustment factor | $\lambda_2$ | 28.66 |
| Offset adjustment factor | $\lambda_3$ | 0.32 |
| Green phase threshold | $\tau_1$ | 2.41 |
| Offset threshold | $\tau_2$ | 0.47 |
| Alpha | $\alpha$ | 0.62 |

### FairSCOSCA_2
|**Parameter**|**Symbol**|**Avg. Delay**|
|--|--|--|
| Green phase adjustment factor | $\lambda_1$  | 10.59 |
| Cycle length adjustment factor | $\lambda_2$ | 10.36 | 
| Offset adjustment factor | $\lambda_3$ | 0.32 |
| Green phase threshold | $\tau_1$ | 0.10 |
| Offset threshold | $\tau_2$ | 0.11 |
| Time To Green | $\texttt{TTG}$ | 54.96 |
| Time Earlier Green | $\texttt{TEG}$ | 2.36 |


## What you will find in this repository
This repository contains the miroscopic traffic simulation model, data, and source code to reproduce the findings of our study. 
The folder contain following information:
```
./
├── code/
│   ├── figures/...
│   └── pipeline/...
│       ├── module_trip_generator/...
│       ├── module_reconstruction/...
│       ├── module_od_estimation/...
│       └── module_df_router/...
├── figures/
│   └── ...
├── model/
│   ├── Configuration.sumocfg
│   ├── Network.net.xml
│   └── ...
└── logs/
    └── ...
```


## Simulation Model
The microscopic traffic simulation model consists of five intersections of the arterial network "Schorndorfer Strasse" in Esslingen am Neckar (Germany); the demand model was was calibrated based on real-world loop-detector data. 

## Logs

## Code

## Citation
If you found this repository helpful, please cite our work:
```
Kevin Riehl, Justin Weiss, Anastasios Kouvelas, Michail A. Makridis
"FairSCOSCA: Fairness At Arterial Signals - Just Around The Corner"
Submitted to 105th Annual Meeting of the Transportation Research Board (TRB 2026), Washington, DC, USA, January 11-15, 2025.
```
