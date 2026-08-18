import requests
import math


OSRM_URL = "https://router.project-osrm.org"


def build_route_url(
    start_latitude,
    start_longitude,
    end_latitude,
    end_longitude
):
    return (
        f"{OSRM_URL}/route/v1/driving/"
        f"{start_longitude},{start_latitude};"
        f"{end_longitude},{end_latitude}"
        "?overview=false"
    )


def get_travel_time(
    start_latitude,
    start_longitude,
    end_latitude,
    end_longitude
):
    url = build_route_url(
        start_latitude,
        start_longitude,
        end_latitude,
        end_longitude
    )

    try:
        response = requests.get(
            url,
            timeout=10
        )

        if response.status_code != 200:
            return None

        data = response.json()

        routes = data.get(
            "routes",
            []
        )

        if not routes:
            return None

        route = routes[0]

        duration_seconds = route.get(
            "duration"
        )

        distance_meters = route.get(
            "distance"
        )

        if duration_seconds is None:
            return None

        return {
            "travel_time_minutes": (
                duration_seconds / 60
            ),
            "distance_km": (
                distance_meters / 1000
                if distance_meters is not None
                else None
            ),
            "source": "OSRM"
        }

    except (
        requests.RequestException,
        ValueError
    ):
        return None


def calculate_straight_line_distance(
    latitude_1,
    longitude_1,
    latitude_2,
    longitude_2
):
    latitude_1 = math.radians(
        latitude_1
    )

    latitude_2 = math.radians(
        latitude_2
    )

    latitude_difference = math.radians(
        latitude_2 - latitude_1
    )

    longitude_difference = math.radians(
        longitude_2 - longitude_1
    )

    value = (
        math.sin(latitude_difference / 2) ** 2
        + math.cos(latitude_1)
        * math.cos(latitude_2)
        * math.sin(longitude_difference / 2) ** 2
    )

    value = min(
        1,
        max(
            0,
            value
        )
    )

    return (
        6371
        * 2
        * math.asin(
            math.sqrt(value)
        )
    )


def build_travel_time_matrix(
    demand_zones,
    candidate_locations
):
    matrix = []

    for demand_zone in demand_zones:
        row = []

        for location in candidate_locations:
            result = get_travel_time(
                location["latitude"],
                location["longitude"],
                demand_zone["latitude"],
                demand_zone["longitude"]
            )

            if result is None:
                row.append(None)
            else:
                row.append(
                    result[
                        "travel_time_minutes"
                    ]
                )

        matrix.append(row)

    return matrix


def summarize_traffic(
    travel_times
):
    values = []

    for row in travel_times:
        for value in row:
            if value is not None:
                values.append(value)

    if not values:
        return {
            "available": False
        }

    return {
        "available": True,
        "average_travel_time": sum(values)
        / len(values),
        "minimum_travel_time": min(values),
        "maximum_travel_time": max(values),
        "routes_evaluated": len(values)
    }
