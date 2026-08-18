import requests


OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def get_ems_locations(
    latitude,
    longitude,
    radius=20000
):
    query = f"""
    [out:json];
    (
        node
            (around:{radius},{latitude},{longitude})
            ["amenity"="fire_station"];

        way
            (around:{radius},{latitude},{longitude})
            ["amenity"="fire_station"];

        node
            (around:{radius},{latitude},{longitude})
            ["emergency"="ambulance_station"];

        way
            (around:{radius},{latitude},{longitude})
            ["emergency"="ambulance_station"];
    );
    out center;
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

        locations = []

        for element in data.get(
            "elements",
            []
        ):
            tags = element.get(
                "tags",
                {}
            )

            element_latitude = element.get(
                "lat"
            )

            element_longitude = element.get(
                "lon"
            )

            center = element.get(
                "center",
                {}
            )

            if element_latitude is None:
                element_latitude = center.get(
                    "lat"
                )

            if element_longitude is None:
                element_longitude = center.get(
                    "lon"
                )

            if (
                element_latitude is None
                or element_longitude is None
            ):
                continue

            locations.append(
                {
                    "id": element.get(
                        "id"
                    ),
                    "name": tags.get(
                        "name",
                        "EMS facility"
                    ),
                    "latitude": element_latitude,
                    "longitude": element_longitude,
                    "facility_type": tags.get(
                        "amenity",
                        tags.get(
                            "emergency",
                            "unknown"
                        )
                    ),
                    "operator": tags.get(
                        "operator"
                    )
                }
            )

        return locations

    except (
        requests.RequestException,
        ValueError
    ):
        return []


def filter_ems_locations(
    locations
):
    if not locations:
        return []

    filtered = []

    for location in locations:
        latitude = location.get(
            "latitude"
        )

        longitude = location.get(
            "longitude"
        )

        if latitude is None:
            continue

        if longitude is None:
            continue

        filtered.append(
            location
        )

    return filtered


def get_ems_summary(
    locations
):
    if not locations:
        return {
            "available": False,
            "location_count": 0
        }

    return {
        "available": True,
        "location_count": len(
            locations
        )
    }
