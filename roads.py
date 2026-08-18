import requests


def get_road_network(
    latitude,
    longitude,
    radius=10000
):
    query = f"""
    [out:json][timeout:30];
    (
        way["highway"]
        (around:{radius},{latitude},{longitude});
    );
    out geom tags;
    """

    url = "https://overpass-api.de/api/interpreter"

    try:
        response = requests.post(
            url,
            data=query,
            timeout=40
        )

        response.raise_for_status()

        data = response.json()

        roads = []

        for element in data.get("elements", []):
            geometry = element.get("geometry")

            if not geometry:
                continue

            tags = element.get("tags", {})

            roads.append(
                {
                    "id": element.get("id"),
                    "name": tags.get(
                        "name",
                        "Unnamed road"
                    ),
                    "road_type": tags.get(
                        "highway"
                    ),
                    "max_speed": tags.get(
                        "maxspeed"
                    ),
                    "lanes": tags.get(
                        "lanes"
                    ),
                    "geometry": geometry,
                    "source": "OpenStreetMap"
                }
            )

        return roads

    except (
        requests.RequestException,
        KeyError,
        ValueError
    ):
        return []


def filter_drivable_roads(roads):
    excluded_types = {
        "footway",
        "path",
        "pedestrian",
        "cycleway",
        "steps",
        "bridleway",
        "corridor"
    }

    return [
        road
        for road in roads
        if road.get("road_type") not in excluded_types
    ]


def get_road_summary(roads):
    summary = {}

    for road in roads:
        road_type = road.get(
            "road_type",
            "unknown"
        )

        summary[road_type] = (
            summary.get(road_type, 0) + 1
        )

    return summary
