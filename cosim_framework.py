"""Co-simulation framework module. Contains Model and Manager classes for running the co-simulation."""

class Model:
    """Wrapper class for modeling any physical process (e.g. power flow, heat production, etc.)."""
    
    def __init__(self, process_model):
        """Takes in the model of a physical process as a function or callable class."""
        if not callable(process_model):
            raise ValueError("The process must be a function or callable class.")
        self.process_model = process_model

    def calculate(self, *args) -> float:
        """Call the process function to perform calculations on an arbitrary number of inputs."""
        return self.process_model(*args)
    

class Manager:
    """The orchestrator manager for managing the data exchanged between the coupled models.
    
    NOTE: Currently, it is hardcoded to work with a particular sequence of execution of the coupled
    models as define in run_co_simulation.py.
    """
    
    def __init__(self, models: list[Model]):
        self.models = models
        self.controller = models[-1]  # Last model is the controller

    def run_simulation(self, time_steps: int, initial_power_setpoint: float, initial_temperature: float):
        power_setpoint = initial_power_setpoint
        room_temperature = initial_temperature
        print("===============================================================")
        print(f"Starting simulation with initial power_setpoint: {power_setpoint} and initial temperature: {room_temperature}")
        print("===============================================================")
        for t in range(time_steps):
            print(f"Time step {t}:")

            # Get model outputs for the current power setpoint
            model_outputs = []
            for model in self.models[:-2]:  # Iterate over grid and heat pump models (exclude room and controller)
                model_output = model.calculate(power_setpoint)
                model_outputs.append(model_output)

            # Assuming first output is voltage and second output is room temperature
            voltage = model_outputs[0]  # Current voltage based on current power setpoint of heat pump
            heat_production_from_hp = model_outputs[1]  # Heat production from heat pump based on power setpoint
            room_temperature = self.models[2].calculate(heat_production_from_hp)  # Update room temperature

            # Adjust power setpoint using the controller
            power_setpoint =  self.controller.calculate(power_setpoint, voltage, room_temperature)
            print("-----------------------------------------------------------")
            print(f"New power setpoint: {power_setpoint}")
            print("===========================================================")
