import requests


OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def get_road_network(
    latitude,
    longitude,
    radius=10000
):
    query = f"""
    [out:json];
    way
      (around:{radius},{latitude},{longitude})
      ["highway"];
    out geom;
    """

    try:
        response = requests.post(
            OVERPASS_URL,
            data=query,
            timeout=30
        )

        if response.status_code != 200:
            return []

        data = response.json()

        roads = []

        for element in data.get(
            "elements",
            []
        ):
            tags = element.get(
                "tags",
                {}
            )

            geometry = element.get(
                "geometry",
                []
            )

            if not geometry:
                continue

            roads.append(
                {
                    "id": element.get("id"),
                    "name": tags.get(
                        "name",
                        "Unnamed road"
                    ),
                    "highway_type": tags.get(
                        "highway"
                    ),
                    "maxspeed": tags.get(
                        "maxspeed"
                    ),
                    "lanes": tags.get(
                        "lanes"
                    ),
                    "oneway": tags.get(
                        "oneway"
                    ),
                    "geometry": geometry
                }
            )

        return roads

    except (
        requests.RequestException,
        ValueError
    ):
        return []


def filter_drivable_roads(
    roads
):
    if not roads:
        return []

    excluded_types = {
        "footway",
        "path",
        "cycleway",
        "pedestrian",
        "steps",
        "bridleway"
    }

    filtered = []

    for road in roads:
        road_type = road.get(
            "highway_type"
        )

        if road_type in excluded_types:
            continue

        filtered.append(
            road
        )

    return filtered


def get_road_summary(
    roads
):
    if not roads:
        return {
            "available": False,
            "road_count": 0
        }

    road_types = {}

    for road in roads:
        road_type = road.get(
            "highway_type",
            "unknown"
        )

        road_types[road_type] = (
            road_types.get(
                road_type,
                0
            )
            + 1
        )

    return {
        "available": True,
        "road_count": len(roads),
        "road_types": road_types
    }


def find_road(
    roads,
    road_name
):
    matches = []

    search_name = road_name.lower()

    for road in roads:
        name = road.get(
            "name",
            ""
        )

        if search_name in name.lower():
            matches.append(
                road
            )

    return matches
