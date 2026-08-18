def create_deployment_explanation(
    city_name,
    ambulance_count,
    demand_zones,
    selected_locations,
    weather=None,
    traffic_summary=None,
    road_summary=None
):
    if not demand_zones:
        return (
            f"PulseGrid could not generate a deployment explanation "
            f"for {city_name} because no validated demand data was available."
        )

    total_demand = sum(
        zone.get("predicted_demand", 0)
        for zone in demand_zones
    )

    if total_demand <= 0:
        return (
            f"PulseGrid could not identify meaningful emergency demand "
            f"patterns for {city_name}."
        )

    highest_demand = max(
        demand_zones,
        key=lambda zone: zone.get(
            "predicted_demand",
            0
        )
    )

    highest_demand_value = highest_demand.get(
        "predicted_demand",
        0
    )

    demand_share = (
        highest_demand_value
        / total_demand
        * 100
    )

    weather_text = "No live weather adjustment was available."

    if weather:
        forecast = weather.get(
            "short_forecast"
        )

        if forecast:
            weather_text = (
                f"Current weather conditions are "
                f"{forecast.lower()}."
            )

    traffic_text = (
        "No live traffic adjustment was available."
    )

    if traffic_summary:
        traffic_text = (
            "Traffic information was included "
            "in the deployment analysis."
        )

    road_text = (
        "No additional road-condition information "
        "was available."
    )

    if road_summary:
        road_text = (
            "The road network was included when "
            "evaluating deployment locations."
        )

    explanation = (
        f"For {city_name}, PulseGrid evaluated "
        f"{len(demand_zones)} predicted demand zones "
        f"and {len(selected_locations)} selected "
        f"deployment locations for {ambulance_count} "
        f"available ambulances. The highest-demand "
        f"zone accounted for approximately "
        f"{demand_share:.1f}% of the predicted demand. "
        f"{weather_text} {traffic_text} {road_text} "
        f"The proposed deployment prioritizes locations "
        f"that reduce estimated travel time to areas "
        f"with greater predicted emergency demand while "
        f"respecting the available ambulance count."
    )

    return explanation


def create_data_explanation(
    sources
):
    if not sources:
        return (
            "No validated data sources were available "
            "for this analysis."
        )

    source_names = []

    for source in sources:
        if source:
            source_names.append(
                str(source)
            )

    if not source_names:
        return (
            "No validated data sources were available "
            "for this analysis."
        )

    if len(source_names) == 1:
        source_text = source_names[0]
    else:
        source_text = (
            ", ".join(source_names[:-1])
            + " and "
            + source_names[-1]
        )

    return (
        "PulseGrid used the following validated data "
        f"sources for this analysis: {source_text}. "
        "When a preferred source was unavailable, "
        "the application records the limitation rather "
        "than treating fallback information as live data."
    )
