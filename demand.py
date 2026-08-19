import pandas as pd
import numpy as np
from datetime import datetime
from config import DEMO_RECORD_COUNT, RANDOM_SEED, DEMAND_GRID_SIZE


def prepare_demand_data(records):
    if records is None:
        return pd.DataFrame()
    data = records.copy() if isinstance(records, pd.DataFrame) else pd.DataFrame(records)
    aliases = {"datetime": "timestamp", "date_time": "timestamp", "call_time": "timestamp", "lat": "latitude", "lon": "longitude", "lng": "longitude"}
    data.rename(columns={k: v for k, v in aliases.items() if k in data.columns and v not in data.columns}, inplace=True)
    required = ["timestamp", "latitude", "longitude"]
    if any(c not in data.columns for c in required):
        return pd.DataFrame()
    data["timestamp"] = pd.to_datetime(data["timestamp"], errors="coerce")
    data["latitude"] = pd.to_numeric(data["latitude"], errors="coerce")
    data["longitude"] = pd.to_numeric(data["longitude"], errors="coerce")
    data.dropna(subset=required, inplace=True)
    data = data[data["latitude"].between(-90, 90) & data["longitude"].between(-180, 180)].copy()
    data["hour"] = data["timestamp"].dt.hour
    data["day_of_week"] = data["timestamp"].dt.dayofweek
    data["month"] = data["timestamp"].dt.month
    return data


def create_demo_records(city=None, coordinates=None, count=DEMO_RECORD_COUNT):
    rng = np.random.default_rng(RANDOM_SEED)
    latitude, longitude = coordinates or (35.2271, -80.8431)
    centers = [(latitude, longitude), (latitude + .035, longitude - .04), (latitude - .04, longitude + .035), (latitude + .055, longitude + .045)]
    selected = rng.choice(4, size=count, p=[.42, .25, .20, .13])
    base = pd.Timestamp(datetime.now().replace(minute=0, second=0, microsecond=0))
    records = []
    for i in selected:
        lat, lon = centers[i]
        records.append({"timestamp": base - pd.Timedelta(hours=int(rng.integers(0, 24 * 90))), "latitude": lat + rng.normal(0, .012), "longitude": lon + rng.normal(0, .015), "source": "SIMULATED DEMO DATA"})
    return prepare_demand_data(records)


def create_demand_grid(records, latitude, longitude, grid_size=DEMAND_GRID_SIZE, radius=.12):
    if records is None or records.empty:
        return pd.DataFrame()
    min_lat, max_lat = latitude - radius, latitude + radius
    min_lon, max_lon = longitude - radius, longitude + radius
    filtered = records[records["latitude"].between(min_lat, max_lat) & records["longitude"].between(min_lon, max_lon)].copy()
    if filtered.empty:
        return pd.DataFrame()
    filtered["latitude_grid"] = np.floor((filtered["latitude"] - min_lat) / (2 * radius) * grid_size).clip(0, grid_size - 1).astype(int)
    filtered["longitude_grid"] = np.floor((filtered["longitude"] - min_lon) / (2 * radius) * grid_size).clip(0, grid_size - 1).astype(int)
    return filtered.groupby(["latitude_grid", "longitude_grid"]).size().reset_index(name="demand")


def calculate_historical_demand(records, hour=None, day_of_week=None):
    if records is None or records.empty:
        return pd.DataFrame()
    filtered = records.copy()
    if hour is not None:
        filtered = filtered[filtered["hour"] == hour]
    if day_of_week is not None:
        filtered = filtered[filtered["day_of_week"] == day_of_week]
    if filtered.empty or "latitude_grid" not in filtered.columns:
        return pd.DataFrame()
    return filtered.groupby(["latitude_grid", "longitude_grid"]).size().reset_index(name="historical_demand")


def build_demand_zones(records, coordinates, grid_size=DEMAND_GRID_SIZE):
    if records is None or records.empty or not coordinates:
        return pd.DataFrame()
    latitude, longitude = coordinates
    grid = create_demand_grid(prepare_demand_data(records), latitude, longitude, grid_size)
    if grid.empty:
        return pd.DataFrame()
    radius = .12
    min_lat, min_lon = latitude - radius, longitude - radius
    grid["latitude"] = min_lat + ((grid["latitude_grid"] + .5) / grid_size) * 2 * radius
    grid["longitude"] = min_lon + ((grid["longitude_grid"] + .5) / grid_size) * 2 * radius
    grid["historical_demand"] = grid["demand"]
    grid["priority"] = pd.qcut(grid["historical_demand"].rank(method="first"), 3, labels=["Low", "Medium", "High"]).astype(str) if len(grid) >= 3 else "Medium"
    return grid[["latitude", "longitude", "historical_demand", "priority"]].sort_values("historical_demand", ascending=False).reset_index(drop=True)


def predict_demand(zones, weather=None, mode="Current conditions", weather_factor=1.0, traffic_factor=1.0):
    if zones is None or zones.empty:
        return pd.DataFrame()
    prediction = zones.copy()
    if weather is not None:
        text = str(weather).lower()
        if any(x in text for x in ["storm", "thunder", "heavy rain", "snow"]):
            weather_factor = max(weather_factor, 1.15)
        elif any(x in text for x in ["rain", "showers"]):
            weather_factor = max(weather_factor, 1.08)
    if mode == "Historical conditions":
        weather_factor = traffic_factor = 1.0
    prediction["predicted_demand"] = (prediction["historical_demand"] * weather_factor * traffic_factor).clip(lower=0)
    return prediction


def rank_demand_zones(predicted_demand):
    if predicted_demand is None or predicted_demand.empty:
        return pd.DataFrame()
    ranked = predicted_demand.sort_values("predicted_demand", ascending=False).reset_index(drop=True).copy()
    ranked["priority_rank"] = np.arange(1, len(ranked) + 1)
    return ranked
