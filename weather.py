import requests


def get_weather(latitude, longitude):
    url = (
        "https://api.weather.gov/points/"
        f"{latitude},{longitude}"
    )

    headers = {
        "User-Agent": "PulseGrid emergency planning research application"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        point_data = response.json()

        forecast_url = point_data["properties"]["forecast"]

        forecast_response = requests.get(
            forecast_url,
            headers=headers,
            timeout=10
        )

        forecast_response.raise_for_status()

        forecast_data = forecast_response.json()

        periods = forecast_data["properties"]["periods"]

        if not periods:
            return None

        current_period = periods[0]

        return {
            "temperature": current_period.get("temperature"),
            "temperature_unit": current_period.get(
                "temperatureUnit"
            ),
            "wind_speed": current_period.get("windSpeed"),
            "wind_direction": current_period.get(
                "windDirection"
            ),
            "short_forecast": current_period.get(
                "shortForecast"
            ),
            "detailed_forecast": current_period.get(
                "detailedForecast"
            ),
            "precipitation_probability": current_period.get(
                "probabilityOfPrecipitation",
                {}
            ).get("value"),
            "source": "National Weather Service",
            "status": "live"
        }

    except (requests.RequestException, KeyError, ValueError):
        return None
