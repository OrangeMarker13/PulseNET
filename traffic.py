import requests


def get_route_time(
    start_latitude,
    start_longitude,
    end_latitude,
    end_longitude
):
    url = (
        "https://router.project-osrm.org/route/v1/driving/"
        f"{start_longitude},{start_latitude};"
        f"{end_longitude},{end_latitude}"
    )

    params = {
        "overview": "false",
        "steps": "false"
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        route_data = response.json()

        if route_data.get("code") != "Ok":
            return None

        routes = route_data.get("routes", [])

        if not routes:
            return None

        route = routes[0]

        return {
            "duration_seconds": route.get("duration"),
            "distance_meters": route.get("distance"),
            "source": "OpenStreetMap routing",
            "status": "route_estimate"
        }

    except (requests.RequestException, KeyError, ValueError):
        return None


def get_multiple_route_times(
    start_location,
    destinations
):
    results = []

    for destination in destinations:
        route = get_route_time(
            start_location["latitude"],
            start_location["longitude"],
            destination["latitude"],
            destination["longitude"]
        )

        if route is None:
            continue

        results.append({
            "destination": destination,
            "route": route
        })

    return results
