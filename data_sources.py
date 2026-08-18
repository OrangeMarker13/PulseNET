DATA_SOURCES = {
    "ems": {
        "primary": "North Carolina Office of EMS",
        "secondary": "NC DETECT",
        "fallback": "OpenStreetMap",
        "status": "access_required"
    },
    "weather": {
        "primary": "National Weather Service",
        "fallback": None,
        "status": "available"
    },
    "roads": {
        "primary": "North Carolina GIS",
        "secondary": "OpenStreetMap",
        "fallback": None,
        "status": "available"
    },
    "traffic": {
        "primary": "live traffic provider",
        "secondary": "historical traffic data",
        "fallback": "road network routing",
        "status": "provider_required"
    },
    "hospitals": {
        "primary": "North Carolina GIS",
        "secondary": "OpenStreetMap",
        "fallback": None,
        "status": "available"
    },
    "geography": {
        "primary": "North Carolina GIS",
        "secondary": "OpenStreetMap",
        "fallback": None,
        "status": "available"
    }
}


def get_source(data_type):
    return DATA_SOURCES.get(data_type)


def get_primary_source(data_type):
    source = DATA_SOURCES.get(data_type)

    if source is None:
        return None

    return source.get("primary")


def get_fallback_source(data_type):
    source = DATA_SOURCES.get(data_type)

    if source is None:
        return None

    return source.get("fallback")


def get_source_status(data_type):
    source = DATA_SOURCES.get(data_type)

    if source is None:
        return "unknown"

    return source.get("status", "unknown")


def get_all_sources():
    return DATA_SOURCES
