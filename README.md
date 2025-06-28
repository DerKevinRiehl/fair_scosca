# FairSCOSCA: Fairness At Arterial Signals - Just Around The Corner

## Introduction 

This is the online repository of **"FairSCOSCA: Fairness At Arterial Signals - Just Around The Corner"** (submitted to the 105th Annual Meeting of the Transportation Research Board (TRB 2026) in Washington DC, USA). 
This repository contians a Python-implementation of the proposed FairSCOSCA algorithm for fairness-enhancing, coordinated, signalized intersection management (traffic lights), as an adoption to SCOOTS/SCATS.
The repository is based on [SUMO (provided by DLR)](https://eclipse.dev/sumo/).

## Abstract


## Benchmark Controller Parameter

In this case study four different traffic light controllers were compared:
- Pretimed, Fixed-Cycle Controller
- Max-Pressure Controller
- SCOOTS/SCATS (SCOSCA)
- FairSCOSCA_1
- FairSCOSCA_2

The parameters for each of the control algorithms were determined with Bayesian optimization, and different goal functions.
Following tables summarize the parameters for different goal functions, and the ones chosen for the benchmark.

### Pretimed, Fixed_Cycle Controller

### Max-Pressure Controller

### SCOOTS/SCATS (SCOSCA)

|Parameter|Symbol|Throughput|Avg. Delay|Tot. Travel Time|
|--|--|--|--|--|
| Cycle length adjustment factor | $\lambda_2$ | 41.26 | 46.71 | 16.77 |
| Green phase adjustment factor | $x$ |   |   |   |
| Green phase threshold | $x$ |   |   |   |
| Offset adjustment factor | $x$ |   |   |   |
| Offset threshold | $x$ |   |   |   |

### FairSCOSCA_1

|Parameter|Symbol|Throughput|Avg. Delay|Tot. Travel Time|
|--|--|--|--|--|
| Cycle length adjustment factor | $\lambda_2$ | 41.26 | 46.71 | 16.77 |
| Green phase adjustment factor | $x$ |   |   |   |
| Green phase threshold | $x$ |   |   |   |
| Offset adjustment factor | $x$ |   |   |   |
| Offset threshold | $x$ |   |   |   |
| Alpha | $\alpha$ |

### FairSCOSCA_2



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
The microscopic traffic simulation model consists of 34 loop detectors and 96 traffic lights across seven intersections of the arterial network "Schorndorfer Strasse" in Esslingen am Neckar (Germany); the demand model was was calibrated based on real-world loop-detector data. 

## Logs

## Code

## Citation
If you found this repository helpful, please cite our work:
```
Kevin Riehl, Justin Weiss, Anastasios Kouvelas, Michail A. Makridis
"FairSCOSCA: Fairness At Arterial Signals - Just Around The Corner"
Submitted to 105th Annual Meeting of the Transportation Research Board (TRB 2026), Washington, DC, USA, January 11-15, 2025.
```