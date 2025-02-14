"""Electricity grid model."""
import numpy as np
import pandas as pd
from power_grid_model import (
    LoadGenType,
    PowerGridModel,
    ComponentType,
    initialize_array,
    DatasetType,
)


def electric_grid_function(
    active_power_df: pd.DataFrame,
    smart_consumer_power_setpoint: float,
    grid_topology: pd.DataFrame,
    time_step: pd.DatetimeIndex,
    smart_consumer_name_in_active_power_df: str = "Customer_95",
) -> dict[str, float]:
    """Function to simulate power flow in an electricity grid."""
    # Initialize voltages dictionary to store consumer voltages.
    voltages = {"time step": time_step, "consumers": {}}

    # Process active power data: convert active power values from kW to W and and remove unit "(kW)" from column names.
    active_power_df = process_active_power_data_frame(active_power_df)

    # Update active power data frame with smart consumer power setpoint
    updated_active_power_dataframe = update_active_power_data_frame_with_smart_consumer_power_setpoint(
        active_power_df, smart_consumer_name_in_active_power_df, smart_consumer_power_setpoint, time_step,
    )

    # Run power flow for the given time step
    consumer_voltage_dict = run_power_flow(grid_topology, updated_active_power_dataframe, time_step)

    # Update voltages dictionary with consumer voltages
    voltages["consumers"].update(consumer_voltage_dict)

    # Update voltages dictionary with smart consumer voltage and rename the key to "smart_consumer"
    voltages["consumers"]["smart_consumer"] = voltages["consumers"].pop(smart_consumer_name_in_active_power_df)

    return voltages


def update_active_power_data_frame_with_smart_consumer_power_setpoint(
    active_power_df: pd.DataFrame,
    smart_consumer_name_in_active_power_df: str,
    smart_consumer_power_setpoint: float,
    time_step: pd.DatetimeIndex,
) -> pd.DataFrame:
    """Update active power data frame with smart consumer power setpoint."""
    active_power_df.loc[time_step, smart_consumer_name_in_active_power_df] = smart_consumer_power_setpoint
    return active_power_df

def run_power_flow(
    grid_topology_df: pd.DataFrame,
    active_power_df: pd.DataFrame,
    time_step: pd.DatetimeIndex,
) -> dict[str, float]:
    """Run the power flow for a given time step."""
    # 1. Prepare power flow data
    input_data = prepare_power_flow_data(grid_topology_df, active_power_df, time_step)
    # 2. Initialize power flow model with input data
    model = PowerGridModel(input_data)
    # 3. Run power flow model
    output_data = model.calculate_power_flow()
    # 4. Get node voltages
    voltages = output_data[ComponentType.node]["u_pu"].flatten().tolist()
    consumers = active_power_df.columns
    consumer_voltage_dict = dict(zip(consumers, voltages))

    return consumer_voltage_dict


def prepare_power_flow_data(
    grid_topology_df: pd.DataFrame, active_power_df: pd.DataFrame, time_step: pd.DatetimeIndex,
) -> dict:
    """Prepare the data for the power flow calculation."""

    # Initialize line data
    num_lines = len(grid_topology_df)
    line = initialize_array(DatasetType.input, ComponentType.line, num_lines)
    line["id"] = np.arange(96, 96 + num_lines)
    line["from_node"] = grid_topology_df["FROM"].values
    line["to_node"] = grid_topology_df["TO"].values
    line["from_status"] = np.ones(num_lines)
    line["to_status"] = np.ones(num_lines)
    line["r1"] = grid_topology_df["Raa"].values
    line["x1"] = grid_topology_df["Xaa"].values
    line["c1"] = np.full(num_lines, 10e-6)
    line["tan1"] = np.zeros(num_lines)
    line["i_n"] = grid_topology_df["Imax"].values

    # Initialize node data
    node = initialize_array(DatasetType.input, ComponentType.node, 95)
    node["id"] = np.arange(1, 96)
    node["u_rated"] = [0.23e3] * 95  # Rated voltage (230V)

    # Initialize source (slack Node)
    source = initialize_array(DatasetType.input, ComponentType.source, 1)
    source["id"] = [96 + num_lines + 95]
    source["node"] = [1]  # Slack node
    source["status"] = [1]
    source["u_ref"] = [1.0]  # Reference voltage (p.u.)

    # Initialize load data
    sym_load = initialize_array(DatasetType.input, ComponentType.sym_load, 95)
    sym_load["id"] = np.arange(96 + num_lines, 96 + num_lines + 95)
    sym_load["node"] = np.arange(1, 96)
    sym_load["status"] = np.ones(95)
    sym_load["type"] = np.full(95, LoadGenType.const_power)
    sym_load["p_specified"] = active_power_df.loc[time_step, :].values
    sym_load["q_specified"] = calculate_reactive_power_from_active_power(sym_load["p_specified"])

    return {
        ComponentType.node: node,
        ComponentType.line: line,
        ComponentType.sym_load: sym_load,
        ComponentType.source: source,
    }


def calculate_reactive_power_from_active_power(active_power, power_factor: float =0.95) -> float:
    """Calculate reactive power from active power using a power factor assumed to be 0.95."""
    return active_power * np.tan(np.arccos(power_factor))


def process_active_power_data_frame(active_power_df: pd.DataFrame) -> pd.DataFrame:
    """Convert active power values from kW to W and rename columns."""
    active_power_df = active_power_df * 1e3
    active_power_df.columns = active_power_df.columns.str.replace(" (kW)", "")

    return active_power_df


# # Run script as standalone with no interaction between the models
# if __name__ == "__main__":
#     active_power_file = "data/combined_active_power.csv"
#     grid_topology_file = "data/grid_topology.csv"

#     active_power_df = pd.read_csv(active_power_file, index_col='time')
#     grid_topology_df = pd.read_csv(grid_topology_file)

#     for time_step in active_power_df.index:
#         print(f"Processing Time Step: {time_step}")
#         voltages = electric_grid_function(active_power_df, 5000, grid_topology_df, time_step)
#         print(f"Node Voltages for time step {time_step=}: {voltages}")
