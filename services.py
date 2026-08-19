import math
import requests
from config import OSM_SEARCH_RADIUS_KM, ROUTING_TIMEOUT, NOMINATIM_TIMEOUT, WEATHER_TIMEOUT, OVERPASS_TIMEOUT

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NWS_POINTS_URL = "https://api.weather.gov/points/{},{}"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OSRM_URL = "https://router.project-osrm.org/route/v1/driving"
HEADERS = {"User-Agent": "PulseGrid/1.0 (emergency resource planning research prototype)", "Accept": "application/json"}


def _float(value):
    try:
        value = float(value)
        return value if math.isfinite(value) else None
    except (TypeError, ValueError):
        return None


def _valid(lat, lon):
    lat, lon = _float(lat), _float(lon)
    return lat is not None and lon is not None and -90 <= lat <= 90 and -180 <= lon <= 180


def _json(response):
    try:
        data = response.json()
        return data if isinstance(data, dict) else None
    except (ValueError, TypeError):
        return None


def get_city_coordinates(city_name):
    if not isinstance(city_name, str) or not city_name.strip():
        return None

    try:
        response = requests.get(
            NOMINATIM_URL,
            params={"q": city_name, "format": "json", "limit": 1, "countrycodes": "us"},
            headers=HEADERS,
            timeout=NOMINATIM_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list) or not data:
            return None

        lat, lon = _float(data[0].get("lat")), _float(data[0].get("lon"))
        return (lat, lon) if _valid(lat, lon) else None
    except (requests.RequestException, ValueError, TypeError, KeyError):
        return None


def get_weather(latitude, longitude):
    if not _valid(latitude, longitude):
        return {"success": False, "error": "Invalid coordinates."}

    try:
        point = requests.get(
            NWS_POINTS_URL.format(latitude, longitude),
            headers=HEADERS,
            timeout=WEATHER_TIMEOUT
        )
        point.raise_for_status()
        point_data = _json(point)
        forecast_url = point_data.get("properties", {}).get("forecast") if point_data else None

        if not forecast_url:
            return {"success": False, "error": "No NWS forecast was returned."}

        forecast = requests.get(
            forecast_url,
            headers=HEADERS,
            timeout=WEATHER_TIMEOUT
        )
        forecast.raise_for_status()
        data = _json(forecast)
        periods = data.get("properties", {}).get("periods", []) if data else []

        if not periods:
            return {"success": False, "error": "No forecast periods were returned."}

        period = periods[0]
        precipitation = period.get("probabilityOfPrecipitation", {}).get("value")

        return {
            "success": True,
            "temperature": _float(period.get("temperature")),
            "temperature_unit": period.get("temperatureUnit"),
            "description": period.get("shortForecast"),
            "wind_speed": period.get("windSpeed"),
            "wind_direction": period.get("windDirection"),
            "precipitation_probability": _float(precipitation),
            "forecast_period": period.get("name"),
            "error": None
        }
    except (requests.RequestException, ValueError, TypeError, KeyError) as error:
        return {"success": False, "error": str(error)}


def _overpass_query(latitude, longitude, radius):
    return f"""
[out:json][timeout:25];
(
node["amenity"="fire_station"](around:{radius},{latitude},{longitude});
way["amenity"="fire_station"](around:{radius},{latitude},{longitude});
node["amenity"="hospital"](around:{radius},{latitude},{longitude});
way["amenity"="hospital"](around:{radius},{latitude},{longitude});
way["highway"](around:{radius},{latitude},{longitude});
);
out center tags;
"""


def get_osm_facilities(latitude, longitude, radius_km=OSM_SEARCH_RADIUS_KM):
    empty = {"success": False, "ems": [], "hospitals": [], "roads": [], "error": None}

    if not _valid(latitude, longitude):
        empty["error"] = "Invalid coordinates."
        return empty

    try:
        response = requests.post(
            OVERPASS_URL,
            data=_overpass_query(latitude, longitude, int(radius_km * 1000)),
            headers=HEADERS,
            timeout=OVERPASS_TIMEOUT
        )
        response.raise_for_status()
        data = _json(response)

        if not data:
            empty["error"] = "Invalid OpenStreetMap response."
            return empty

        ems, hospitals, roads = [], [], []

        for element in data.get("elements", []):
            tags = element.get("tags", {})
            center = element.get("center", {})
            lat = _float(element.get("lat", center.get("lat")))
            lon = _float(element.get("lon", center.get("lon")))

            if not _valid(lat, lon):
                continue

            item = {
                "id": element.get("id"),
                "name": tags.get("name"),
                "latitude": lat,
                "longitude": lon
            }

            if tags.get("amenity") == "fire_station":
                item["name"] = item["name"] or "Fire Station"
                item["type"] = "fire_station"
                ems.append(item)
            elif tags.get("amenity") == "hospital":
                item["name"] = item["name"] or "Hospital"
                item["type"] = "hospital"
                hospitals.append(item)
            elif tags.get("highway"):
                item["name"] = item["name"] or tags["highway"]
                item["type"] = tags["highway"]
                roads.append(item)

        return {
            "success": True,
            "ems": ems,
            "hospitals": hospitals,
            "roads": roads,
            "error": None
        }
    except (requests.RequestException, ValueError, TypeError, KeyError) as error:
        empty["error"] = str(error)
        return empty


def get_route_time(origin_latitude, origin_longitude, destination_latitude, destination_longitude):
    if not _valid(origin_latitude, origin_longitude) or not _valid(destination_latitude, destination_longitude):
        return {"success": False, "duration_minutes": None, "distance_km": None, "error": "Invalid coordinates."}

    coordinates = f"{origin_longitude},{origin_latitude};{destination_longitude},{destination_latitude}"

    try:
        response = requests.get(
            f"{OSRM_URL}/{coordinates}",
            params={"overview": "false", "steps": "false", "alternatives": "false"},
            headers=HEADERS,
            timeout=ROUTING_TIMEOUT
        )
        response.raise_for_status()
        data = _json(response)

        if not data or data.get("code") != "Ok" or not data.get("routes"):
            return {"success": False, "duration_minutes": None, "distance_km": None, "error": "No usable route returned."}

        route = data["routes"][0]
        seconds = _float(route.get("duration"))
        meters = _float(route.get("distance"))

        if seconds is None or meters is None:
            return {"success": False, "duration_minutes": None, "distance_km": None, "error": "Incomplete route data."}

        return {
            "success": True,
            "duration_minutes": seconds / 60,
            "distance_km": meters / 1000,
            "duration_seconds": seconds,
            "distance_meters": meters,
            "error": None
        }
    except (requests.RequestException, ValueError, TypeError, KeyError) as error:
        return {"success": False, "duration_minutes": None, "distance_km": None, "error": str(error)}


def build_route_time_matrix(facilities, demand_zones):
    matrix = []
    distance_matrix = []
    successful, failed = 0, 0

    for facility in facilities or []:
        times, distances = [], []

        for zone in demand_zones or []:
            route = get_route_time(
                facility.get("latitude"),
                facility.get("longitude"),
                zone.get("latitude"),
                zone.get("longitude")
            )

            if route["success"]:
                times.append(route["duration_minutes"])
                distances.append(route["distance_km"])
                successful += 1
            else:
                times.append(None)
                distances.append(None)
                failed += 1

        matrix.append(times)
        distance_matrix.append(distances)

    return {
        "success": successful > 0 or failed == 0,
        "matrix": matrix,
        "distance_matrix_km": distance_matrix,
        "successful_routes": successful,
        "failed_routes": failed,
        "error": None if not failed else f"{failed} route requests failed."
    }
