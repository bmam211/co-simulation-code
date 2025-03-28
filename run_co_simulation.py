"""Run the co-simulation."""
from functools import partial

from controller import controller_function
from cosim_framework import Manager, Model
from grid import electric_grid_function
from heat_pump import heat_pump_function
from load_configurations import load_configurations
from room import RoomFunction
from ev import  adjust_power
import argparse
import pandas as pd

# 1. Load configurations from the 'configurations' folder
configurations_folder_path = './configurations'
controller_config, settings_configs, dataset = load_configurations(configurations_folder_path,use_forecasted=False)

# 2. Create model instances by wrapping the functions with the Model class 
electric_grid_model = Model(electric_grid_function)
ev = Model(adjust_power)
heat_pump_model = Model(heat_pump_function)
room_model = Model(RoomFunction(settings_configs["config 1"]))
controller_model = Model(partial(controller_function, controller_settings=controller_config))

# 3. Run co-simulation with the given configurations
models = [electric_grid_model, heat_pump_model, room_model,ev, controller_model]
manager = Manager(models, settings_configs["config 1"])

original_results = manager.run_simulation(dataset)
manager.store_results(original_results)

parser = argparse.ArgumentParser(description="Run co-simulation with dataset selection.")
parser.add_argument("--use-forecasted", action="store_true", help="Use forecasted dataset instead of original dataset.")
args = parser.parse_args()

if args.use_forecasted:
    print("\n Running forecasted simulation...")
    controller_config, settings_configs, forecasted_dataset = load_configurations(configurations_folder_path, use_forecasted=True)
    forecasted_results = manager.run_simulation(forecasted_dataset)
    manager.compare_results(forecasted_results)
