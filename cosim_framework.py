"""Co-simulation framework module. Contains Model and Manager classes for running the co-simulation."""
import matplotlib.pyplot as plt


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

    def run_simulation(
        self, start_time: float, delta_t: float, end_time: float, init_p_setpoint_hp: float, init_temp_room: float
    ):
        hp_power_setpoint = init_p_setpoint_hp
        room_temperature = init_temp_room

        # Initialize lists to store data for plotting
        times = []
        voltages = []
        temperatures = []
        power_setpoints = []
        heat_productions = []

        print("===============================================================")
        print(f"Starting simulation at time {start_time}, ending at {end_time}, with time step delta_t: {delta_t}\n")
        print(f"Initial heat pump power_setpoint: {hp_power_setpoint}\n Initial heat pump temperature: {room_temperature}\n")
        print("===============================================================")

        time_steps = int((end_time - start_time) / delta_t)
    
        for step in range(time_steps):
            current_time = start_time + step * delta_t
            print(f"Time step {step} | Current time: {current_time:.2f}")

            # Track time
            times.append(current_time)

            # Get model outputs for the current power setpoint
            model_outputs = []
            for model in self.models[:-2]:  # Iterate over grid and heat pump models (exclude room and controller)
                model_output = model.calculate(hp_power_setpoint)
                model_outputs.append(model_output)

            # Assuming first output is voltage and second output is room temperature
            voltage = model_outputs[0]  # Current voltage based on current power setpoint of heat pump
            heat_production_from_hp = model_outputs[1]  # Heat production from heat pump based on power setpoint
            room_temperature = self.models[2].calculate(heat_production_from_hp)  # Update room temperature

            # Adjust power setpoint using the controller
            hp_power_setpoint =  self.controller.calculate(hp_power_setpoint, voltage, room_temperature)
            print("-----------------------------------------------------------")
            print(f"New power setpoint: {hp_power_setpoint}")
            print("===========================================================")

            # Track the values for plotting
            voltages.append(voltage)
            temperatures.append(room_temperature)
            power_setpoints.append(hp_power_setpoint)
            heat_productions.append(heat_production_from_hp)

        # Plot the data after the simulation
        self.plot_results(times, voltages, temperatures, power_setpoints, heat_productions)

    def plot_results(self, times, voltages, temperatures, power_setpoints, heat_productions):
        plt.style.use('ggplot')
        _, axs = plt.subplots(2, 2, figsize=(12, 8))

        # Plot voltage over time
        axs[0, 0].plot(times, voltages, label="Voltage", color='blue')
        axs[0, 0].set_title("Voltage Over Time")
        axs[0, 0].set_xlabel("Time  [s]")
        axs[0, 0].set_ylabel("Voltage  [V]")

        # Plot temperature over time
        axs[0, 1].plot(times, temperatures, label="Room Temperature", color='red')
        axs[0, 1].set_title("Temperature Over Time")
        axs[0, 1].set_xlabel("Time  [s]")
        axs[0, 1].set_ylabel("Temperature  [°C]")

        # Plot heat pump power over time
        axs[1, 0].plot(times, power_setpoints, label="Power Setpoint", color='green')
        axs[1, 0].set_title("Heat Pump Power Setpoint Over Time")
        axs[1, 0].set_xlabel("Time  [s]")
        axs[1, 0].set_ylabel("Power Setpoint  [kW]")

        # Plot heat production over time
        axs[1, 1].plot(times, heat_productions, label="Heat Production", color='orange')
        axs[1, 1].set_title("Heat Production Over Time")
        axs[1, 1].set_xlabel("Time  [s]")
        axs[1, 1].set_ylabel("Heat Production  [kW]")

        # Layout and show the plot
        plt.tight_layout()
        plt.savefig("co_simulation_results.png")