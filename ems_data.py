import pandas as pd


REQUIRED_COLUMNS = [
    "timestamp",
    "latitude",
    "longitude"
]


def load_ems_csv(file_path):
    try:
        data = pd.read_csv(file_path)
    except (
        FileNotFoundError,
        pd.errors.EmptyDataError,
        pd.errors.ParserError
    ):
        return pd.DataFrame()

    return standardize_ems_data(data)


def standardize_ems_data(data):
    if data is None:
        return pd.DataFrame()

    if not isinstance(data, pd.DataFrame):
        return pd.DataFrame()

    data = data.copy()

    column_mapping = {
        "date_time": "timestamp",
        "datetime": "timestamp",
        "call_time": "timestamp",
        "lat": "latitude",
        "lon": "longitude",
        "lng": "longitude"
    }

    data = data.rename(
        columns=column_mapping
    )

    for column in REQUIRED_COLUMNS:
        if column not in data.columns:
            return pd.DataFrame()

    data["timestamp"] = pd.to_datetime(
        data["timestamp"],
        errors="coerce"
    )

    data["latitude"] = pd.to_numeric(
        data["latitude"],
        errors="coerce"
    )

    data["longitude"] = pd.to_numeric(
        data["longitude"],
        errors="coerce"
    )

    data = data.dropna(
        subset=REQUIRED_COLUMNS
    )

    data = data[
        (data["latitude"] >= -90)
        & (data["latitude"] <= 90)
        & (data["longitude"] >= -180)
        & (data["longitude"] <= 180)
    ]

    return data.reset_index(
        drop=True
    )


def filter_city_area(
    data,
    latitude,
    longitude,
    radius=0.12
):
    if data.empty:
        return pd.DataFrame()

    minimum_latitude = latitude - radius
    maximum_latitude = latitude + radius
    minimum_longitude = longitude - radius
    maximum_longitude = longitude + radius

    filtered = data[
        (data["latitude"] >= minimum_latitude)
        & (data["latitude"] <= maximum_latitude)
        & (data["longitude"] >= minimum_longitude)
        & (data["longitude"] <= maximum_longitude)
    ]

    return filtered.reset_index(
        drop=True
    )


def filter_date_range(
    data,
    start_date,
    end_date
):
    if data.empty:
        return pd.DataFrame()

    filtered = data[
        (data["timestamp"] >= start_date)
        & (data["timestamp"] <= end_date)
    ]

    return filtered.reset_index(
        drop=True
    )


def get_data_summary(data):
    if data.empty:
        return {
            "records": 0,
            "start_date": None,
            "end_date": None
        }

    return {
        "records": len(data),
        "start_date": data[
            "timestamp"
        ].min(),
        "end_date": data[
            "timestamp"
        ].max()
    }


def validate_ems_data(data):
    if data.empty:
        return False

    for column in REQUIRED_COLUMNS:
        if column not in data.columns:
            return False

    if data["timestamp"].isna().any():
        return False

    if data["latitude"].isna().any():
        return False

    if data["longitude"].isna().any():
        return False

    return True
