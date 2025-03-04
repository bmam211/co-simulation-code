"""Run the co-simulation."""
from functools import partial

from controller import controller_function
from cosim_framework import Manager, Model
from grid import electric_grid_function
from heat_pump import heat_pump_function
from load_configurations import load_configurations
from room import RoomFunction


# 1. Load configurations from the 'configurations' folder
configurations_folder_path = './configurations'
controller_config, settings_configs = load_configurations(configurations_folder_path)

# 2. Create model instances by wrapping the functions with the Model class 
electric_grid_model = Model(electric_grid_function)
heat_pump_model = Model(heat_pump_function)
room_model = Model(RoomFunction(settings_configs["config 1"]))
controller_model = Model(partial(controller_function, controller_settings=controller_config))

# 3. Run co-simulation with the given configurations
models = [electric_grid_model, heat_pump_model, room_model, controller_model]
manager = Manager(models, settings_configs["config 1"])
manager.run_simulation()
