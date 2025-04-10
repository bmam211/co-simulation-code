def adjust_power(power: float, status: int) -> float:
    """
    Adjusts EV charging power based on user status.
    - If user is home (status = 0) and power < 25000, increase by 500.
    - If power reaches 25000, stop charging.
    - If user is away (status = 1), do not charge (set power to 0).

    Args:
        power (float): Current charging power.
        status (int): User status (0 = home, 1 = away).

    Returns:
        float: Adjusted power value.
    """

    if status == 1:
        return 0  # Stop charging when user is away
    elif power < 25000:
        return min(power + 500, 25000)  # Charge while at home, but cap at 25000
    else:
        return power  # Maintain power at max if already full
