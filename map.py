import folium
from streamlit_folium import st_folium


def _value(item, key, default=None):
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)


def create_map(
    coordinates,
    demand_zones=None,
    ems_locations=None,
    selected_locations=None,
    classical_locations=None,
    hospitals=None
):
    latitude, longitude = coordinates
    m = folium.Map(
        location=[latitude, longitude],
        zoom_start=11,
        tiles="OpenStreetMap",
        control_scale=True
    )

    folium.Marker(
        [latitude, longitude],
        tooltip="Analysis center",
        popup="PulseGrid analysis center",
        icon=folium.Icon(color="purple", icon="info-sign")
    ).add_to(m)

    demand_layer = folium.FeatureGroup(name="Demand zones").add_to(m)
    if demand_zones is not None and not demand_zones.empty:
        for _, zone in demand_zones.iterrows():
            lat, lon = zone["latitude"], zone["longitude"]
            demand = zone.get("predicted_demand", zone.get("historical_demand", 0))
            priority = str(zone.get("priority", "Medium"))
            radius = max(6, min(25, 5 + float(demand) * 1.5))
            color = {"High": "red", "Medium": "orange", "Low": "green"}.get(priority, "blue")
            folium.CircleMarker(
                [lat, lon],
                radius=radius,
                color=color,
                fill=True,
                fill_opacity=.55,
                tooltip=f"{priority} demand zone",
                popup=f"Priority: {priority}<br>Historical demand: {zone.get('historical_demand', 0):.0f}<br>Predicted demand: {demand:.1f}"
            ).add_to(demand_layer)

    ems_layer = folium.FeatureGroup(name="EMS facilities").add_to(m)
    for location in ems_locations or []:
        lat, lon = _value(location, "latitude"), _value(location, "longitude")
        if lat is None or lon is None:
            continue
        folium.Marker(
            [lat, lon],
            tooltip=_value(location, "name", "EMS facility"),
            popup=_value(location, "name", "EMS facility"),
            icon=folium.Icon(color="blue", icon="plus")
        ).add_to(ems_layer)

    hospital_layer = folium.FeatureGroup(name="Hospitals").add_to(m)
    for hospital in hospitals or []:
        lat, lon = _value(hospital, "latitude"), _value(hospital, "longitude")
        if lat is None or lon is None:
            continue
        folium.Marker(
            [lat, lon],
            tooltip=_value(hospital, "name", "Hospital"),
            popup=_value(hospital, "name", "Hospital"),
            icon=folium.Icon(color="green", icon="home")
        ).add_to(hospital_layer)

    classical_layer = folium.FeatureGroup(name="Classical deployment").add_to(m)
    for facility in classical_locations or []:
        lat, lon = _value(facility, "latitude"), _value(facility, "longitude")
        if lat is None or lon is None:
            continue
        folium.Marker(
            [lat, lon],
            tooltip="Classical optimization",
            popup=f"Classical candidate: {_value(facility, 'name', 'Facility')}",
            icon=folium.Icon(color="orange", icon="cog")
        ).add_to(classical_layer)

    selected_layer = folium.FeatureGroup(name="Selected deployment").add_to(m)
    for facility in selected_locations or []:
        lat, lon = _value(facility, "latitude"), _value(facility, "longitude")
        if lat is None or lon is None:
            continue
        folium.Marker(
            [lat, lon],
            tooltip="PulseGrid selected deployment",
            popup=f"Selected ambulance location: {_value(facility, 'name', 'Facility')}",
            icon=folium.Icon(color="red", icon="ambulance")
        ).add_to(selected_layer)

    folium.LayerControl(collapsed=False).add_to(m)
    return m


def display_map(
    coordinates,
    demand_zones=None,
    ems_locations=None,
    selected_locations=None,
    classical_locations=None,
    hospitals=None
):
    m = create_map(
        coordinates,
        demand_zones,
        ems_locations,
        selected_locations,
        classical_locations,
        hospitals
    )
    return st_folium(m, use_container_width=True, height=520, returned_objects=[])
