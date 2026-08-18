import requests


CENSUS_URL = "https://api.census.gov/data/2020/dec/pl"


def search_cities(search_text):
    if not search_text:
        return []

    search_text = search_text.strip().lower()

    if len(search_text) < 2:
        return []

    try:
        response = requests.get(
            CENSUS_URL,
            params={
                "get": "NAME,P1_001N",
                "for": "place:*"
            },
            timeout=15
        )

        if response.status_code != 200:
            return []

        data = response.json()

        if len(data) < 2:
            return []

        headers = data[0]
        rows = data[1:]

        results = []

        for row in rows:
            record = dict(
                zip(headers, row)
            )

            name = record.get(
                "NAME",
                ""
            )

            population = record.get(
                "P1_001N"
            )

            if not name:
                continue

            if search_text not in name.lower():
                continue

            try:
                population = int(
                    population
                )
            except (
                TypeError,
                ValueError
            ):
                continue

            results.append(
                {
                    "name": name,
                    "population": population,
                    "state": record.get(
                        "state"
                    ),
                    "place": record.get(
                        "place"
                    )
                }
            )

        results.sort(
            key=lambda city: city["population"],
            reverse=True
        )

        return results

    except (
        requests.RequestException,
        ValueError
    ):
        return []


def get_large_cities(
    minimum_population=100000
):
    try:
        response = requests.get(
            CENSUS_URL,
            params={
                "get": "NAME,P1_001N",
                "for": "place:*"
            },
            timeout=15
        )

        if response.status_code != 200:
            return []

        data = response.json()

        if len(data) < 2:
            return []

        headers = data[0]
        rows = data[1:]

        cities = []

        for row in rows:
            record = dict(
                zip(headers, row)
            )

            try:
                population = int(
                    record.get(
                        "P1_001N",
                        0
                    )
                )
            except (
                TypeError,
                ValueError
            ):
                continue

            if population < minimum_population:
                continue

            cities.append(
                {
                    "name": record.get(
                        "NAME"
                    ),
                    "population": population,
                    "state": record.get(
                        "state"
                    ),
                    "place": record.get(
                        "place"
                    )
                }
            )

        cities.sort(
            key=lambda city: city["population"],
            reverse=True
        )

        return cities

    except (
        requests.RequestException,
        ValueError
    ):
        return []


def format_city_name(city):
    name = city.get(
        "name",
        ""
    )

    state = city.get(
        "state",
        ""
    )

    if state:
        return f"{name}, {state}"

    return name
