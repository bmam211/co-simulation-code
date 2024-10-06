"""Co-simulation framework module. Contains Model and Manager classes for running the co-simulation."""

class Model:
    """Wrapper class for modeling any physical process (e.g. power flow, heat production, etc.)."""
    
    def __init__(self, process_function):
        """Takes in a function that models a physical process."""
        self.process_function = process_function

    def calculate(self, *args) -> float:
        """Call the process function to perform calculations on an arbitrary number of inputs."""
        return self.process_function(*args)
    

class Manager:
    """The orchestrator manager for managing the data exchanged between the coupled models."""
    
    def __init__(self, models: list[Model]):
        self.models = models
        self.controller = models[-1]  # Last model is the controller

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

            # Assuming first output is voltage, second is heat_output, and third is heat_loss
            voltage = model_outputs[0]
            heat_output = model_outputs[1]
            heat_loss = model_outputs[2]

            # Adjust power setpoint using the controller
            power_setpoint, temperature =  self.controller.calculate(
                power_setpoint, voltage, heat_output, temperature, heat_loss,
            )
            print("-----------------------------------------------------------")
            print(f"New power setpoint: {power_setpoint}")
            print("===========================================================")
