import requests


OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def get_hospitals(
    latitude,
    longitude,
    radius=20000
):
    query = f"""
    [out:json];
    (
        node
            (around:{radius},{latitude},{longitude})
            ["amenity"="hospital"];

        way
            (around:{radius},{latitude},{longitude})
            ["amenity"="hospital"];

        relation
            (around:{radius},{latitude},{longitude})
            ["amenity"="hospital"];
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

        hospitals = []

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

            hospitals.append(
                {
                    "id": element.get(
                        "id"
                    ),
                    "name": tags.get(
                        "name",
                        "Unnamed hospital"
                    ),
                    "latitude": element_latitude,
                    "longitude": element_longitude,
                    "emergency": tags.get(
                        "emergency"
                    ),
                    "phone": tags.get(
                        "phone"
                    ),
                    "website": tags.get(
                        "website"
                    )
                }
            )

        return hospitals

    except (
        requests.RequestException,
        ValueError
    ):
        return []


def filter_emergency_hospitals(
    hospitals
):
    if not hospitals:
        return []

    filtered = []

    for hospital in hospitals:
        emergency_status = hospital.get(
            "emergency"
        )

        if emergency_status in {
            "yes",
            "24/7"
        }:
            filtered.append(
                hospital
            )

    return filtered


def get_hospital_summary(
    hospitals
):
    if not hospitals:
        return {
            "available": False,
            "hospital_count": 0
        }

    return {
        "available": True,
        "hospital_count": len(
            hospitals
        )
    }
