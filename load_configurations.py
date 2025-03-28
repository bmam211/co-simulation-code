"""Functions for loading simulation configurations from YAML files."""
import os

import pandas as pd
import yaml


def load_configurations(configurations_folder_path: str, use_forecasted: bool) -> tuple[dict, list[dict[str, dict]]]:
    """Load configurations from YAML files in the specified folder path."""

    config_files = [f for f in os.listdir(configurations_folder_path) if f.endswith('.yaml')]
    initialization_configurations = {}

    for config_file in config_files:
        if config_file == 'controller_config.yaml':
            with open(os.path.join(configurations_folder_path, config_file), 'r') as file:
                controller_configuration = yaml.safe_load(file)
            continue
        config_path = os.path.join(configurations_folder_path, config_file)
        with open(config_path, 'r') as file:
            config_data = yaml.safe_load(file)
            try:
                config_id = config_data["InitializationSettings"]["config_id"]
            except KeyError as e:
                raise KeyError(f"Configuration file {config_file} is missing the 'config_id' key.") from e
            initialization_configurations[f"config {config_id}"] = config_data

    dataset_file = "combined_active_power_forecasted.csv" if use_forecasted else "combined_active_power.csv"
    dataset_path = os.path.join('./data', dataset_file)

    try:
        df = pd.read_csv(dataset_path, index_col="snapshots", parse_dates=True)
    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset file {dataset_path} not found.")

    return controller_configuration, initialization_configurations, df