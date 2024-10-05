"""Run the co-simulation."""
from cosim_framework import Model, Controller, Manager


# Trivial function to model the electric grid
def electric_grid_function(power_setpoint: float) -> float:
    voltage = 5000 / power_setpoint
    return voltage

# Trivial function to model the heat pump
def heat_pump_function(power_setpoint: float) -> float:
    heat_production = 0.5 * power_setpoint
    return heat_production

# Create model instances by wrapping the functions with Model class 
electric_grid_model = Model(electric_grid_function)
heat_pump_model = Model(heat_pump_function)

# Create a controller instance
controller = Controller()  # Initialize with default boundary conditions

# Create a manager instance with the models and controller
manager = Manager(models=[electric_grid_model, heat_pump_model], controller=controller)

# Initialize simulation parameters
initial_power = 100
initial_temperature = 20
time_steps = 5

# Run co-simulation
print(f"Starting simulation with initial power_setpoint: {initial_power}\n")
print("===========================================================")
manager.run_simulation(time_steps, initial_power, initial_temperature)
