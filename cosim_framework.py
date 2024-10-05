"""Co-simulation framework module. Contains Model, Controller, and Manager classes for running the co-simulation."""

class Model:
    """Wrapper class for modeling any physical process (e.g. power flow, heat production, etc.)."""
    
    def __init__(self, process_function):
        """Takes in a function that models a physical process."""
        self.process_function = process_function

    def calculate(self, input_value: any) -> float:
        """Call the process function to perform calculations with the given input value."""
        return self.process_function(input_value)


class Controller:
    """A simple controller for co-simulated electric grid and heat pump systems."""
    
    def __init__(self, voltage_min: float = 10, voltage_max: float = 20, temp_min: float = 18, temp_max: float = 25,
        power_set_step_voltage: float = 100, power_set_step_temp: float = 100):
        """Initialize the controller with default values for voltage and temperature limits."""
        self.voltage_min = voltage_min
        self.voltage_max = voltage_max
        self.temp_min = temp_min
        self.temp_max = temp_max
        self.power_set_step_voltage = power_set_step_voltage
        self.power_set_step_temp = power_set_step_temp

    def adjust_power_setpoint(self, power_setpoint: float, voltage: float, heat_output: float, temperature: float) -> float:
        """Adjust power setpoint based on voltage and temperature."""
        print(f"Current power setpoint: {power_setpoint}")
        print(f"Current voltage: {voltage}")
        print(f"Current heat production: {heat_output}")
        temp_increase = heat_output * 0.1
        temperature += temp_increase
        print(f"Current temperature: {temperature}")

        # Priority 1: Adjust power based on voltage limits
        if voltage < self.voltage_min:
            power_setpoint -= self.power_set_step_voltage
            print(f"Voltage {voltage} too low, decreasing power setpoint to correct voltage.")
        elif voltage > self.voltage_max:
            power_setpoint += self.power_set_step_voltage
            print(f"Voltage {voltage} too high, increasing power setpoint to correct voltage.")

        # Priority 2: Adjust power based on temperature needs (only if voltage is within limits)
        if self.voltage_min <= voltage <= self.voltage_max:
            if temperature > self.temp_max:
                power_setpoint -= self.power_set_step_temp
                print("Temperature is too high, reducing power to cool down.")
            elif temperature < self.temp_min:
                power_setpoint += self.power_set_step_temp
                print("Temperature is too low, increasing power to warm up.")

        return power_setpoint, temperature
    

class Manager:
    """The central manager for the co-simulated system."""
    
    def __init__(self, models: list[Model], controller: Controller):
        self.models = models
        self.controller = controller

    def run_simulation(self, time_steps: int, initial_power_setpoint: float, initial_temperature: float):
        power_setpoint = initial_power_setpoint
        temperature = initial_temperature

        for t in range(time_steps):
            print(f"Time step {t}:")

            # Get model outputs for the current power setpoint
            model_outputs = []
            for model in self.models:
                model_output = model.calculate(power_setpoint)
                model_outputs.append(model_output)

            # Assuming first output is voltage and second is heat_output
            voltage = model_outputs[0]
            heat_output = model_outputs[1]

            # Adjust power setpoint using the controller
            power_setpoint, temperature = self.controller.adjust_power_setpoint(
                power_setpoint, voltage, heat_output, temperature
            )
            print("-----------------------------------------------------------")
            print(f"New power setpoint: {power_setpoint}")
            print("===========================================================")
