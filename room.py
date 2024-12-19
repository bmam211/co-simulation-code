"""Room model."""


class RoomFunction:
    """A class to model the temperature of a room over time."""
    def __init__(self, settings_configuration: dict):
        """Initialize the Room with thermal properties and initial temperature."""
        config = settings_configuration

        # Store variables as class attributes to be tracked during the simulation
        self.delta_t = config['InitializationSettings']['time']['delta_t']
        self.room_temp = config['InitializationSettings']['initial_conditions']['room']['temperature']
        self.outside_temp = config['InitializationSettings']['initial_conditions']['room']['outside_temperature']
        self.room_tc = config['InitializationSettings']['initial_conditions']['room']['thermal_capacitance']
        self.room_tr = config['InitializationSettings']['initial_conditions']['room']['thermal_resistance']

    def __call__(self, heat_production_from_hp: float) -> float:
        """
        Callable method to update the room temperature during the simulation.
        :param heat_production_from_hp: Heat input from the heat pump (W)
        :return: Updated room temperature (°C)
        """
        # Calculate heat loss to the environment
        heat_loss = (self.room_temp - self.outside_temp) / self.room_tr

        # Update room temperature using the discrete-time equation
        self.room_temp += self.delta_t * (heat_production_from_hp - heat_loss) / self.room_tc
        return self.room_temp