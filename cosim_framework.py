"""Co-simulation framework module. Contains Model and Manager classes for running the co-simulation."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def generate_daily_status(delta_t: int) -> np.ndarray:
    """
    Generates a status array where:
      - 1 = user is away (cannot charge EV, different temperature limits).
      - 0 = user is at home.

    Args:
        delta_t (int): Time step in minutes.

    Returns:
        np.ndarray: Status array for the entire simulation (31 days).
    """
    num_days = 31
    total_minutes = num_days * 1440  # 31 days * 1440 minutes per day
    time_steps = total_minutes // delta_t  # Convert to simulation steps

    status = np.zeros(time_steps, dtype=int)  # Default: user is home

    for day in range(num_days):
        start_of_day = day * 1440  # Start minute of the day

        # Generate random leave and return times
        leave_time = start_of_day + np.random.randint(300, 360)  # Leave (5 AM - 6 AM)
        return_time = start_of_day + np.random.randint(1020, 1080)  # Return (5 PM - 6 PM)

        # Convert to time step indices
        leave_step = min(leave_time // delta_t, time_steps - 1)
        return_step = min(return_time // delta_t, time_steps - 1)

        # Set status to 1 (away) in this period
        status[leave_step:return_step] = 1

    return status


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
    """The orchestrator manager for managing the data exchanged between the coupled models."""

    def __init__(self, models: list[Model], settings_configuration: dict):
        self.models = models
        self.electric_grid = models[0]  # First model is the electric grid
        self.heat_pump = models[1]  # Second model is the heat pump
        self.room = models[2]  # Third model is the room
        self.ev = models[3]  # EV Model
        self.controller = models[-1]  # Last model is the controller
        self.settings_configuration = settings_configuration
        self.results = None

    def run_simulation(self, df):
        temp_rise = np.linspace(0, 15, num=48, endpoint=True)
        temp_fall = np.linspace(0, 15, num=48, endpoint=True)
        temp_day = np.concatenate((temp_rise, temp_fall))

        # Extract the relevant simulation parameters from the configuration
        config = self.settings_configuration
        outside_temp = np.tile(temp_day, 31)
        config_id = config['InitializationSettings']['config_id']
        start_time = config['InitializationSettings']['time']['start_time']
        end_time = config['InitializationSettings']['time']['end_time']
        delta_t = config['InitializationSettings']['time']['delta_t']

        # Grid line data
        grid_topology = pd.read_csv(config['InitializationSettings']['grid_topology'])

        # Passive consumers
        passive_consumer_power_setpoints = df
        #passive_consumer_power_setpoints = pd.read_csv(
        #    config['InitializationSettings']['passive_consumers_power_setpoints'], index_col="snapshots",
        #    parse_dates=True,
        #)

        # Smart consumer
        hp_power_setpoint = config['InitializationSettings']['initial_conditions']['heat_pump']['power_set_point']
        room_temperature = config['InitializationSettings']['initial_conditions']['room']['temperature']
        ev_power = config['InitializationSettings']['initial_conditions']['ev']['power']  # Initialize once

        # Initialize lists to store data for plotting
        results = {
            "times": [],
            "smart_consumer_voltage": [],
            "temperature": [],
            "hp_power_setpoint": [],
            "heat_production": [],
            "ev_power": [],
        } # Store status for plotting

        print("===============================================================")
        print(f"Starting simulation at time {start_time}, ending at {end_time}, with time step delta_t: {delta_t}\n")
        print(
            f"Initial heat pump power_setpoint: {hp_power_setpoint}\nInitial heat pump temperature: {room_temperature}\n")
        print("===============================================================")

        time_steps = int((end_time - start_time) / delta_t)
        status = generate_daily_status(delta_t)

        for time_step in range(time_steps):
            time_clock = start_time + time_step * delta_t
            current_status = status[time_step]

            # Map time step to the corresponding index in the power setpoint dataframe
            corresponding_time_in_dataframe = passive_consumer_power_setpoints.index[time_step]
            print(f"Time step {corresponding_time_in_dataframe} | Simulation time clock: {time_clock:.2f}")

            # Compute new state based on the current power setpoint of the heat pump
            all_consumer_voltages = self.electric_grid.calculate(
                passive_consumer_power_setpoints, hp_power_setpoint, grid_topology, corresponding_time_in_dataframe,
            )
            smart_consumer_voltage = all_consumer_voltages["consumers"]["smart_consumer"]

            # Update EV power, ensuring it accumulates over time

            heat_production_from_hp = self.heat_pump.calculate(hp_power_setpoint)
            room_temperature = self.room.calculate(heat_production_from_hp, outside_temp[time_step])
            ev_power = self.ev.calculate(ev_power, current_status)
            # Adjust power setpoint using the controller
            hp_power_setpoint = self.controller.calculate(
                hp_power_setpoint, current_status, ev_power, smart_consumer_voltage, room_temperature
            )

            print("-----------------------------------------------------------")
            print(f"New power setpoint: {hp_power_setpoint}")
            print(f"EV Power Production: {ev_power}")  # Debugging print statement
            print(f"User Status: {'Away' if current_status == 1 else 'Home'}")  # Debugging status
            print("===========================================================")

            results["times"].append(time_clock)
            results["smart_consumer_voltage"].append(smart_consumer_voltage)
            results["temperature"].append(room_temperature)
            results["hp_power_setpoint"].append(hp_power_setpoint)
            results["heat_production"].append(heat_production_from_hp)
            results["ev_power"].append(ev_power)  # Store status

        return results



    def store_results(self, results):
        self.results = results

    def compare_results(self, forecasted_results):
        if self.results is None:
            print("ERROR: No original results to compare!")
            return

        print("Comparing original vs. forecasted simulation results:")
        for key in self.results.keys():
            if key != "times":  # Skip time values
                original_avg = np.mean(self.results[key])
                forecasted_avg = np.mean(forecasted_results[key])
                print(f"{key}: Original Avg = {original_avg:.3f}, Forecasted Avg = {forecasted_avg:.3f}")

            # ✅ Call the plot function
        self.plot_results(self.results, forecasted_results)

    def plot_results(self, original_results, forecasted_results):
        """✅ Updates plot_results to compare original and forecasted simulations."""

        plt.style.use('ggplot')
        _, axs = plt.subplots(3, 2, figsize=(12, 10))

        metrics = [
            ("smart_consumer_voltage", "Voltage [V]", 'blue'),
            ("temperature", "Temperature [°C]", 'red'),
            ("hp_power_setpoint", "Power Setpoint [kW]", 'green'),
            ("heat_production", "Heat Production [kW]", 'orange'),
            ("ev_power", "EV Power [kW]", 'purple'),
        ]

        for i, (metric, ylabel, color) in enumerate(metrics):
            ax = axs[i // 2, i % 2]
            ax.plot(original_results["times"], original_results[metric], color='black', linestyle='dashed',
                    label="Original")
            ax.plot(forecasted_results["times"], forecasted_results[metric], color=color, linestyle='solid',
                    label="Forecasted")
            ax.set_title(f"{metric.replace('_', ' ').title()} Over Time")
            ax.set_ylabel(ylabel)
            ax.legend()

        plt.tight_layout()
        plt.show()

