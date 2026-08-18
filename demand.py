import pandas as pd
import numpy as np


def prepare_demand_data(records):
    if not records:
        return pd.DataFrame()

    data = pd.DataFrame(records)

    required_columns = [
        "timestamp",
        "latitude",
        "longitude"
    ]

    for column in required_columns:
        if column not in data.columns:
            return pd.DataFrame()

    data["timestamp"] = pd.to_datetime(
        data["timestamp"],
        errors="coerce"
    )

    data = data.dropna(
        subset=[
            "timestamp",
            "latitude",
            "longitude"
        ]
    )

    data["hour"] = data["timestamp"].dt.hour
    data["day_of_week"] = data["timestamp"].dt.dayofweek
    data["month"] = data["timestamp"].dt.month

    return data


def create_demand_grid(
    records,
    latitude,
    longitude,
    grid_size=10,
    radius=0.12
):
    if records.empty:
        return pd.DataFrame()

    minimum_latitude = latitude - radius
    maximum_latitude = latitude + radius

    minimum_longitude = longitude - radius
    maximum_longitude = longitude + radius

    filtered = records[
        (records["latitude"] >= minimum_latitude)
        & (records["latitude"] <= maximum_latitude)
        & (records["longitude"] >= minimum_longitude)
        & (records["longitude"] <= maximum_longitude)
    ].copy()

    if filtered.empty:
        return pd.DataFrame()

    filtered["latitude_grid"] = (
        np.floor(
            (
                filtered["latitude"]
                - minimum_latitude
            )
            / (2 * radius)
            * grid_size
        )
    )

    filtered["longitude_grid"] = (
        np.floor(
            (
                filtered["longitude"]
                - minimum_longitude
            )
            / (2 * radius)
            * grid_size
        )
    )

    grid = (
        filtered
        .groupby(
            [
                "latitude_grid",
                "longitude_grid"
            ]
        )
        .size()
        .reset_index(name="demand")
    )

    return grid


def calculate_historical_demand(
    records,
    hour=None,
    day_of_week=None
):
    if records.empty:
        return pd.DataFrame()

    filtered = records.copy()

    if hour is not None:
        filtered = filtered[
            filtered["hour"] == hour
        ]

    if day_of_week is not None:
        filtered = filtered[
            filtered["day_of_week"] == day_of_week
        ]

    if filtered.empty:
        return pd.DataFrame()

    demand = (
        filtered
        .groupby(
            [
                "latitude_grid",
                "longitude_grid"
            ]
        )
        .size()
        .reset_index(name="historical_demand")
    )

    return demand


def predict_demand(
    historical_demand,
    weather_factor=1.0,
    traffic_factor=1.0
):
    if historical_demand.empty:
        return pd.DataFrame()

    prediction = historical_demand.copy()

    prediction["predicted_demand"] = (
        prediction["historical_demand"]
        * weather_factor
        * traffic_factor
    )

    prediction["predicted_demand"] = (
        prediction["predicted_demand"]
        .clip(lower=0)
    )

    return prediction


def rank_demand_zones(
    predicted_demand
):
    if predicted_demand.empty:
        return pd.DataFrame()

    ranked = predicted_demand.copy()

    ranked = ranked.sort_values(
        "predicted_demand",
        ascending=False
    )

    ranked["priority_rank"] = range(
        1,
        len(ranked) + 1
    )

    return ranked
