# #############################################################################
# ####### FairSCOSCA: Fairness At Arterial Signals - Just Around The Corner
# #######   AUTHOR:       Kevin Riehl <kriehl@ethz.ch>, Justin Weiss <juweiss@ethz.ch> 
# #######                 Anastasios Kouvelas <kouvelas@ethz.ch>, Michail A. Makridis <mmakridis@ethz.ch>
# #######   YEAR :        2025
# #######   ORGANIZATION: Traffic Engineering Group (SVT), 
# #######                 Institute for Transportation Planning and Systems,
# #######                 ETH Zürich
# #############################################################################


# #############################################################################
# ###### IMPORTS ##############################################################
# #############################################################################

import numpy as np
import pandas as pd




# #############################################################################
# ###### METHODS ##############################################################
# #############################################################################

def load_population_data(file):
    f = open(file, "r")
    content = f.read()
    f.close()
    content = content.split("\n")
    content = [line.strip() for line in content]
    content = [line for line in content if line.startswith("<tripinfo ")]
    ids = [line.split("id=\"")[1].split("\"")[0] for line in content]
    time_loss = [float(line.split("timeLoss=\"")[1].split("\"")[0]) for line in content]
    route_length = [float(line.split("routeLength=\"")[1].split("\"")[0]) for line in content]
    delay_pkm = [time_loss[x]/route_length[x] for x in range(0, len(time_loss))]
    typs = [
        veh_feeder_map.get(idx, "-") if idx.startswith("VEH_") 
        else bus_feeder_map.get(idx.split("-")[-1], "-") 
        for idx in ids
    ]
    return [ids, time_loss, route_length, typs, delay_pkm]

def load_population_from_method(method):
    ids_all = []
    timeloss_all = []
    routelength_all = []
    typs_all = []
    delay_pkm_all = []
    for seed in ["41"]:
        file = "../../logs/"+method+"/seed_"+seed+"/TripInfos.xml"
        pop_seed = load_population_data(file)
        ids_all += pop_seed[0]
        timeloss_all += pop_seed[1]
        routelength_all += pop_seed[2]
        typs_all += pop_seed[3]
        delay_pkm_all += pop_seed[4]
    return [ids_all, timeloss_all, routelength_all, typs_all, delay_pkm_all]

def gini_coefficient(values):
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    n = len(values)
    cumulative = 0
    for i, val in enumerate(sorted_vals, 1):
        cumulative += i * val
    total = sum(sorted_vals)
    if total == 0:
        return 0.0
    gini = (2 * cumulative) / (n * total) - (n + 1) / n
    return gini

def print_stats(pop_data, idx):
    delays_main = []
    delays_feeder = []
    # Loop through each entry and classify by 'main' or 'feeder'
    for x in range(0, len(pop_data[0])):
        typs = pop_data[3][x]  # Type from the 4th element of pop_data
        if idx==1:
            if typs == "main":
                delays_main.append(pop_data[1][x])  # Collect delays for main
            else:
                delays_feeder.append(pop_data[1][x])  # Collect delays for feeder
        else:
            if typs == "main":
                delays_main.append(pop_data[4][x]*1000)  # Collect delays for main
            else:
                delays_feeder.append(pop_data[4][x]*1000)  # Collect delays for feeder
    # Prepare a combined DataFrame for plotting
    combined_delays = delays_main + delays_feeder  # Combine main and feeder delays
    type_labels = ['main'] * len(delays_main) + ['feeder'] * len(delays_feeder)  # Labels for main and feeder
    # Flatten the data for the violinplot
    flattened_delays = combined_delays
    types = type_labels
    # Create DataFrame
    df = pd.DataFrame({
        'delay': flattened_delays,
        'type': types,
    })
    # Print Statements
    if idx==1:
        print(">>Delay [s]")
    else:
        print(">>Delay [s/km]")
    print("Main")
    print("Mean", f"arteria\n{np.mean(df[df['type']=='main']['delay']):.4f}")
    print("Max", f"arteria\n{np.max(df[df['type']=='main']['delay']):.4f}")
    print("Sum", f"arteria\n{np.sum(df[df['type']=='main']['delay']):.4f}")
    print("Gini", gini_coefficient(df[df['type']=='main']['delay'].tolist()))
    print("Feeder")
    print("Mean", f"feeder\n{np.mean(df[df['type']=='feeder']['delay']):.4f}")
    print("Max", f"feeder\n{np.max(df[df['type']=='feeder']['delay']):.4f}")
    print("Sum", f"feeder\n{np.sum(df[df['type']=='feeder']['delay']):.4f}")
    print("Gini", gini_coefficient(df[df['type']=='feeder']['delay'].tolist()))

def print_stats_table(pop_data, idx):
    delays_main = []
    delays_feeder = []
    for x in range(0, len(pop_data[0])):
        typs = pop_data[3][x]
        if idx == 1:
            if typs == "main":
                delays_main.append(pop_data[1][x])
            else:
                delays_feeder.append(pop_data[1][x])
        else:
            if typs == "main":
                delays_main.append(pop_data[4][x]*1000)
            else:
                delays_feeder.append(pop_data[4][x]*1000)
    data = {
        "Type": ["main", "feeder"],
        "Mean": [
            np.mean(delays_main),
            np.mean(delays_feeder)
        ],
        "Max": [
            np.max(delays_main),
            np.max(delays_feeder)
        ],
        "Sum": [
            np.sum(delays_main),
            np.sum(delays_feeder)
        ],
        "Gini": [
            gini_coefficient(delays_main),
            gini_coefficient(delays_feeder)
        ]
    }
    df = pd.DataFrame(data)
    if idx == 1:
        print(">> Delay [s]")
    else:
        print(">> Delay [s/km]")
    print(df.to_markdown(index=False)) 




# #############################################################################
# ###### MAIN CODE ############################################################
# #############################################################################

# BUS & VEHICLE ROUTES MAIN OR FEEDER ROAD
bus_feeder_map = {
    "route_101": "feeder",
    "route_R101": "feeder",
    "route_102": "feeder",
    "route_R102": "feeder",
    "route_103": "feeder",
    "route_R103": "feeder",
    "route_106": "main",
    "route_R106": "feeder",
    "route_114": "main",
    "route_R114": "feeder",
    "route_114A": "main",
    "route_R114A": "feeder",
    "route_115": "feeder",
    "route_R115": "feeder",
    "route_140": "feeder",
    "route_R140": "feeder",
    "route_132": "feeder",
    "route_R132": "feeder",
    "route_138": "feeder",
    "route_R138": "feeder",
    "route_N16": "main",
    "route_RN16": "feeder",
}
main_entrances = ["E3", "E4", "E5", "E24", "E25"]
df = pd.read_csv("../../model/Spawn_Vehicles.csv")
df["veh_id"] = df['Unnamed: 0'].apply(lambda x: "VEH_" + str(x + 1))
df['typs'] = df['entrance'].apply(lambda x: 'main' if x in main_entrances else 'feeder')
veh_feeder_map = df.set_index("veh_id")["typs"].to_dict()

# LOAD DATA
pop_fixed_cycle = load_population_from_method("FIXED_CYCLE")
pop_max_pressure = load_population_from_method("MAX_PRESSURE")
pop_scosca = load_population_from_method("SCOSCA")
pop_scoscav1 = load_population_from_method("SCOSCAFAIRV1")
pop_scoscav2 = load_population_from_method("SCOSCAFAIRV2")

pop_methods = {
    "Fixed-Cycle": pop_fixed_cycle,
    "Max-Pressure": pop_max_pressure,
    "SCOOTS/SCATS (SCOSCA)": pop_scosca,
    "FairSCOSCA_1": pop_scoscav1,
    "FairSCOSCA_2": pop_scoscav2
}

for method in ["SCOOTS/SCATS (SCOSCA)", "FairSCOSCA_1", "FairSCOSCA_2", "Max-Pressure", "Fixed-Cycle",]:
    print(method)
    # print_stats(pop_methods[method], idx=1)
    print_stats_table(pop_methods[method], idx=1)

for method in ["SCOOTS/SCATS (SCOSCA)", "FairSCOSCA_1", "FairSCOSCA_2", "Max-Pressure", "Fixed-Cycle",]:
    print(method)
    # print_stats(pop_methods[method], idx=4)
    print_stats_table(pop_methods[method], idx=4)