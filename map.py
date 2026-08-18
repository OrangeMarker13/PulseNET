import folium
from streamlit_folium import st_folium


def create_map(
    latitude,
    longitude,
    ems_locations=None,
    hospitals=None
):
    map_object = folium.Map(
        location=[
            latitude,
            longitude
        ],
        zoom_start=11,
        tiles="OpenStreetMap"
    )

    folium.Marker(
        [latitude, longitude],
        tooltip="Analysis center",
        icon=folium.Icon(
            icon="info-sign"
        )
    ).add_to(map_object)

    for location in ems_locations or []:
        folium.Marker(
            [
                location["latitude"],
                location["longitude"]
            ],
            tooltip=location.get(
                "name",
                "EMS location"
            ),
            popup="EMS location",
            icon=folium.Icon(
                icon="plus"
            )
        ).add_to(map_object)

    for hospital in hospitals or []:
        folium.Marker(
            [
                hospital["latitude"],
                hospital["longitude"]
            ],
            tooltip=hospital.get(
                "name",
                "Hospital"
            ),
            popup="Emergency hospital",
            icon=folium.Icon(
                icon="home"
            )
        ).add_to(map_object)

    return map_object


def display_map(
    latitude,
    longitude,
    ems_locations=None,
    hospitals=None
):
    map_object = create_map(
        latitude,
        longitude,
        ems_locations,
        hospitals
    )

    return st_folium(
        map_object,
        width=None,
        height=500,
        returned_objects=[]
    )
