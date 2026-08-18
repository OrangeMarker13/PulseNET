from pipeline import load_city_data
from demand import (
    prepare_demand_data,
    create_demand_grid,
    calculate_historical_demand,
    predict_demand,
    rank_demand_zones
)
from optimization import create_optimization_problem
from classical_optimizer import greedy_optimize
from quantum_engine import (
    create_ambulance_problem,
    run_qaoa
)


def prepare_analysis(
    city_name,
    ambulance_count,
    emergency_records=None,
    latitude=None,
    longitude=None
):
    city_data = load_city_data(
        city_name
    )

    if city_data.get("status") != "success":
        return {
            "status": "error",
            "reason": city_data.get(
                "reason",
                "city data could not be loaded"
            )
        }

    location = city_data.get(
        "location",
        {}
    )

    latitude = latitude or location.get(
        "latitude"
    )

    longitude = longitude or location.get(
        "longitude"
    )

    if latitude is None or longitude is None:
        return {
            "status": "error",
            "reason": "city coordinates are unavailable"
        }

    prepared_records = prepare_demand_data(
        emergency_records or []
    )

    demand_grid = create_demand_grid(
        prepared_records,
        latitude,
        longitude
    )

    historical_demand = calculate_historical_demand(
        demand_grid
    )

    predicted_demand = predict_demand(
        historical_demand
    )

    ranked_demand = rank_demand_zones(
        predicted_demand
    )

    demand_zones = []

    for _, row in ranked_demand.iterrows():
        demand_zones.append(
            {
                "latitude_grid": row[
                    "latitude_grid"
                ],
                "longitude_grid": row[
                    "longitude_grid"
                ],
                "predicted_demand": row[
                    "predicted_demand"
                ]
            }
        )

    candidate_locations = []

    for location in city_data.get(
        "ems_locations",
        []
    ):
        if (
            "latitude" in location
            and "longitude" in location
        ):
            candidate_locations.append(
                location
            )

    optimization_problem = create_optimization_problem(
        demand_zones,
        candidate_locations,
        ambulance_count
    )

    classical_result = None
    quantum_result = None

    if optimization_problem is not None:
        classical_result = greedy_optimize(
            optimization_problem[
                "cost_matrix"
            ],
            ambulance_count
        )

        quantum_problem = create_ambulance_problem(
            optimization_problem[
                "cost_matrix"
            ],
            ambulance_count
        )

        quantum_result = run_qaoa(
            quantum_problem
        )

    return {
        "status": "success",
        "city_data": city_data,
        "demand_zones": demand_zones,
        "candidate_locations": candidate_locations,
        "optimization_problem": optimization_problem,
        "classical_result": classical_result,
        "quantum_result": quantum_result
    }


def get_selected_locations(
    analysis_result,
    method="quantum"
):
    if not analysis_result:
        return []

    if method == "classical":
        result = analysis_result.get(
            "classical_result"
        )
    else:
        result = analysis_result.get(
            "quantum_result"
        )

    if not result:
        return []

    if result.get("status") != "success":
        return []

    selected_indexes = result.get(
        "selected_locations",
        []
    )

    candidates = analysis_result.get(
        "candidate_locations",
        []
    )

    selected_locations = []

    for index in selected_indexes:
        if 0 <= index < len(candidates):
            selected_locations.append(
                candidates[index]
            )

    return selected_locations


def get_analysis_status(
    analysis_result
):
    if not analysis_result:
        return "not_started"

    if analysis_result.get(
        "status"
    ) != "success":
        return "error"

    quantum_result = analysis_result.get(
        "quantum_result"
    )

    if quantum_result is None:
        return "pending"

    if quantum_result.get(
        "status"
    ) == "success":
        return "complete"

    return "partial"
