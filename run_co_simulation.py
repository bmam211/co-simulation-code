"""Run the co-simulation."""
from cosim_framework import Manager, Model


def electric_grid_function(power_setpoint: float) -> float:
    """A simple function to model the electric grid."""
    voltage = 5000 / power_setpoint  # Voltage as a function of power setpoint
    return voltage


def heat_pump_function(power_setpoint: float) -> float:
    """A simple function to model the heat pump."""
    heat_production = 0.5 * power_setpoint  # Heat production as a function of power setpoint
    return heat_production


# Room model is implemented as a class to keep track of the room temperature
class RoomFunction:
    """A class to model the temperature of a building over time."""
    def __init__(self, initial_temperature: float):
        """Initialize the Room with the given initial temperature."""
        self.temperature = initial_temperature

    def __call__(self, heat_production_from_hp: float) -> float:
        """Callable method to update the room temperature during the simulation."""
        heat_loss = 0.09 * heat_production_from_hp
        net_heat_supplied = heat_production_from_hp - heat_loss
        self.temperature += net_heat_supplied * 0.009  # Temperature change as a function of net heat supplied
        return self.temperature


def controller_function(power_set_point_hp: float, voltage: float, temperature: float) -> float:
    """A simple controller for co-simulated coupled electric grid, heat pump, and building systems.
    
    The controller is used to adjust the power setpoint of the heat pump based boundary conditions.
    """
    # Boundary conditions
    voltage_min, voltage_max = 10, 20 
    temp_min, temp_max = 18, 25
    p_adjust_step_size_voltage = 70  # Step size for power setpoint adjustment for voltage correction
    p_adjust_step_size_temp = 20  # Step size for power setpoint adjustment for temperature correction

    # Log current state of the system
    print(f"Current power setpoint of the heat pump: {power_set_point_hp}")
    print(f"Current grid voltage: {voltage}")
    print(f"Current temperature: {temperature}")

    # Priority 1: Adjust power based on voltage limits
    if voltage < voltage_min:
        power_set_point_hp -= p_adjust_step_size_voltage
        print(f"Voltage {voltage} too low, decreasing heat pump power setpoint (consumption) to correct voltage.")
    elif voltage > voltage_max:
        power_set_point_hp += p_adjust_step_size_voltage
        print(f"Voltage {voltage} too high, increasing heat pump power setpoint (consumption) to correct voltage.")
    else:
        print()

    # Priority 2: Adjust power based on temperature needs (only if voltage is within limits)
    if voltage_min <= voltage <= voltage_max:
        if temperature > temp_max:
            power_set_point_hp -= p_adjust_step_size_temp
            print("Temperature is too high, reducing heat pump power setpoint of heatpump to cool down.")
        elif temperature < temp_min:
            power_set_point_hp += p_adjust_step_size_temp
            print("Temperature is too low, increasing heat pump power setpoint of heatpump to warm up.")

    return power_set_point_hp


# Initialize simulation parameters
initial_power_set_point_hp = 100
initial_temperature = 20
time_steps = 10

# Create model instances by wrapping the functions with the Model class 
electric_grid_model = Model(electric_grid_function)
heat_pump_model = Model(heat_pump_function)
room_model = Model(RoomFunction(initial_temperature))
controller_model = Model(controller_function)

# Create a manager instance with the models and controller
models = [electric_grid_model, heat_pump_model, room_model, controller_model]
manager = Manager(models)

# Run co-simulation
manager.run_simulation(time_steps, initial_power_set_point_hp, initial_temperature)
