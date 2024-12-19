"""Heat pump model."""


def heat_pump_function(power_setpoint: float) -> float:
    """A simple function to model the heat pump."""
    heat_production = 0.5 * power_setpoint  # Heat production as a function of power setpoint
    return heat_production