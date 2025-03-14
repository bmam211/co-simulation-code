"""Co-simulation framework module. Contains Model and Manager classes for running the co-simulation."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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
        self.user = models[4]
        self.controller = models[-1]  # Last model is the controller
        self.settings_configuration = settings_configuration

    def run_simulation(self):
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
        passive_consumer_power_setpoints = pd.read_csv(
            config['InitializationSettings']['passive_consumers_power_setpoints'], index_col="snapshots",
            parse_dates=True,
        )

        # Smart consumer
        hp_power_setpoint = config['InitializationSettings']['initial_conditions']['heat_pump']['power_set_point']
        room_temperature = config['InitializationSettings']['initial_conditions']['room']['temperature']
        ev_power = config['InitializationSettings']['initial_conditions']['ev']['power']  # Initialize once

        # Initialize lists to store data for plotting
        times = []
        smart_consumer_power_setpoint_over_time = []
        smart_consumer_voltage_over_time = []
        heat_pump_heat_output_over_time = []
        temperature_over_time = []
        ev_over_time = []
        status_over_time = []  # Store status for plotting

        print("===============================================================")
        print(f"Starting simulation at time {start_time}, ending at {end_time}, with time step delta_t: {delta_t}\n")
        print(
            f"Initial heat pump power_setpoint: {hp_power_setpoint}\nInitial heat pump temperature: {room_temperature}\n")
        print("===============================================================")

        time_steps = int((end_time - start_time) / delta_t)
        status = self.user.calculate(delta_t)

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

            times.append(time_clock)
            smart_consumer_power_setpoint_over_time.append(hp_power_setpoint)
            smart_consumer_voltage_over_time.append(smart_consumer_voltage)
            heat_pump_heat_output_over_time.append(heat_production_from_hp)
            temperature_over_time.append(room_temperature)
            ev_over_time.append(ev_power)  # Store updated EV power
            status_over_time.append(current_status)  # Store status

        self.plot_results(
            times,
            smart_consumer_voltage_over_time,
            temperature_over_time,
            smart_consumer_power_setpoint_over_time,
            heat_pump_heat_output_over_time,
            ev_over_time,  # Include EV data in the plot
            status_over_time,  # Include user status in the plot
            config_id,
        )

    def plot_results(self, times, voltages, temperatures, power_setpoints, heat_productions, ev_production, status_over_time, config_id):
        plt.style.use('ggplot')
        _, axs = plt.subplots(3, 2, figsize=(12, 10))  # Adjusted for 6 subplots

        plots = [
            (axs[0, 0], times, voltages, "Voltage Over Time", "Time [min]", "Voltage [V]", 'blue'),
            (axs[0, 1], times, temperatures, "Temperature Over Time", "Time [min]", "Temperature [°C]", 'red'),
            (axs[1, 0], times, power_setpoints, "Heat Pump Power Setpoint Over Time", "Time [min]", "Power Setpoint [kW]", 'green'),
            (axs[1, 1], times, heat_productions, "Heat Production Over Time", "Time [min]", "Heat Production [kW]", 'orange'),
            (axs[2, 0], times, ev_production, "EV Power Production Over Time", "Time [min]", "EV Power [kW]", 'purple'),
            (axs[2, 1], times, status_over_time, "User Status Over Time", "Time [min]", "Status (1=Away, 0=Home)", 'black')
        ]

        for ax, x, y, title, xlabel, ylabel, color in plots:
            ax.plot(x, y, color=color)
            ax.set_title(title, color='black')

        plt.tight_layout()
        plt.savefig(f"results_config{config_id}.png")
