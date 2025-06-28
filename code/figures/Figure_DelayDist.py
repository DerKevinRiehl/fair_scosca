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

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
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
    # typs = [veh_feeder_map.get(idx, "-") for idx in ids]
    typs = [
        veh_feeder_map.get(idx, "-") if idx.startswith("VEH_") 
        else bus_feeder_map.get(idx.split("-")[-1], "-") 
        for idx in ids
    ]
    return [ids, time_loss, route_length, typs]

def load_population_from_method(method):
    ids_all = []
    timeloss_all = []
    routelength_all = []
    typs_all = []
    for seed in ["41"]:#, "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60"]:
        file = "../../logs/"+method+"/seed_"+seed+"/TripInfos.xml"
        pop_seed = load_population_data(file)
        ids_all += pop_seed[0]
        timeloss_all += pop_seed[1]
        routelength_all += pop_seed[2]
        typs_all += pop_seed[3]
    return [ids_all, timeloss_all, routelength_all, typs_all]

def plot_pdf(vals, color, label):
    # Adjust the bandwidth for the KDE
    # sns.kdeplot(vals, shade=True, bw_adjust=0.5)  # Decrease the bandwidth
    sns.kdeplot(vals, shade=True, bw_adjust=0.5, color=color, label=label)  # Add label and color




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

colors = {
    "Fixed-Cycle": "red", 
    "Max-Pressure": "green", 
    "SCOOTS/SCATS (SCOSCA)": "black",
    "FairSCOSCA_1": "blue",
    "FairSCOSCA_2": "cyan"
}


plt.figure(figsize=(8.0, 4.0))

plt.subplot(2,2,1)
for key in ["Fixed-Cycle", "Max-Pressure", "SCOOTS/SCATS (SCOSCA)"]:
    pop_data = pop_methods[key]
    plot_pdf(pop_data[1], colors[key], key)
plt.legend(loc="upper right", fontsize="x-small")
plt.ylabel("Probability\nDistribution [%]")
plt.xlabel("Delay [s]")
plt.xlim(0, 500)

plt.subplot(2,2,2)
for key in ["SCOOTS/SCATS (SCOSCA)", "FairSCOSCA_1", "FairSCOSCA_2"]:
    pop_data = pop_methods[key]
    plot_pdf(pop_data[1], colors[key], key)
plt.legend(loc="upper right", fontsize="x-small")
plt.ylabel("")
plt.yticks([])
plt.xlabel("Delay [s]")
plt.xlim(0, 500)


def draw_violinplot(pop_data):
    delays_main = []
    delays_feeder = []
    
    # Loop through each entry and classify by 'main' or 'feeder'
    for x in range(0, len(pop_data[0])):
        typs = pop_data[3][x]  # Type from the 4th element of pop_data
        if typs == "main":
            delays_main.append(pop_data[1][x])  # Collect delays for main
        else:
            delays_feeder.append(pop_data[1][x])  # Collect delays for feeder
    
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
    
    # Create the violin plot with split using positions manually
    sns.violinplot(x="type", y='delay', hue='type', data=df, split=True, ax=plt.gca(),
                   palette=["lightgray", "gray"], inner="quart", width=7.5, legend=False)

    # Disable the legend explicitly
    plt.legend([],[], frameon=False)  # This hides the legend
    
# Plotting part
plt.subplot(2, 3, 4)
draw_violinplot(pop_methods["SCOOTS/SCATS (SCOSCA)"])
plt.ylabel("Delay [s]")
plt.xlabel("SCOOTS/SCATS (SCOSCA)")
plt.xlim(-4, 5)  
plt.xticks([])
plt.ylim(0, 500)
plt.text(-3.5, 400, "arteria")
plt.text(2.5, 400, "feeder")

plt.subplot(2, 3, 5)
draw_violinplot(pop_methods["FairSCOSCA_1"])
plt.ylabel("")
plt.xlabel("FairSCOSCA_1")
plt.xlim(-4, 5)  
plt.xticks([])
plt.yticks([])
plt.ylim(0, 500)
plt.text(-3.5, 400, "arteria")
plt.text(2.5, 400, "feeder")

plt.subplot(2, 3, 6)
draw_violinplot(pop_methods["FairSCOSCA_2"])
plt.ylabel("")
plt.xlabel("FairSCOSCA_2")
plt.xlim(-4, 5)  
plt.xticks([])
plt.yticks([])
plt.ylim(0, 500)
plt.text(-3.5, 400, "arteria")
plt.text(2.5, 400, "feeder")

plt.subplots_adjust(top=0.98, bottom=0.08, left=0.125, right=0.970, hspace=0.33, wspace=0.125)
plt.tight_layout()
