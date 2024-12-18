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


# Updated RoomFunction class for discrete temperature dynamics
class RoomFunction:
    """A class to model the temperature of a room over time."""
    def __init__(self, initial_temperature: float, C_room: float, R_thermal: float, T_env: float, delta_t: float):
        """Initialize the Room with thermal properties and initial temperature."""
        self.temperature = initial_temperature  # Room temperature (°C)
        self.C_room = C_room  # Thermal capacitance (J/°C)
        self.R_thermal = R_thermal  # Thermal resistance (°C/W)
        self.T_env = T_env  # Ambient temperature (°C)
        self.delta_t = delta_t  # Time step (seconds)

    def __call__(self, heat_production_from_hp: float) -> float:
        """
        Callable method to update the room temperature during the simulation.
        :param heat_production_from_hp: Heat input from the heat pump (W)
        :return: Updated room temperature (°C)
        """
        # Calculate heat loss to the environment
        Q_loss = (self.temperature - self.T_env) / self.R_thermal
        # Update room temperature using the discrete-time equation
        self.temperature += self.delta_t * (heat_production_from_hp - Q_loss) / self.C_room
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
initial_power_set_point_hp = 300
initial_temperature_room = 15
start_time = 0  # Time in seconds
end_time = 20  # Time in seconds
delta_t = 0.1  # Time step in seconds

# Parameters for RoomFunction
C_room = 500  # Thermal capacitance (J/°C)
R_thermal = 1.0  # Thermal resistance (°C/W)
T_env = 20  # Ambient temperature (°C)

# Create model instances by wrapping the functions with the Model class 
electric_grid_model = Model(electric_grid_function)
heat_pump_model = Model(heat_pump_function)
room_model = Model(RoomFunction(initial_temperature_room, C_room, R_thermal, T_env, delta_t))
controller_model = Model(controller_function)

# Create a manager instance with the models and controller
models = [electric_grid_model, heat_pump_model, room_model, controller_model]
manager = Manager(models)

# Run co-simulation
manager.run_simulation(start_time, delta_t, end_time, initial_power_set_point_hp, initial_temperature_room)
