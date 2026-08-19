"""
PulseGrid external services.

This module handles:
- City geocoding through OpenStreetMap Nominatim
- Weather data through the National Weather Service
- EMS facilities, hospitals, and roads through OpenStreetMap Overpass
- Driving route estimates through OSRM

All external requests are isolated here so app.py does not need to contain
separate API clients for each service.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import requests


# ---------------------------------------------------------------------------
# API CONFIGURATION
# ---------------------------------------------------------------------------

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NWS_POINTS_URL = "https://api.weather.gov/points/{lat},{lon}"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OSRM_URL = "https://router.project-osrm.org/route/v1/driving"

DEFAULT_TIMEOUT = 15

USER_AGENT = (
    "PulseGrid/1.0 "
    "(emergency resource planning research prototype)"
)


# ---------------------------------------------------------------------------
# INTERNAL HELPERS
# ---------------------------------------------------------------------------

def _request_headers() -> Dict[str, str]:
    """Return headers used for external API requests."""
    return {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }


def _safe_float(value: Any) -> Optional[float]:
    """Convert a value to float without raising an exception."""
    try:
        if value is None:
            return None

        result = float(value)

        if not math.isfinite(result):
            return None

        return result

    except (TypeError, ValueError):
        return None


def _valid_coordinates(latitude: Any, longitude: Any) -> bool:
    """Check whether latitude and longitude are valid."""
    lat = _safe_float(latitude)
    lon = _safe_float(longitude)

    if lat is None or lon is None:
        return False

    return -90 <= lat <= 90 and -180 <= lon <= 180


def _safe_json(response: requests.Response) -> Optional[Dict[str, Any]]:
    """Safely decode a JSON response."""
    try:
        data = response.json()

        if isinstance(data, dict):
            return data

        return None

    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# CITY COORDINATES
# ---------------------------------------------------------------------------

def get_city_coordinates(
    city_name: str,
    timeout: int = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """
    Convert a city name into geographic coordinates.

    Returns:
        {
            "success": bool,
            "city": str,
            "latitude": float | None,
            "longitude": float | None,
            "display_name": str | None,
            "error": str | None
        }
    """

    result = {
        "success": False,
        "city": city_name,
        "latitude": None,
        "longitude": None,
        "display_name": None,
        "error": None,
    }

    if not city_name or not isinstance(city_name, str):
        result["error"] = "A valid city name is required."
        return result

    params = {
        "q": city_name,
        "format": "json",
        "limit": 1,
        "countrycodes": "us",
    }

    try:
        response = requests.get(
            NOMINATIM_URL,
            params=params,
            headers=_request_headers(),
            timeout=timeout,
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, list) or not data:
            result["error"] = f"No coordinates were found for {city_name}."
            return result

        location = data[0]

        latitude = _safe_float(location.get("lat"))
        longitude = _safe_float(location.get("lon"))

        if not _valid_coordinates(latitude, longitude):
            result["error"] = "The geocoding service returned invalid coordinates."
            return result

        result.update(
            {
                "success": True,
                "latitude": latitude,
                "longitude": longitude,
                "display_name": location.get("display_name"),
            }
        )

        return result

    except requests.Timeout:
        result["error"] = "The city-location service timed out."
        return result

    except requests.RequestException as exc:
        result["error"] = f"City-location service error: {exc}"
        return result

    except (ValueError, TypeError, KeyError) as exc:
        result["error"] = f"Invalid city-location response: {exc}"
        return result


# ---------------------------------------------------------------------------
# WEATHER
# ---------------------------------------------------------------------------

def _get_nws_forecast_url(
    latitude: float,
    longitude: float,
    timeout: int,
) -> Tuple[Optional[str], Optional[str]]:
    """Get the NWS forecast URL for a coordinate pair."""

    if not _valid_coordinates(latitude, longitude):
        return None, "Invalid coordinates."

    try:
        url = NWS_POINTS_URL.format(
            lat=f"{latitude:.4f}",
            lon=f"{longitude:.4f}",
        )

        response = requests.get(
            url,
            headers=_request_headers(),
            timeout=timeout,
        )

        response.raise_for_status()

        data = _safe_json(response)

        if not data:
            return None, "The weather service returned an invalid response."

        properties = data.get("properties", {})

        forecast_url = properties.get("forecast")

        if not forecast_url:
            return None, "No forecast URL was returned by the weather service."

        return forecast_url, None

    except requests.Timeout:
        return None, "The weather service timed out."

    except requests.RequestException as exc:
        return None, f"Weather service error: {exc}"

    except (TypeError, KeyError) as exc:
        return None, f"Invalid weather response: {exc}"


def get_weather(
    latitude: float,
    longitude: float,
    timeout: int = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """
    Retrieve the current relevant NWS forecast for a location.

    Returns:
        {
            "success": bool,
            "temperature": float | None,
            "temperature_unit": str | None,
            "description": str | None,
            "wind_speed": str | None,
            "wind_direction": str | None,
            "precipitation_probability": float | None,
            "forecast_period": str | None,
            "error": str | None
        }
    """

    result = {
        "success": False,
        "temperature": None,
        "temperature_unit": None,
        "description": None,
        "wind_speed": None,
        "wind_direction": None,
        "precipitation_probability": None,
        "forecast_period": None,
        "error": None,
    }

    forecast_url, error = _get_nws_forecast_url(
        latitude,
        longitude,
        timeout,
    )

    if error:
        result["error"] = error
        return result

    try:
        response = requests.get(
            forecast_url,
            headers=_request_headers(),
            timeout=timeout,
        )

        response.raise_for_status()

        data = _safe_json(response)

        if not data:
            result["error"] = "The weather forecast response was invalid."
            return result

        periods = data.get("properties", {}).get("periods", [])

        if not periods:
            result["error"] = "No forecast periods were returned."
            return result

        period = periods[0]

        temperature = _safe_float(period.get("temperature"))

        precipitation_probability = (
            period.get("probabilityOfPrecipitation", {})
            .get("value")
        )

        precipitation_probability = _safe_float(
            precipitation_probability
        )

        result.update(
            {
                "success": True,
                "temperature": temperature,
                "temperature_unit": period.get(
                    "temperatureUnit"
                ),
                "description": period.get(
                    "shortForecast"
                ),
                "wind_speed": period.get(
                    "windSpeed"
                ),
                "wind_direction": period.get(
                    "windDirection"
                ),
                "precipitation_probability": (
                    precipitation_probability
                ),
                "forecast_period": period.get(
                    "name"
                ),
            }
        )

        return result

    except requests.Timeout:
        result["error"] = "The weather forecast request timed out."
        return result

    except requests.RequestException as exc:
        result["error"] = f"Weather forecast error: {exc}"
        return result

    except (TypeError, KeyError, ValueError) as exc:
        result["error"] = f"Invalid weather forecast response: {exc}"
        return result


# ---------------------------------------------------------------------------
# OPENSTREETMAP / OVERPASS
# ---------------------------------------------------------------------------

def _build_overpass_query(
    latitude: float,
    longitude: float,
    radius_meters: int,
) -> str:
    """
    Build an Overpass query for EMS facilities, hospitals, and roads.
    """

    return f"""
[out:json][timeout:20];

(
  node["amenity"="fire_station"]
    (around:{radius_meters},{latitude},{longitude});

  way["amenity"="fire_station"]
    (around:{radius_meters},{latitude},{longitude});

  relation["amenity"="fire_station"]
    (around:{radius_meters},{latitude},{longitude});

  node["amenity"="hospital"]
    (around:{radius_meters},{latitude},{longitude});

  way["amenity"="hospital"]
    (around:{radius_meters},{latitude},{longitude});

  relation["amenity"="hospital"]
    (around:{radius_meters},{latitude},{longitude});

  way["highway"]
    (around:{radius_meters},{latitude},{longitude});
);

out center tags;
"""


def _extract_element_coordinates(
    element: Dict[str, Any],
) -> Tuple[Optional[float], Optional[float]]:
    """Extract coordinates from an Overpass element."""

    latitude = _safe_float(element.get("lat"))
    longitude = _safe_float(element.get("lon"))

    if _valid_coordinates(latitude, longitude):
        return latitude, longitude

    center = element.get("center", {})

    latitude = _safe_float(center.get("lat"))
    longitude = _safe_float(center.get("lon"))

    if _valid_coordinates(latitude, longitude):
        return latitude, longitude

    return None, None


def get_osm_facilities(
    latitude: float,
    longitude: float,
    radius_meters: int = 10000,
    timeout: int = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """
    Retrieve emergency facilities, hospitals, and road segments.

    Returns:
        {
            "success": bool,
            "ems_facilities": [...],
            "hospitals": [...],
            "roads": [...],
            "error": str | None
        }
    """

    result = {
        "success": False,
        "ems_facilities": [],
        "hospitals": [],
        "roads": [],
        "error": None,
    }

    if not _valid_coordinates(latitude, longitude):
        result["error"] = "Invalid coordinates for OpenStreetMap search."
        return result

    if radius_meters <= 0:
        result["error"] = "The OpenStreetMap search radius must be positive."
        return result

    query = _build_overpass_query(
        latitude,
        longitude,
        radius_meters,
    )

    try:
        response = requests.post(
            OVERPASS_URL,
            data=query,
            headers=_request_headers(),
            timeout=max(timeout, 20),
        )

        response.raise_for_status()

        data = _safe_json(response)

        if not data:
            result["error"] = "OpenStreetMap returned an invalid response."
            return result

        elements = data.get("elements", [])

        if not isinstance(elements, list):
            result["error"] = "OpenStreetMap returned invalid element data."
            return result

        ems_facilities: List[Dict[str, Any]] = []
        hospitals: List[Dict[str, Any]] = []
        roads: List[Dict[str, Any]] = []

        for element in elements:
            if not isinstance(element, dict):
                continue

            tags = element.get("tags", {})

            if not isinstance(tags, dict):
                tags = {}

            element_lat, element_lon = _extract_element_coordinates(
                element
            )

            if element_lat is None or element_lon is None:
                continue

            osm_id = element.get("id")
            element_type = element.get("type")

            name = tags.get("name")

            amenity = tags.get("amenity")
            highway = tags.get("highway")

            if amenity == "fire_station":
                ems_facilities.append(
                    {
                        "id": osm_id,
                        "osm_type": element_type,
                        "name": name or "Fire Station",
                        "latitude": element_lat,
                        "longitude": element_lon,
                        "type": "fire_station",
                    }
                )

            elif amenity == "hospital":
                hospitals.append(
                    {
                        "id": osm_id,
                        "osm_type": element_type,
                        "name": name or "Hospital",
                        "latitude": element_lat,
                        "longitude": element_lon,
                        "type": "hospital",
                    }
                )

            elif highway:
                roads.append(
                    {
                        "id": osm_id,
                        "osm_type": element_type,
                        "name": name or highway,
                        "latitude": element_lat,
                        "longitude": element_lon,
                        "type": highway,
                    }
                )

        result.update(
            {
                "success": True,
                "ems_facilities": ems_facilities,
                "hospitals": hospitals,
                "roads": roads,
            }
        )

        return result

    except requests.Timeout:
        result["error"] = "OpenStreetMap request timed out."
        return result

    except requests.RequestException as exc:
        result["error"] = f"OpenStreetMap request error: {exc}"
        return result

    except (TypeError, KeyError, ValueError) as exc:
        result["error"] = f"Invalid OpenStreetMap response: {exc}"
        return result


# ---------------------------------------------------------------------------
# OSRM ROUTING
# ---------------------------------------------------------------------------

def get_route_time(
    origin_latitude: float,
    origin_longitude: float,
    destination_latitude: float,
    destination_longitude: float,
    timeout: int = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """
    Get an estimated driving route between two coordinates.

    Returns:
        {
            "success": bool,
            "duration_minutes": float | None,
            "distance_km": float | None,
            "duration_seconds": float | None,
            "distance_meters": float | None,
            "error": str | None
        }
    """

    result = {
        "success": False,
        "duration_minutes": None,
        "distance_km": None,
        "duration_seconds": None,
        "distance_meters": None,
        "error": None,
    }

    if not _valid_coordinates(
        origin_latitude,
        origin_longitude,
    ):
        result["error"] = "Invalid origin coordinates."
        return result

    if not _valid_coordinates(
        destination_latitude,
        destination_longitude,
    ):
        result["error"] = "Invalid destination coordinates."
        return result

    coordinates = (
        f"{origin_longitude},{origin_latitude};"
        f"{destination_longitude},{destination_latitude}"
    )

    url = f"{OSRM_URL}/{coordinates}"

    params = {
        "overview": "false",
        "steps": "false",
        "alternatives": "false",
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers=_request_headers(),
            timeout=timeout,
        )

        response.raise_for_status()

        data = _safe_json(response)

        if not data:
            result["error"] = "OSRM returned an invalid response."
            return result

        if data.get("code") != "Ok":
            result["error"] = (
                f"OSRM routing failed: "
                f"{data.get('code', 'Unknown error')}"
            )
            return result

        routes = data.get("routes", [])

        if not routes:
            result["error"] = "OSRM returned no route."
            return result

        route = routes[0]

        duration_seconds = _safe_float(
            route.get("duration")
        )

        distance_meters = _safe_float(
            route.get("distance")
        )

        if duration_seconds is None or distance_meters is None:
            result["error"] = "OSRM returned incomplete route information."
            return result

        result.update(
            {
                "success": True,
                "duration_seconds": duration_seconds,
                "duration_minutes": duration_seconds / 60.0,
                "distance_meters": distance_meters,
                "distance_km": distance_meters / 1000.0,
            }
        )

        return result

    except requests.Timeout:
        result["error"] = "OSRM routing request timed out."
        return result

    except requests.RequestException as exc:
        result["error"] = f"OSRM routing error: {exc}"
        return result

    except (TypeError, KeyError, ValueError) as exc:
        result["error"] = f"Invalid OSRM response: {exc}"
        return result


# ---------------------------------------------------------------------------
# BATCH ROUTING
# ---------------------------------------------------------------------------

def build_route_time_matrix(
    facilities: List[Dict[str, Any]],
    demand_zones: List[Dict[str, Any]],
    timeout: int = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """
    Build a facility-to-demand-zone route-time matrix.

    The matrix uses:
        matrix[facility_index][zone_index]

    Each value is the estimated driving time in minutes.

    Failed routes are represented by None rather than raising an exception.

    Returns:
        {
            "success": bool,
            "matrix": list[list[float | None]],
            "distance_matrix_km": list[list[float | None]],
            "successful_routes": int,
            "failed_routes": int,
            "error": str | None
        }
    """

    result = {
        "success": False,
        "matrix": [],
        "distance_matrix_km": [],
        "successful_routes": 0,
        "failed_routes": 0,
        "error": None,
    }

    if not isinstance(facilities, list):
        result["error"] = "Facilities must be provided as a list."
        return result

    if not isinstance(demand_zones, list):
        result["error"] = "Demand zones must be provided as a list."
        return result

    matrix: List[List[Optional[float]]] = []
    distance_matrix: List[List[Optional[float]]] = []

    successful_routes = 0
    failed_routes = 0

    for facility in facilities:
        facility_row: List[Optional[float]] = []
        distance_row: List[Optional[float]] = []

        facility_lat = facility.get("latitude")
        facility_lon = facility.get("longitude")

        for zone in demand_zones:
            zone_lat = zone.get("latitude")
            zone_lon = zone.get("longitude")

            route = get_route_time(
                facility_lat,
                facility_lon,
                zone_lat,
                zone_lon,
                timeout=timeout,
            )

            if route["success"]:
                facility_row.append(
                    route["duration_minutes"]
                )

                distance_row.append(
                    route["distance_km"]
                )

                successful_routes += 1

            else:
                facility_row.append(None)
                distance_row.append(None)

                failed_routes += 1

        matrix.append(facility_row)
        distance_matrix.append(distance_row)

    total_routes = successful_routes + failed_routes

    result.update(
        {
            "success": total_routes == 0 or successful_routes > 0,
            "matrix": matrix,
            "distance_matrix_km": distance_matrix,
            "successful_routes": successful_routes,
            "failed_routes": failed_routes,
        }
    )

    if failed_routes > 0 and successful_routes == 0:
        result["error"] = "No route requests returned usable results."

    elif failed_routes > 0:
        result["error"] = (
            f"{failed_routes} of {total_routes} route requests failed."
        )

    return result


# ---------------------------------------------------------------------------
# SIMPLE COMPATIBILITY HELPERS
# ---------------------------------------------------------------------------

def get_city_coordinates_tuple(
    city_name: str,
    timeout: int = DEFAULT_TIMEOUT,
) -> Optional[Tuple[float, float]]:
    """
    Convenience helper returning:

        (latitude, longitude)

    Returns None if geocoding fails.
    """

    result = get_city_coordinates(
        city_name,
        timeout=timeout,
    )

    if not result["success"]:
        return None

    return (
        result["latitude"],
        result["longitude"],
    )


def get_weather_data(
    latitude: float,
    longitude: float,
    timeout: int = DEFAULT_TIMEOUT,
) -> Optional[Dict[str, Any]]:
    """
    Convenience helper returning weather data or None.
    """

    result = get_weather(
        latitude,
        longitude,
        timeout=timeout,
    )

    if not result["success"]:
        return None

    return result


def get_facilities(
    latitude: float,
    longitude: float,
    radius_meters: int = 10000,
    timeout: int = DEFAULT_TIMEOUT,
) -> Optional[Dict[str, Any]]:
    """
    Convenience helper returning facility data or None.
    """

    result = get_osm_facilities(
        latitude,
        longitude,
        radius_meters=radius_meters,
        timeout=timeout,
    )

    if not result["success"]:
        return None

    return result
