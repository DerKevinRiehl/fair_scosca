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
from prettytable import PrettyTable
import scipy.stats as stats




# #############################################################################
# ###### METHODS ##############################################################
# #############################################################################

def load_data(file):
    f = open(file, "r")
    content = f.read()
    f.close()
    content = content.split("\n")
    data = {}
    for line in content:
        key = line.split(":")[0].strip()
        value = float(line.split(":")[1].strip())
        data[key] = value
    return data        

def retrieve_population(method, key):
    vals = []
    for seed in ["41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60"]:
        file = "../../logs/"+method+"/seed_"+seed+"/Output.txt"
        data = load_data(file)
        vals.append(data[key])
    return vals

def retrieve_average_value(method, key):
    vals = retrieve_population(method, key)
    return np.mean(vals), np.std(vals)        
      
def compare_significance(baseline_data, method_data):
    t_stat, p_value = stats.ttest_ind(baseline_data, method_data, equal_var=False)
    if np.mean(method_data) > np.mean(baseline_data):
        char = "+"
    else:
        char = "-"
        
    # Set significance levels based on p-value
    if p_value < 0.01:
        return char+char+char
    elif p_value < 0.02:
        return char+char
    elif p_value < 0.05:
        return char
    else:
        return ""

        


# #############################################################################
# ###### RENDER EFFICIENCY TABLE ##############################################
# #############################################################################  
        
print("Efficiency Table")
print(">>>>>>>>>>>>>>>>>>>>>>>>")
table = PrettyTable()
table.field_names = ["Method", "FLOW", "AVG SPEED", "DENSITY", "THROUGHPUT"]

# Iterate over methods and keys to populate the table
for method in ["SCOSCA", "SCOSCAFAIRV1", "SCOSCAFAIRV2", "MAX_PRESSURE", "FIXED_CYCLE"]:
    row = [method]  # Start with the method as the first column
    
    for key in ["FLOW", "AVG SPEED", "DENSITY", "THROUGHPUT"]:
        baseline = retrieve_population("SCOSCA", key)
        significance = ""
        if method in ["SCOSCAFAIRV1", "SCOSCAFAIRV2",  "MAX_PRESSURE", "FIXED_CYCLE"]:
            compare = retrieve_population(method, key)
            significance = compare_significance(baseline, compare)
        mean, std = retrieve_average_value(method, key)
        # Format the mean and std
        result = f"{mean:.4f} [{std:.2f}]"
        
        # Append significance symbols for SCOSCAFAIRV1 and SCOSCAFAIRV2
        if significance:
            result += f" {significance}"
        
        # Append to the row
        row.append(result)
        
    
    table.add_row(row)
print(table)
print(">>>>>>>>>>>>>>>>>>>>>>>>")
print("")




# #############################################################################
# ###### RENDER EQUITY TABLE ##################################################
# #############################################################################  
        
table = PrettyTable()
table.field_names = ["Method", "GINI TOTAL", "MAX DELAY", "TOTAL TRAVEL TIME", "AVG DELAY"]

print("Equity Table")
print(">>>>>>>>>>>>>>>>>>>>>>>>")
# Iterate over methods and keys to populate the table
for method in ["SCOSCA", "SCOSCAFAIRV1", "SCOSCAFAIRV2", "MAX_PRESSURE", "FIXED_CYCLE"]:
    row = [method]  # Start with the method as the first column
    
    for key in ["GINI TOTAL", "MAX DELAY", "TOTAL TRAVEL TIME", "AVG DELAY"]:
        baseline = retrieve_population("SCOSCA", key)
        significance = ""
        if method in ["SCOSCAFAIRV1", "SCOSCAFAIRV2",  "MAX_PRESSURE", "FIXED_CYCLE"]:
            compare = retrieve_population(method, key)
            significance = compare_significance(baseline, compare)
        mean, std = retrieve_average_value(method, key)
        # Format the mean and std
        result = f"{mean:.4f} [{std:.2f}]"
        
        # Append significance symbols for SCOSCAFAIRV1 and SCOSCAFAIRV2
        if significance:
            result += f" {significance}"
        
        # Append to the row
        row.append(result)
        
    table.add_row(row)
print(table)
print(">>>>>>>>>>>>>>>>>>>>>>>>")
print("")




# #############################################################################
# ###### RENDER EQUITY TABLE 2 ################################################
# #############################################################################  
        
table = PrettyTable()
table.field_names = ["Method", "AVG. DELAY SIDEROAD", "AVG. DELAY MAINROAD", "GINI SIDEROAD", "GINI MAINROAD"]

print("Equity Table 2 (HORIZONTAL)")
print(">>>>>>>>>>>>>>>>>>>>>>>>")
# Iterate over methods and keys to populate the table
for method in ["SCOSCA", "SCOSCAFAIRV1", "SCOSCAFAIRV2", "MAX_PRESSURE", "FIXED_CYCLE"]:
    row = [method]  # Start with the method as the first column
    
    for key in ["AVG. DELAY SIDEROAD", "AVG. DELAY MAINROAD", "GINI SIDEROAD", "GINI MAINROAD"]:
        baseline = retrieve_population("SCOSCA", key)
        significance = ""
        if method in ["SCOSCAFAIRV1", "SCOSCAFAIRV2",  "MAX_PRESSURE", "FIXED_CYCLE"]:
            compare = retrieve_population(method, key)
            significance = compare_significance(baseline, compare)
        mean, std = retrieve_average_value(method, key)
        # Format the mean and std
        result = f"{mean:.4f} [{std:.2f}]"
        
        # Append significance symbols for SCOSCAFAIRV1 and SCOSCAFAIRV2
        if significance:
            result += f" {significance}"
        
        # Append to the row
        row.append(result)
        
    table.add_row(row)
print(table)
print(">>>>>>>>>>>>>>>>>>>>>>>>")
print("")