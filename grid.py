"""Electricity grid model."""
import pandas as pd


def electric_grid_function(passive_consumers_power_setpoint: pd.DataFrame, smart_consumer_power_setpoint: float, time_step: int) -> dict[str, float]:
    """A simple function to model the electric grid."""
    voltages = {"time step": passive_consumers_power_setpoint.index[time_step], "consumers": {}}

    for passive_consumer in passive_consumers_power_setpoint.columns:
        voltages["consumers"][passive_consumer] = float(
            passive_consumers_power_setpoint.iloc[time_step, passive_consumers_power_setpoint.columns.get_loc(passive_consumer)]
        )

    voltages["consumers"]["smart_consumer"] = 5000 / smart_consumer_power_setpoint  # Voltage as a function of power setpoint

    return voltages
