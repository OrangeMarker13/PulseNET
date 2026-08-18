from datetime import datetime


def get_city_info(city_name, supported_cities):
    if city_name not in supported_cities:
        return None

    return supported_cities[city_name]


def get_data_status():
    return {
        "weather": {
            "available": False,
            "source": None
        },
        "traffic": {
            "available": False,
            "source": None
        },
        "ems": {
            "available": False,
            "source": None
        },
        "roads": {
            "available": False,
            "source": None
        },
        "geography": {
            "available": False,
            "source": None
        }
    }


def create_data_record(
    data_type,
    source,
    timestamp,
    status,
    data=None
):
    return {
        "data_type": data_type,
        "source": source,
        "timestamp": timestamp,
        "status": status,
        "data": data
    }


def get_timestamp():
    return datetime.now().isoformat()
