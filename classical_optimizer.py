import numpy as np


def greedy_optimize(
    cost_matrix,
    ambulance_count
):
    if cost_matrix is None:
        return {
            "status": "error",
            "reason": "cost matrix is empty"
        }

    if cost_matrix.size == 0:
        return {
            "status": "error",
            "reason": "cost matrix is empty"
        }

    if ambulance_count <= 0:
        return {
            "status": "error",
            "reason": "ambulance count must be positive"
        }

    location_count = cost_matrix.shape[1]

    ambulance_count = min(
        ambulance_count,
        location_count
    )

    selected_locations = []
    remaining_locations = list(
        range(location_count)
    )

    current_cost = np.full(
        cost_matrix.shape[0],
        np.inf
    )

    for _ in range(ambulance_count):
        best_location = None
        best_score = None

        for location in remaining_locations:
            new_cost = np.minimum(
                current_cost,
                cost_matrix[:, location]
            )

            score = np.sum(new_cost)

            if (
                best_score is None
                or score < best_score
            ):
                best_score = score
                best_location = location

        if best_location is None:
            break

        selected_locations.append(
            best_location
        )

        current_cost = np.minimum(
            current_cost,
            cost_matrix[:, best_location]
        )

        remaining_locations.remove(
            best_location
        )

    return {
        "status": "success",
        "selected_locations": selected_locations,
        "objective_value": float(
            np.sum(current_cost)
        )
    }


def evaluate_solution(
    cost_matrix,
    selected_locations
):
    if cost_matrix is None:
        return None

    if cost_matrix.size == 0:
        return None

    if not selected_locations:
        return None

    selected_costs = cost_matrix[
        :,
        selected_locations
    ]

    minimum_costs = np.min(
        selected_costs,
        axis=1
    )

    return {
        "total_cost": float(
            np.sum(minimum_costs)
        ),
        "average_cost": float(
            np.mean(minimum_costs)
        ),
        "maximum_cost": float(
            np.max(minimum_costs)
        )
    }


def compare_solutions(
    classical_result,
    quantum_result,
    cost_matrix
):
    if (
        classical_result.get("status") != "success"
        or quantum_result.get("status") != "success"
    ):
        return None

    classical_evaluation = evaluate_solution(
        cost_matrix,
        classical_result["selected_locations"]
    )

    quantum_evaluation = evaluate_solution(
        cost_matrix,
        quantum_result["selected_locations"]
    )

    if (
        classical_evaluation is None
        or quantum_evaluation is None
    ):
        return None

    classical_cost = classical_evaluation[
        "average_cost"
    ]

    quantum_cost = quantum_evaluation[
        "average_cost"
    ]

    if classical_cost == 0:
        improvement = 0
    else:
        improvement = (
            (
                classical_cost
                - quantum_cost
            )
            / classical_cost
            * 100
        )

    return {
        "classical": classical_evaluation,
        "quantum": quantum_evaluation,
        "quantum_improvement_percent": improvement
    }
