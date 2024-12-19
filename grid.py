"""Electricity grid model."""


def electric_grid_function(power_setpoint: float) -> float:
    """A simple function to model the electric grid."""
    voltage = 5000 / power_setpoint  # Voltage as a function of power setpoint
    return voltage