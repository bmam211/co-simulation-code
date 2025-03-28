import numpy as np  # Import NumPy first


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