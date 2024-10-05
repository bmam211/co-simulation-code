"""Co-simulation framework module. Contains Model, Controller, and Manager classes for running the co-simulation."""

class Model:
    """Wrapper class for modeling any physical process (e.g. power flow, heat production, etc.)."""
    
    def __init__(self, process_function):
        """Takes in a function that models a physical process."""
        self.process_function = process_function

    def calculate(self, *args) -> float:
        """Call the process function to perform calculations on an arbitrary number of inputs."""
        return self.process_function(*args)
    

class Manager:
    """The central manager for the co-simulated system."""
    
    def __init__(self, models: list[Model]):
        self.models = models

    def run_simulation(self, time_steps: int, initial_power_setpoint: float, initial_temperature: float):
        power_setpoint = initial_power_setpoint
        temperature = initial_temperature

        for t in range(time_steps):
            print(f"Time step {t}:")

            # Get model outputs for the current power setpoint
            model_outputs = []
            for model in self.models[:-1]:  # First exclude the controller
                model_output = model.calculate(power_setpoint)
                model_outputs.append(model_output)

            # Assuming first output is voltage and second is heat_output
            voltage = model_outputs[0]
            heat_output = model_outputs[1]

            # Adjust power setpoint using the controller
            power_setpoint, temperature =  self.models[-1].calculate(
                power_setpoint, voltage, heat_output, temperature
            )
            print("-----------------------------------------------------------")
            print(f"New power setpoint: {power_setpoint}")
            print("===========================================================")
