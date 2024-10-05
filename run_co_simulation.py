"""Run the co-simulation."""
from cosim_framework import Model, Manager


# Trivial function to model the electric grid
def electric_grid_function(power_setpoint: float) -> float:
    voltage = 5000 / power_setpoint
    return voltage


# Trivial function to model the heat pump
def heat_pump_function(power_setpoint: float) -> float:
    heat_production = 0.5 * power_setpoint
    return heat_production


# Trivial function to model controller
def controller_function(power_setpoint: float, voltage: float, heat_output: float, temperature: float) -> float:
    """A simple controller for co-simulated coupled electric grid and heat pump systems.
    
    The controller is used to adjust the power setpoint of the heat pump based boundary conditions.
    """
    # Boundary conditions
    voltage_min = 10
    voltage_max = 20
    temp_min = 18
    temp_max = 25
    power_set_step_voltage = 100
    power_set_step_temp = 100

    # Print current state
    print(f"Current power setpoint: {power_setpoint}")
    print(f"Current voltage: {voltage}")
    print(f"Current heat production: {heat_output}")
    temp_increase = heat_output * 0.1
    temperature += temp_increase
    print(f"Current temperature: {temperature}")

    # Priority 1: Adjust power based on voltage limits
    if voltage < voltage_min:
        power_setpoint -= power_set_step_voltage
        print(f"Voltage {voltage} too low, decreasing power setpoint to correct voltage.")
    elif voltage > voltage_max:
        power_setpoint += power_set_step_voltage
        print(f"Voltage {voltage} too high, increasing power setpoint to correct voltage.")

    # Priority 2: Adjust power based on temperature needs (only if voltage is within limits)
    if voltage_min <= voltage <= voltage_max:
        if temperature > temp_max:
            power_setpoint -= power_set_step_temp
            print("Temperature is too high, reducing power to cool down.")
        elif temperature < temp_min:
            power_setpoint += power_set_step_temp
            print("Temperature is too low, increasing power to warm up.")

    return power_setpoint, temperature


# Create model instances by wrapping the functions with the Model class 
electric_grid_model = Model(electric_grid_function)
heat_pump_model = Model(heat_pump_function)
controller_model = Model(controller_function)

# Create a manager instance with the models and controller
manager = Manager(models=[electric_grid_model, heat_pump_model, controller_model])

# Initialize simulation parameters
initial_power = 100
initial_temperature = 20
time_steps = 5

# Run co-simulation
print(f"Starting simulation with initial power_setpoint: {initial_power}\n")
print("===========================================================")
manager.run_simulation(time_steps, initial_power, initial_temperature)
