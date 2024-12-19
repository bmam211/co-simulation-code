"""Controller model."""


def controller_function(
    power_set_point_hp: float, voltage: float, temperature: float, controller_settings: dict,
) -> float:
    """A simple controller for co-simulated coupled electric grid, heat pump, and building systems.
    
    The controller is used to adjust the power setpoint of the heat pump based boundary conditions.
    """
    # Boundary conditions
    voltage_min = controller_settings['ControllerSettings']['boundary_conditions']['minimum_voltage']
    voltage_max = controller_settings['ControllerSettings']['boundary_conditions']['maximum_voltage']
    temp_min = controller_settings['ControllerSettings']['boundary_conditions']['minimum_temperature']
    temp_max = controller_settings['ControllerSettings']['boundary_conditions']['maximum_temperature']
    
    p_adjust_step_size_voltage = controller_settings['ControllerSettings']['actions']['p_change_for_voltage']
    p_adjust_step_size_temp = controller_settings['ControllerSettings']['actions']['p_change_for_temperature']

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