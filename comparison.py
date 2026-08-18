def calculate_improvement(
    baseline_value,
    optimized_value,
    lower_is_better=True
):
    if baseline_value is None:
        return None

    if optimized_value is None:
        return None

    if baseline_value == 0:
        return None

    if lower_is_better:
        improvement = (
            (baseline_value - optimized_value)
            / baseline_value
            * 100
        )
    else:
        improvement = (
            (optimized_value - baseline_value)
            / baseline_value
            * 100
        )

    return improvement


def compare_response_times(
    baseline_response_time,
    optimized_response_time
):
    improvement = calculate_improvement(
        baseline_response_time,
        optimized_response_time,
        lower_is_better=True
    )

    return {
        "baseline": baseline_response_time,
        "optimized": optimized_response_time,
        "improvement_percent": improvement
    }


def compare_coverage(
    baseline_coverage,
    optimized_coverage
):
    improvement = calculate_improvement(
        baseline_coverage,
        optimized_coverage,
        lower_is_better=False
    )

    return {
        "baseline": baseline_coverage,
        "optimized": optimized_coverage,
        "improvement_percent": improvement
    }


def calculate_demand_coverage(
    demand_zones,
    response_times,
    response_threshold=10
):
    if not demand_zones:
        return None

    if not response_times:
        return None

    total_demand = 0
    covered_demand = 0

    for index, zone in enumerate(demand_zones):
        demand = zone.get(
            "predicted_demand",
            0
        )

        if index >= len(response_times):
            continue

        response_time = response_times[index]

        total_demand += demand

        if response_time <= response_threshold:
            covered_demand += demand

    if total_demand == 0:
        return None

    return (
        covered_demand
        / total_demand
        * 100
    )


def create_comparison(
    baseline_response_time,
    optimized_response_time,
    baseline_coverage,
    optimized_coverage
):
    response_comparison = compare_response_times(
        baseline_response_time,
        optimized_response_time
    )

    coverage_comparison = compare_coverage(
        baseline_coverage,
        optimized_coverage
    )

    return {
        "response_time": response_comparison,
        "coverage": coverage_comparison
    }


def format_comparison(comparison):
    if not comparison:
        return "No comparison results are available."

    response = comparison.get(
        "response_time",
        {}
    )

    coverage = comparison.get(
        "coverage",
        {}
    )

    response_improvement = response.get(
        "improvement_percent"
    )

    coverage_improvement = coverage.get(
        "improvement_percent"
    )

    response_text = "unavailable"

    if response_improvement is not None:
        response_text = (
            f"{response_improvement:.1f}%"
        )

    coverage_text = "unavailable"

    if coverage_improvement is not None:
        coverage_text = (
            f"{coverage_improvement:.1f}%"
        )

    return (
        f"Estimated response-time improvement: "
        f"{response_text}. "
        f"Estimated coverage improvement: "
        f"{coverage_text}."
    )
