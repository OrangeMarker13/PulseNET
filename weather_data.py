import requests


WEATHER_URL = "https://api.weather.gov"


def get_weather_data(latitude, longitude):
    headers = {
        "User-Agent": "PulseGrid emergency planning research app"
    }

    try:
        point_response = requests.get(
            f"{WEATHER_URL}/points/{latitude},{longitude}",
            headers=headers,
            timeout=10
        )

        if point_response.status_code != 200:
            return None

        point_data = point_response.json()

        forecast_url = point_data.get(
            "properties",
            {}
        ).get(
            "forecast"
        )

        hourly_url = point_data.get(
            "properties",
            {}
        ).get(
            "forecastHourly"
        )

        if not forecast_url:
            return None

        forecast_response = requests.get(
            forecast_url,
            headers=headers,
            timeout=10
        )

        if forecast_response.status_code != 200:
            return None

        forecast_data = forecast_response.json()

        hourly_data = None

        if hourly_url:
            hourly_response = requests.get(
                hourly_url,
                headers=headers,
                timeout=10
            )

            if hourly_response.status_code == 200:
                hourly_data = hourly_response.json()

        return {
            "source": "National Weather Service",
            "forecast": forecast_data,
            "hourly": hourly_data
        }

    except requests.RequestException:
        return None


def get_current_conditions(weather_data):
    if not weather_data:
        return None

    hourly = weather_data.get(
        "hourly"
    )

    if not hourly:
        return None

    periods = hourly.get(
        "properties",
        {}
    ).get(
        "periods",
        []
    )

    if not periods:
        return None

    current = periods[0]

    return {
        "temperature": current.get(
            "temperature"
        ),
        "temperature_unit": current.get(
            "temperatureUnit"
        ),
        "wind_speed": current.get(
            "windSpeed"
        ),
        "wind_direction": current.get(
            "windDirection"
        ),
        "short_forecast": current.get(
            "shortForecast"
        ),
        "precipitation_probability": (
            current.get(
                "probabilityOfPrecipitation",
                {}
            ).get(
                "value"
            )
        )
    }


def get_forecast_periods(weather_data):
    if not weather_data:
        return []

    forecast = weather_data.get(
        "forecast"
    )

    if not forecast:
        return []

    return (
        forecast
        .get(
            "properties",
            {}
        )
        .get(
            "periods",
            []
        )
    )


def get_weather_summary(weather_data):
    current = get_current_conditions(
        weather_data
    )

    if current is None:
        return {
            "available": False
        }

    return {
        "available": True,
        "source": weather_data.get(
            "source"
        ),
        "temperature": current.get(
            "temperature"
        ),
        "temperature_unit": current.get(
            "temperature_unit"
        ),
        "wind_speed": current.get(
            "wind_speed"
        ),
        "wind_direction": current.get(
            "wind_direction"
        ),
        "short_forecast": current.get(
            "short_forecast"
        ),
        "precipitation_probability": current.get(
            "precipitation_probability"
        )
    }
