import requests


def get_city_coordinates(city_name):
    search_url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": f"{city_name}, North Carolina, USA",
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": "PulseGrid emergency planning research application"
    }

    try:
        response = requests.get(
            search_url,
            params=params,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        results = response.json()

        if not results:
            return None

        result = results[0]

        return {
            "latitude": float(result["lat"]),
            "longitude": float(result["lon"]),
            "display_name": result.get("display_name"),
            "source": "OpenStreetMap Nominatim"
        }

    except (requests.RequestException, KeyError, ValueError):
        return None
