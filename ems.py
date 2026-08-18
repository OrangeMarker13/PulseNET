import requests


def search_ems_locations(
    latitude,
    longitude,
    radius=25000
):
    query = f"""
    [out:json][timeout:20];
    (
        node["amenity"="fire_station"]
        (around:{radius},{latitude},{longitude});

        way["amenity"="fire_station"]
        (around:{radius},{latitude},{longitude});

        relation["amenity"="fire_station"]
        (around:{radius},{latitude},{longitude});
    );
    out center tags;
    """

    url = "https://overpass-api.de/api/interpreter"

    try:
        response = requests.post(
            url,
            data=query,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        locations = []

        for element in data.get("elements", []):
            tags = element.get("tags", {})

            if "lat" in element and "lon" in element:
                location_latitude = element["lat"]
                location_longitude = element["lon"]

            elif "center" in element:
                location_latitude = element["center"]["lat"]
                location_longitude = element["center"]["lon"]

            else:
                continue

            locations.append(
                {
                    "name": tags.get(
                        "name",
                        "Unnamed EMS location"
                    ),
                    "latitude": location_latitude,
                    "longitude": location_longitude,
                    "amenity": tags.get(
                        "amenity",
                        "fire_station"
                    ),
                    "emergency": tags.get(
                        "emergency"
                    ),
                    "source": "OpenStreetMap"
                }
            )

        return locations

    except (
        requests.RequestException,
        KeyError,
        ValueError
    ):
        return []


def filter_ems_locations(locations):
    filtered_locations = []

    for location in locations:
        name = location["name"].lower()
        emergency_type = str(
            location.get("emergency", "")
        ).lower()

        if (
            "ems" in name
            or "ambulance" in name
            or "rescue" in name
            or emergency_type in {
                "ambulance_station",
                "ambulance",
                "rescue"
            }
        ):
            filtered_locations.append(location)

    return filtered_locations
