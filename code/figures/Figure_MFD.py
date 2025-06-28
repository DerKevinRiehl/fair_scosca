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




# #############################################################################
# ###### METHODS ##############################################################
# #############################################################################

def load_mfd_data(file):
    f = open(file, "r")
    content = f.read()
    f.close()
    content = content.split("\n")
    content = [line.strip() for line in content]
    content = [line for line in content if line.startswith("<step ")]
    time = [float(line.split("time=\"")[1].split("\"")[0]) for line in content]
    speeds = [float(line.split("meanSpeed=\"")[1].split("\"")[0])*3.6 for line in content]
    density = [float(line.split("running=\"")[1].split("\"")[0]) for line in content]
    flow_cum = [float(line.split("arrived=\"")[1].split("\"")[0]) for line in content]
    flows = [flow_cum[0]] + [flow_cum[i] - flow_cum[i-1] for i in range(1, len(flow_cum))]
    flows = [flow/5*60 for flow in flows]
    return [time, flows, speeds, density]

def load_mfd_from_method(method):
    time_all = []
    flows_all = []
    speeds_all = []
    density_all = []
    for seed in ["41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60"]:
        file = "../../logs/"+method+"/seed_"+seed+"/Log_summary.xml"
        mfd_seed = load_mfd_data(file)
        time_all += mfd_seed[0]
        flows_all += mfd_seed[1]
        speeds_all += mfd_seed[2]
        density_all += mfd_seed[3]
    return [time_all, flows_all, speeds_all, density_all]

def estimate_polynomial(x, y, degree=2):
    # Fit a 2nd degree polynomial to the data
    coeffs = np.polyfit(x, y, degree)
    poly = np.poly1d(coeffs)
    # Generate x values for the smooth curve
    x_fit = np.linspace(min(x), max(x), 500)
    y_fit = poly(x_fit)
    return x_fit, y_fit




# #############################################################################
# ###### MAIN CODE ############################################################
# #############################################################################

mfd_fixed_cycle = load_mfd_from_method("FIXED_CYCLE")
mfd_max_pressure = load_mfd_from_method("MAX_PRESSURE")
mfd_scosca = load_mfd_from_method("SCOSCA")
mfd_scoscav1 = load_mfd_from_method("SCOSCAFAIRV1")
mfd_scoscav2 = load_mfd_from_method("SCOSCAFAIRV2")
    
mfd_methods = {
    "Fixed-Cycle": mfd_fixed_cycle,
    "Max-Pressure": mfd_max_pressure,
    "SCOOTS/SCATS (SCOSCA)": mfd_scosca,
    "FairSCOSCA_1": mfd_scoscav1,
    "FairSCOSCA_2": mfd_scoscav2
}

colors = {
    "Fixed-Cycle": "red", 
    "Max-Pressure": "green", 
    "SCOOTS/SCATS (SCOSCA)": "black",
    "FairSCOSCA_1": "blue",
    "FairSCOSCA_2": "cyan"
}

plt.figure(figsize=(8.0, 3.0))

plt.subplot(1,2,1)
for key in mfd_methods:
    mfd_data = mfd_methods[key]
    plt.scatter(mfd_data[3], mfd_data[1], alpha=0.025, color=colors[key])
    poly_x, poly_y = estimate_polynomial(mfd_data[3], mfd_data[1])
    plt.plot(poly_x, poly_y, 'k--', label=key, color=colors[key])
plt.legend(loc="lower right", fontsize="x-small")
plt.ylabel("Flow [veh/h]")
plt.xlabel("Density [veh]")
plt.xlim(100, 250)


plt.subplot(1,2,2)
for key in mfd_methods:
    mfd_data = mfd_methods[key]
    plt.scatter(mfd_data[3], mfd_data[2], alpha=0.025, color=colors[key])
    poly_x, poly_y = estimate_polynomial(mfd_data[3], mfd_data[2], degree=2)
    plt.plot(poly_x, poly_y, 'k--', label=key, color=colors[key])
plt.legend(loc="upper right", fontsize="x-small")
plt.ylabel("Speed [km/h]")
plt.xlabel("Density [veh]")
plt.xlim(100, 250)

plt.tight_layout()