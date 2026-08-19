SUPPORTED_CITIES = {
    "Charlotte, NC": {"county": "Mecklenburg County", "state": "North Carolina"},
    "Raleigh, NC": {"county": "Wake County", "state": "North Carolina"},
    "Greensboro, NC": {"county": "Guilford County", "state": "North Carolina"},
    "Durham, NC": {"county": "Durham County", "state": "North Carolina"},
    "Winston-Salem, NC": {"county": "Forsyth County", "state": "North Carolina"},
    "Fayetteville, NC": {"county": "Cumberland County", "state": "North Carolina"},
    "Cary, NC": {"county": "Wake County", "state": "North Carolina"},
    "Wilmington, NC": {"county": "New Hanover County", "state": "North Carolina"},
    "High Point, NC": {"county": "Guilford County", "state": "North Carolina"},
    "Concord, NC": {"county": "Cabarrus County", "state": "North Carolina"},
    "Asheville, NC": {"county": "Buncombe County", "state": "North Carolina"},
    "Gastonia, NC": {"county": "Gaston County", "state": "North Carolina"},
    "Chapel Hill, NC": {"county": "Orange County", "state": "North Carolina"},
    "Jacksonville, NC": {"county": "Onslow County", "state": "North Carolina"},
    "Rocky Mount, NC": {"county": "Nash County", "state": "North Carolina"},
    "Burlington, NC": {"county": "Alamance County", "state": "North Carolina"},
    "Wilson, NC": {"county": "Wilson County", "state": "North Carolina"},
    "Greenville, NC": {"county": "Pitt County", "state": "North Carolina"},
    "Kannapolis, NC": {"county": "Cabarrus County", "state": "North Carolina"},
    "Apex, NC": {"county": "Wake County", "state": "North Carolina"},
    "Huntersville, NC": {"county": "Mecklenburg County", "state": "North Carolina"},
    "Mooresville, NC": {"county": "Iredell County", "state": "North Carolina"}
}

DEFAULT_AMBULANCE_COUNT = 12
MAX_AMBULANCE_COUNT = 100
DEFAULT_ANALYSIS_MODE = "Current conditions"

ANALYSIS_MODES = [
    "Current conditions",
    "Historical conditions",
    "Custom scenario"
]

DATA_FALLBACK_ORDER = [
    "live",
    "recent",
    "historical"
]

OSM_SEARCH_RADIUS_KM = 20
ROUTING_TIMEOUT = 15
NOMINATIM_TIMEOUT = 10
WEATHER_TIMEOUT = 10
OVERPASS_TIMEOUT = 30

MAX_QUANTUM_QUBITS = 12
QUANTUM_SHOTS = 512
QUANTUM_REPETITIONS = 1

RESPONSE_THRESHOLD_MINUTES = 10

DEMAND_GRID_SIZE = 5
DEMO_RECORD_COUNT = 500
RANDOM_SEED = 42
