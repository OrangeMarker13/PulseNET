import requests


def search_hospitals(
    latitude,
    longitude,
    radius=30000
):
    query = f"""
    [out:json][timeout:20];
    (
        node["amenity"="hospital"]
        (around:{radius},{latitude},{longitude});

        way["amenity"="hospital"]
        (around:{radius},{latitude},{longitude});

        relation["amenity"="hospital"]
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

        hospitals = []

        for element in data.get("elements", []):
            tags = element.get("tags", {})

            if "lat" in element and "lon" in element:
                hospital_latitude = element["lat"]
                hospital_longitude = element["lon"]

            elif "center" in element:
                hospital_latitude = element["center"]["lat"]
                hospital_longitude = element["center"]["lon"]

            else:
                continue

            hospitals.append(
                {
                    "name": tags.get(
                        "name",
                        "Unnamed hospital"
                    ),
                    "latitude": hospital_latitude,
                    "longitude": hospital_longitude,
                    "emergency": tags.get(
                        "emergency"
                    ),
                    "operator": tags.get(
                        "operator"
                    ),
                    "source": "OpenStreetMap"
                }
            )

        return hospitals

    except (
        requests.RequestException,
        KeyError,
        ValueError
    ):
        return []


def filter_emergency_hospitals(hospitals):
    emergency_hospitals = []

    for hospital in hospitals:
        emergency_status = str(
            hospital.get("emergency", "")
        ).lower()

        if emergency_status in {
            "yes",
            "emergency_department",
            "emergency"
        }:
            emergency_hospitals.append(hospital)

    return emergency_hospitals
