import numpy as np


def calculate_distance(
    latitude_1,
    longitude_1,
    latitude_2,
    longitude_2
):
    latitude_difference = np.radians(
        latitude_2 - latitude_1
    )

    longitude_difference = np.radians(
        longitude_2 - longitude_1
    )

    latitude_1 = np.radians(latitude_1)
    latitude_2 = np.radians(latitude_2)

    a = (
        np.sin(latitude_difference / 2) ** 2
        + np.cos(latitude_1)
        * np.cos(latitude_2)
        * np.sin(longitude_difference / 2) ** 2
    )

    distance = (
        2
        * 6371
        * np.arcsin(np.sqrt(a))
    )

    return distance


def build_travel_cost_matrix(
    demand_zones,
    candidate_locations
):
    if not demand_zones or not candidate_locations:
        return np.empty((0, 0))

    matrix = []

    for demand_zone in demand_zones:
        row = []

        for location in candidate_locations:
            distance = calculate_distance(
                demand_zone["latitude"],
                demand_zone["longitude"],
                location["latitude"],
                location["longitude"]
            )

            row.append(distance)

        matrix.append(row)

    return np.array(matrix)


def calculate_coverage(
    demand,
    travel_time,
    response_threshold
):
    if travel_time > response_threshold:
        return 0

    return demand


def evaluate_deployment(
    demand_zones,
    ambulance_locations,
    response_threshold=10
):
    total_demand = 0
    covered_demand = 0

    for demand_zone in demand_zones:
        demand_value = demand_zone.get(
            "predicted_demand",
            0
        )

        total_demand += demand_value

        best_time = None

        for ambulance in ambulance_locations:
            travel_time = ambulance.get(
                "travel_time",
                None
            )

            if travel_time is None:
                continue

            if best_time is None:
                best_time = travel_time
            elif travel_time < best_time:
                best_time = travel_time

        if best_time is not None:
            covered_demand += calculate_coverage(
                demand_value,
                best_time,
                response_threshold
            )

    if total_demand == 0:
        coverage_percentage = 0
    else:
        coverage_percentage = (
            covered_demand
            / total_demand
            * 100
        )

    return {
        "total_demand": total_demand,
        "covered_demand": covered_demand,
        "coverage_percentage": coverage_percentage
    }


def create_optimization_problem(
    demand_zones,
    candidate_locations,
    ambulance_count,
    response_threshold=10
):
    if not demand_zones:
        return None

    if not candidate_locations:
        return None

    if ambulance_count <= 0:
        return None

    cost_matrix = build_travel_cost_matrix(
        demand_zones,
        candidate_locations
    )

    return {
        "demand_zones": demand_zones,
        "candidate_locations": candidate_locations,
        "ambulance_count": ambulance_count,
        "response_threshold": response_threshold,
        "cost_matrix": cost_matrix
    }


def calculate_baseline_score(
    demand_zones,
    baseline_locations,
    response_threshold=10
):
    return evaluate_deployment(
        demand_zones,
        baseline_locations,
        response_threshold
    )


def calculate_optimized_score(
    demand_zones,
    optimized_locations,
    response_threshold=10
):
    return evaluate_deployment(
        demand_zones,
        optimized_locations,
        response_threshold
    )


def compare_deployments(
    baseline,
    optimized
):
    baseline_coverage = baseline.get(
        "coverage_percentage",
        0
    )

    optimized_coverage = optimized.get(
        "coverage_percentage",
        0
    )

    improvement = (
        optimized_coverage
        - baseline_coverage
    )

    return {
        "baseline_coverage": baseline_coverage,
        "optimized_coverage": optimized_coverage,
        "coverage_improvement": improvement
    }
