from config import SUPPORTED_CITIES
from location import get_city_coordinates
from weather import get_weather
from ems import search_ems_locations, filter_ems_locations
from hospitals import search_hospitals, filter_emergency_hospitals
from roads import get_road_network, filter_drivable_roads


def load_city_data(city_name):
    if city_name not in SUPPORTED_CITIES:
        return {
            "status": "error",
            "reason": "city is not supported"
        }

    location = get_city_coordinates(city_name)

    if location is None:
        return {
            "status": "error",
            "reason": "location could not be found"
        }

    latitude = location["latitude"]
    longitude = location["longitude"]

    weather = get_weather(
        latitude,
        longitude
    )

    ems_locations = search_ems_locations(
        latitude,
        longitude
    )

    ems_locations = filter_ems_locations(
        ems_locations
    )

    hospitals = search_hospitals(
        latitude,
        longitude
    )

    emergency_hospitals = filter_emergency_hospitals(
        hospitals
    )

    roads = get_road_network(
        latitude,
        longitude
    )

    roads = filter_drivable_roads(
        roads
    )

    return {
        "status": "success",
        "city": city_name,
        "location": location,
        "weather": weather,
        "ems_locations": ems_locations,
        "hospitals": emergency_hospitals,
        "roads": roads
    }


def get_data_summary(city_data):
    if city_data.get("status") != "success":
        return {}

    weather_available = (
        city_data.get("weather") is not None
    )

    return {
        "weather": weather_available,
        "ems_locations": len(
            city_data.get(
                "ems_locations",
                []
            )
        ),
        "hospitals": len(
            city_data.get(
                "hospitals",
                []
            )
        ),
        "roads": len(
            city_data.get(
                "roads",
                []
            )
        )
    }


def get_pipeline_status(city_data):
    if city_data.get("status") != "success":
        return {
            "status": "error"
        }

    summary = get_data_summary(
        city_data
    )

    return {
        "status": "ready",
        "weather": (
            "ready"
            if summary["weather"]
            else "unavailable"
        ),
        "ems": (
            "ready"
            if summary["ems_locations"] > 0
            else "unavailable"
        ),
        "hospitals": (
            "ready"
            if summary["hospitals"] > 0
            else "unavailable"
        ),
        "roads": (
            "ready"
            if summary["roads"] > 0
            else "unavailable"
        )
    }
