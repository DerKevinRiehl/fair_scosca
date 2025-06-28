# #############################################################################
# ####### CASE STUDY - Justin Weiss Bachelorthesis
# #######
# #######     AUTHOR:       Justin Weiss <juweiss@ethz.ch> 
# #######     YEAR :        2025
# #######     ORGANIZATION: Traffic Engineering Group (SVT), 
# #######                   Institute for Transportation Planning and Systems,
# #######                   ETH Zürich
# #######     NETWORK BY:   Kevin Riehl (ETH Zürich, SVT)
# #######     TEMPLATE BY:  Kevin Riehl (ETH Zürich, SVT)
# #############################################################################
"""
This code will run a microsimulation with one of the desired Controllers on the Network.
"""
# #############################################################################
# ## IMPORTS
# #############################################################################
import os
import sys
import traci
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import warnings
from Utils import (degree_of_saturation_SCATS,getThroughput,
                    get_average_delay_total, get_queue_lengths,get_total_travel_time,
                    get_flow,get_total_distance,get_density,get_max_delay,get_gini, get_waiting_times)
from ControllerSCOSCA import setup_scosca_control
from ControllerSCOSCAFAIRV1 import setup_scoscafairv1_control
if 'SUMO_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
warnings.filterwarnings("ignore")
from ControllerSCOSCAFAIRV2 import setup_scoscafairv2_control, Optimizer_Fairness
# #############################################################################
# ## RUN ARGUMENTS & PARSING
# #############################################################################
sumoBinary = "C:/Users/juweiss/AppData/Local/sumo-1.22.0/bin/sumo.exe"  # Adjust if needed
CONTROL_MODE = "SCOSCA" #MAX_PRESSURE, SCOSCA, SCOSCAFAIRV1, SCOSCAFAIRV2
sys.argv = ['RunSimulation.py',
            '--sumo-path', sumoBinary,
            '--controller', CONTROL_MODE]
# #############################################################################
# ## PARAMETERS FOR SIMULATIONS
# #############################################################################
# TIME PARAMETER
SIMULATION_STEPS_PER_SECOND = 1
SIMULATION_WAIT_TIME = 0
start_time = datetime.strptime("2024-03-04 15:15:00", "%Y-%m-%d %H:%M:%S")
end_time = datetime.strptime("2024-03-04 17:45:00", "%Y-%m-%d %H:%M:%S")
simulation_times = [dt.strftime("%Y-%m-%d %H:%M:%S") for dt in [start_time + timedelta(seconds=i) for i in range(int((end_time - start_time).total_seconds()) + 1)]]
simulation_duration = int((end_time - start_time).total_seconds())
# PUBLIC TRANSPORT PARAMETER
BUS_STOP_DURATION = 20 # SECS
# MAX PRESSURE PARAMETER
T_A = 5 
T_L = 3 #Yellow Time
G_T_MIN = 5 #Min Greentime (used for Max. Pressure)
G_T_MAX = 50 #Max Greentime (used for Max. Pressure)
WEIGHTS_MAX_PRESSURE = {"car": 1.0, "moc": 1.0, "lwt": 1.0, "hwt": 1.0, "bus": 1.0}
# DEBUGGING
DEBUG_CONTROLLER_LOG = "NONE"# "intersection2"
DEBUG_TIME = True
DEBUG_GUI = True
# #############################################################################
# ## METHODS
# #############################################################################
def getRandomVehicleClass(no_truck=False):
    probs = [0.81, 0.082, 0.046, 0.062]
    vals = ["car", "moc", "lwt", "hwt"]
    random_vehicle_class = np.random.choice(vals, size=1, p=probs)[0]
    while no_truck and random_vehicle_class=="hwt":
        random_vehicle_class = np.random.choice(vals, size=1, p=probs)[0]
    return random_vehicle_class

def determineWhetherTruckBannedRoute(desired_route):
    route_entrance = desired_route.split("_")[1]
    route_exit = desired_route.split("_")[2]
    selected_entrances = ["E21", "E22", "E24", "E25", "E20", "E3", "E4", "E5", "E1", "E2", "E6", "E7", "E12", "E13"]
    selected_exits = ["A1", "A2", "A3", "A16", "A18", "A15"]
    if route_entrance in selected_entrances and route_exit in selected_exits:
        return False
    return True

sumo_vehicle_types = {
    "car": "sumo_car",
    "moc": "sumo_motorcycle",
    "lwt": "sumo_transporter",
    "hwt": "sumo_truck",
    "bus": "sumo_bus",
}

def spawnRandomVehicle(veh_ctr, desired_route):
    # determine vehicle characteristics
    new_vehicle_id = "VEH_"+str(veh_ctr)
    no_truck = determineWhetherTruckBannedRoute(desired_route)
    vehicle_class = getRandomVehicleClass(no_truck)
    vehicle_type = sumo_vehicle_types[vehicle_class]
    # add vehicle with traci
    traci.vehicle.add(new_vehicle_id, desired_route, typeID=vehicle_type)
    veh_routes[new_vehicle_id] = desired_route
    veh_classes[new_vehicle_id] = vehicle_class
    
def spawnRandomBus(veh_ctr, desired_route, stops):
    # determine vehicle characteristics
    new_vehicle_id = "BUS_"+str(veh_ctr)+"-"+desired_route
    vehicle_class = "bus"
    vehicle_type = sumo_vehicle_types[vehicle_class]
    # add vehicle with traci
    traci.vehicle.add(new_vehicle_id, desired_route, typeID=vehicle_type)
    for stop in stops.split("-"):
        traci.vehicle.setBusStop(new_vehicle_id, stop, duration=BUS_STOP_DURATION)    
    veh_routes[new_vehicle_id] = desired_route
    veh_classes[new_vehicle_id] = vehicle_class

def determine_current_state():
    current_vehicles = traci.vehicle.getIDList()
    if len(current_vehicles)==0:
        print(">> NOTHING, so no state")
        return None, None
    current_lanes = [traci.vehicle.getLaneID(v_id) for v_id in current_vehicles]
    new_current_lanes = []
    for v_ctr in range(0, len(current_vehicles)):
        if not current_lanes[v_ctr].startswith(":"):
            new_current_lanes.append(current_lanes[v_ctr])
        else:
            v_id = current_vehicles[v_ctr]
            v_route = traci.vehicle.getRoute(v_id)
            v_current_edge_index = traci.vehicle.getRouteIndex(v_id)
            v_current_edge = v_route[v_current_edge_index]
            new_current_lanes.append("@"+v_current_edge)
    df_current_status = pd.DataFrame(np.asarray([current_vehicles, new_current_lanes]).transpose(), columns=["veh_id", "lane"])
    df_current_status["class"] = df_current_status["veh_id"].map(veh_classes)
    if CONTROL_MODE=="MAX_PRESSURE":
        df_current_status["weight"] = df_current_status["class"].map(WEIGHTS_MAX_PRESSURE)
    df_hidden_vehicles = df_current_status[df_current_status["lane"].str.startswith("@")]
    df_hidden_vehicles["edge"] = df_hidden_vehicles["lane"].str.replace("@","")
    excluded_edges = {"921020464#1","-331752492#0","38361907","26249185#30","183049933#0","758088375#0","-38361908#1",
                      "-25973410#1","E3","-E1","-E4","22889927#0","-25576697#0","-22889927#2","-208691154#0",
                      "E15","E10","E6"}
    df_hidden_vehicles = df_hidden_vehicles[~df_hidden_vehicles["edge"].isin(excluded_edges)]
    return df_current_status, df_hidden_vehicles

# #############################################################################
# ## MAX PRESSURE CONTROLLER
# #############################################################################
class SignalController:
    def __init__(self, intersection_name, phases, links, multiplier=None):
        self.intersection_name = intersection_name
        self.phases = phases
        self.links = links
        self.current_gt_start = 0
        self.current_phase = self.phases[0]
        self.next_phase = -1
        self.current_state = "start"
        self.timer = -1
        self.pressures = []
        self.multiplier = multiplier
        
    def doSignalLogic(self):
        self.timer += 1
        self.determinePressures()
        if self.intersection_name==DEBUG_CONTROLLER_LOG:
            print("")
            print(self.current_state, self.timer, "State:", self.current_phase, self.pressures, traci.simulation.getTime()-self.current_gt_start)
        if self.current_state == "start":
            if self.timer==G_T_MIN:
                self.current_state="check_pressures"
                self.timer = -1
            else:
                pass
        elif self.current_state=="check_pressures":
            current_pressure = self.pressures[int(self.current_phase/2)]
            other_pressures = max(self.pressures)
            if current_pressure < other_pressures:
                self.current_state="next_phase"
                self.timer = -1
            else:
                self.current_state="wait"
                self.timer = -1
        elif self.current_state=="wait":
            if self.timer==T_A:
                current_gt = traci.simulation.getTime()-self.current_gt_start
                if current_gt > G_T_MAX:
                    self.current_state = "next_phase"
                    self.timer = -1
                else:
                    self.current_state="check_pressures"
                    self.timer = -1
            else:
                pass
        elif self.current_state=="next_phase":
            valid_indices = [i for i in range(len(self.pressures)) if i != int(self.current_phase/2)]
            max_pressure = max(self.pressures[i] for i in valid_indices)
            max_indices = [i for i in valid_indices if self.pressures[i] == max_pressure]
            self.next_phase = int(random.choice(max_indices)*2)
            self.current_phase += 1
            self.timer = -1
            self.current_state="transition"
        elif self.current_state=="transition":
            if self.timer==T_L:
                self.current_phase = self.next_phase 
                self.next_phase = -1
                self.timer = -1
                self.current_state = "start"
                self.current_gt_start = traci.simulation.getTime()
            else:
                pass
        else:
            print("WARNING UNKNOWN STATE", self.current_state)
            print("")
        self.setSignalOnTrafficLights()
            
    def determinePressures(self):
        if df_current_status is None:
            self.pressures = [0 for p in self.links]
            return
        self.pressures = []
        for link in self.links:
            lanes = self.links[link]
            df_vehicles = []
            # based on lane
            if type(df_vehicles)==list:
                df_vehicles = df_current_status[df_current_status["lane"].isin(lanes)]
            else:
                df_vehicles = pd.concat((df_vehicles, df_current_status[df_current_status["lane"].isin(lanes)]))
            # based on hidden on intersection
            edges = [l.split("_")[0] for l in lanes]
            hits = df_hidden_vehicles[df_hidden_vehicles["edge"].isin(edges)]
            if len(hits)>0:
                if type(df_vehicles)==list:
                    df_vehicles = df_hidden_vehicles[df_hidden_vehicles["edge"].isin(edges)]
                else:
                    df_vehicles = pd.concat((df_vehicles, df_hidden_vehicles[df_hidden_vehicles["edge"].isin(edges)][["veh_id", "lane", "class", "weight"]]))
            pressure = 0 
            if len(df_vehicles)>0:
                pressure = sum(df_vehicles["weight"])
            # multiplier
            if self.multiplier is not None:
                if link in self.multiplier:
                    pressure *= self.multiplier[link]
            self.pressures.append(pressure)
    
    def setSignalOnTrafficLights(self):
        traci.trafficlight.setPhase(self.intersection_name, self.current_phase)

controller1 = SignalController(
    intersection_name = "intersection1",
    phases = [0, 2, 4],
    links = {0:["921020465#1_3", "921020465#1_2", "921020464#0_1", "921020464#1_1", "38361907_3", "38361907_2", "-1164287131#1_3", "-1164287131#1_2"], 
             2:["-1169441386_2", "-1169441386_1", "-331752492#1_2", "-331752492#1_1", "-331752492#0_1", "-331752492#0_2"], 
             4:["-183419042#1_1", "26249185#30_1", "26249185#30_2", "26249185#1_1", "26249185#1_2"]},
    )

controller2 = SignalController(
    intersection_name = "intersection2",
    phases = [0, 2, 4],
    links = {0:["183049933#0_1", "-38361908#1_1"], 
             2:["-38361908#1_1", "-38361908#1_2"], 
             4:["-25973410#1_1", "758088375#0_1", "758088375#0_2"]}
    )

controller3 = SignalController(
    intersection_name = "intersection3",
    phases = [0, 2, 4],
    links = {0:["E3_1", "-758088377#1_1", "-758088377#1_2", "-E1_1", "-E1_2"], 
             2:["E3_1", "E3_2"], 
             4:["-758088377#1_1", "-E1_1", "-E4_1", "-E4_2"]}
    )

controller4 = SignalController(
    intersection_name = "intersection4",
    phases = [0, 2],
    links = {0:["22889927#0_1", "758088377#2_1", "-22889927#2_1"], 
             2:["-25576697#0_0"]}
    )

controller5 = SignalController(
    intersection_name = "intersection5",
    phases = [0, 2, 4],
    links = {0:["E6_1", "E6_2", "E5_1", "130569446_1", "E15_1", "E15_2"], 
             2:["E15_2", "E6_3", "E5_2", "130569446_2"],
             4:["E10_1", "E9_1",  "1162834479#1_1", "-208691154#0_1", "-208691154#1_1"]},
    # multiplier={2:5}
    )
signal_controllers = [controller1, controller2, controller3, controller4, controller5]
# #############################################################################
# ## MAIN CODE
# #############################################################################
def Simulation(params):
    #Define Global Variables
    global veh_routes, veh_classes
    global df_current_status, df_hidden_vehicles
    global tracked_vehiclesIN
    global last_vehicles_average, vehicle_waiting_times_average
    global last_vehicles_total, vehicle_departure_times
    #Define Params
    seed, adaptation_cycle, adaptation_green, green_thresh, adaptation_offset, offset_thresh,alpha, Changetime, Thresholdtime = params
    #Add Randomness
    random.seed(seed)
    np.random.seed(seed)
    #Create Local Variables
    veh_routes = {}
    veh_classes = {}
    df_current_status = None
    df_hidden_vehicles = None
    tracked_vehiclesIN = {}
    last_vehicles_average = None
    vehicle_waiting_times_average = {}
    last_vehicles_total = set()
    vehicle_departure_times = {}
    #Introduce Junctions and Initial Values for Variables
    JUNCTION_IDS = [c.intersection_name for c in signal_controllers]
    lanes = {}
    for c in signal_controllers:
        lanes[c.intersection_name] = [lane for group in c.links.values() for lane in group]
    step = 0
    greentimes = {
        "intersection1": [27, 27, 27],     # phases: 0, 2, 4
        "intersection2": [38, 6, 37],      # phases: 0, 2, 4
        "intersection3": [38, 6, 37],      # phases: 0, 2, 4
        "intersection4": [42, 42],         # phases: 0, 2
        "intersection5": [38, 6, 37],      # phases: 0, 2, 4
    }
    up_stream_links = {
        "intersection1": {
        "921020464#1_1":{"921020464#0_1","921020465#1_2"},
        "-331752492#0_2":{"-331752492#1_2","-1169441386_2"},
        "-331752492#0_1":{"-331752492#1_1","-1169441386_1"},
        "38361907_3":{"-1164287131#1_3","-183049933#0_2"},
        "38361907_2":{"-1164287131#1_2","-183049933#0_1"},
        "26249185#30_2":{"26249185#1_2","26249185#0_2"},
        "26249185#30_1":{"26249185#1_1","26249185#0_1"}},
        "intersection2": {
        "183049933#0_1":{},
        "758088375#0_1":{},
        "-25973410#1_1":{},
        "758088375#0_2":{},
        "-38361908#1_2":{},
        "-38361908#1_1":{}},
        "intersection3":{
        "E3_2": {},
        "E3_1":{},
        "-E1_1":{"-758088377#1_1"},
        "-E1_2":{"-758088377#1_2"},
        "-E4_2":{},
        "-E4_1":{},
        },
        "intersection4":{
        "22889927#0_1":{"758088377#2_1"},
        "-22889927#2_1":{},
        "-25576697#0_0":{}},
        "intersection5":{
        "E6_1":{"E5_1","130569446_1"},
        "E6_2":{"E5_2","130569446_2"},
        "E6_3":{"E5_2","130569446_2"},
        "-208691154#0_1":{"-208691154#1_1"},
        "E15_2":{},
        "E15_1":{},
        "E10_1":{"E9_1","1162834479#1_1"}
        }
    }
    cyclelength = 90
    throughput = 0
    delay_total = 0
    delay_sideroad = 0
    delay_mainroad = 0
    veh_total = 0
    veh_sideroad = 0
    veh_mainroad = 0
    TTT=0
    TD = 0
    flow = 0
    density = 0
    DS = 0
    waiting_times = 0
    queue_lengths = 0
    last_cycle_update = -90
    ################################
    # Launch SUMO
    sumoConfigFile = "../SUMO/Configuration.sumocfg" 
    sumoCmd = [
    sumoBinary,
    "-c", sumoConfigFile,
    "--quit-on-end",
    "--start",
    "--time-to-teleport", "-1",
    "--waiting-time-memory", "6000"
    ]
    traci.start(sumoCmd)
    
    # Load Vehicle Spawn Data
    df_veh_spawn = pd.read_csv("../SUMO/Spawn_Vehicles.csv")
    df_veh_spawn = df_veh_spawn.rename(columns={"Unnamed: 0": "veh_ctr"})
    df_bus_spawn = pd.read_csv("../SUMO/Spawn_Bus.csv")
    df_bus_spawn = df_bus_spawn.rename(columns={"Unnamed: 0": "veh_ctr"})
    
    # Initialize Max Pressure
    if CONTROL_MODE=="MAX_PRESSURE":
        for controller in signal_controllers:
            controller.current_gt_start = traci.simulation.getTime()
            
    # Recorder
    veh_routes = {}
    veh_classes = {}
    
    # Run Simulation
    veh_ctr = 0
    
    for current_time in simulation_times:
        #Update Vehicles
        df_current_status, df_hidden_vehicles = determine_current_state()
        #Initialize and Update Controllers
        if CONTROL_MODE == "SCOSCA":
            if step == last_cycle_update + cyclelength:
                queue_lengths = get_queue_lengths(lanes, up_stream_links, df_hidden_vehicles)
                cyclelength,greentimes = setup_scosca_control(queue_lengths,DS, step,
                                             adaptation_cycle, adaptation_green, green_thresh,
                                             adaptation_offset, offset_thresh,
                                             greentimes,cyclelength)
                last_cycle_update = step
            DS = degree_of_saturation_SCATS(greentimes, cyclelength, step, JUNCTION_IDS, lanes)
        elif CONTROL_MODE == "SCOSCAFAIRV1":
            if step == last_cycle_update + cyclelength:
                queue_lengths = get_queue_lengths(lanes, up_stream_links, df_hidden_vehicles)
                cyclelength, greentimes = setup_scoscafairv1_control(queue_lengths,DS,waiting_times, step,
                                             adaptation_cycle, adaptation_green, green_thresh,
                                             adaptation_offset, offset_thresh,
                                             greentimes,cyclelength,alpha)
                last_cycle_update = step
            waiting_times = get_waiting_times(cyclelength, lanes, up_stream_links, df_hidden_vehicles)
            DS = degree_of_saturation_SCATS(greentimes, cyclelength, step, JUNCTION_IDS, lanes)
        elif CONTROL_MODE == "SCOSCAFAIRV2":
            if step == last_cycle_update + cyclelength:
                queue_lengths = get_queue_lengths(lanes, up_stream_links, df_hidden_vehicles)
                cyclelength,greentimes = setup_scoscafairv2_control(queue_lengths,DS, step,
                                                 adaptation_cycle, adaptation_green, green_thresh,
                                                 adaptation_offset, offset_thresh, Changetime,
                                                 greentimes,cyclelength)
                last_cycle_update = step
            DS = degree_of_saturation_SCATS(greentimes, cyclelength, step, JUNCTION_IDS, lanes)
            Optimizer_Fairness(Changetime, Thresholdtime,greentimes)
        #Update Metrics
        if step >= 1800:
            throughput += getThroughput(lanes,step)
            flow += get_flow()
            TD += get_total_distance()
            delay_t,veh_t,delay_s,veh_s,delay_m,veh_m = get_average_delay_total()
            density += get_density()
            delay_total += delay_t
            delay_sideroad += delay_s
            delay_mainroad += delay_m
            veh_total += veh_t
            veh_sideroad += veh_s
            veh_mainroad += veh_m
            TTT += get_total_travel_time(step)
        
        if CONTROL_MODE=="MAX_PRESSURE":
            #Set Trafficlights for Max Pressure
            for controller in signal_controllers:
                controller.doSignalLogic()
                
        #Spawn Vehicles
        for idx, row in df_veh_spawn[df_veh_spawn["Adjusted_Datetime"]==current_time].iterrows():
            for x in range(0, int(np.ceil(row["n_spawn"]))):
                veh_ctr += 1
                spawnRandomVehicle(veh_ctr, desired_route=str(row["route"]))
                
        #Spawn Buses
        for idx, row in df_bus_spawn[df_bus_spawn["Adjusted_Datetime"]==current_time].iterrows():
            veh_ctr += 1
            spawnRandomBus(veh_ctr, desired_route=str(row["route"]), stops=str(row["Stops"]))
            
        #Simulate for One Step
        for n in range(0,SIMULATION_STEPS_PER_SECOND):
            traci.simulationStep()
        if DEBUG_GUI:
            time.sleep(SIMULATION_WAIT_TIME)
            
        step += 1
    #Make Final Metric Calculations
    avg_delay = delay_total/veh_total
    avg_delay_sideroad = delay_sideroad/veh_sideroad
    avg_delay_mainroad = delay_mainroad/veh_mainroad
    avg_density = density/simulation_duration
    avg_speed = TD/TTT
    gini = get_gini()
    max_delay = get_max_delay()
    
    #Print Metrics
    print(f"THROUGHPUT: {throughput}",flush=True)
    print(f"FLOW: {flow}",flush=True)
    print(f"AVG SPEED: {avg_speed}",flush=True)
    print(f"DENSITY: {avg_density}",flush=True)
    print(f"AVG DELAY: {avg_delay}",flush=True)
    print(f"AVG. DELAY SIDEROAD: {avg_delay_sideroad}",flush=True)
    print(f"AVG. DELAY MAINROAD: {avg_delay_mainroad}",flush=True)
    print(f"MAX DELAY: {max_delay}",flush=True)
    print(f"TOTAL TRAVEL TIME: {TTT}",flush=True)
    print(f"GINI TOTAL: {gini[0]}",flush=True)
    print(f"GINI SIDEROAD: {gini[1]}",flush=True)
    print(f"GINI MAINROAD: {gini[2]}",flush=True)
    
    # Close SUMO
    traci.close()
    
    #Return Metrics to Optimizer
    return (throughput,flow,avg_speed,avg_density,avg_delay,avg_delay_sideroad,
            avg_delay_mainroad,max_delay, TTT,gini[0],gini[1],gini[2])
