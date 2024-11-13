"""
Joseph Arman
CS230: Section 5
Data: Which data set you used URL: https://ourairports.com/data/
Link to your web application on Streamlit Cloud (if posted)
Description:
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import pydeck as pdk
import plotly.graph_objects as go


states = {
    "US-MA": "Massachusetts",
    "US-CT": "Connecticut",
    "US-RI": "Rhode Island",
    "US-NH": "New Hampshire",
    "US-VT": "Vermont",
    "US-ME": "Maine"
}

def read_data():
    df = pd.read_csv("airports.csv").set_index("id")
    df = df.loc[df["iso_region"].isin(["US-MA", "US-CT", "US-RI", "US-NH", "US-VT", "US-ME"])]
    df = df.loc[df["type"].isin(["small_airport", "medium_airport", "large_airport"])]
    df = df.sort_values(by="elevation_ft", ascending=True)
    df["iso_region"] = df["iso_region"].map(states)
    return df


def filter_data(user_selection, user_elevation, user_type, yesorno):
    df = read_data()
    user_selection = [states.get(region, region) for region in user_selection]
    df = df.loc[df["iso_region"].isin(user_selection)]
    df = df.loc[df["elevation_ft"] < user_elevation]
    df = df.loc[df["type"].isin(user_type)]
    df = df.loc[df["scheduled_service"].isin(yesorno)]

    return df


def all_regions():
    df = read_data()
    lst = []
    for ind, row in df.iterrows():
        if row["iso_region"] not in lst:
            lst.append(row["iso_region"])
    return lst

def all_types():
    df = read_data()
    lst = []
    for ind, row in df.iterrows():
        if row["type"] not in lst:
            lst.append(row["type"])
    return lst

    
def count_airports(iso_regions, df):
    lst = [df.loc[df["iso_region"].isin([iso_region])].shape[0] for iso_region in iso_regions]

    return lst

def piechart(counts, user_selection):
    plt.figure()
    total = sum(counts)
    plt.pie(counts, labels=user_selection, autopct=lambda p: f"{int(p * total / 100)}")
    plt.title("Airports in New England Area:")
    return plt


def airport_alt(df):
    dict_alt = df.groupby("iso_region")["elevation_ft"].apply(list).to_dict()
    return dict_alt

def airport_alt_max(dict_alt):
    dict_max = {}
    for key in dict_alt.keys():
        dict_max[key] = np.max(dict_alt[key])

    return dict_max


def airport_alt_averages(dict_alt):
    dict_averages = {}
    for key in dict_alt.keys():
        dict_averages[key] = np.mean(dict_alt[key])

    return dict_averages

def bar_chart(dict_averages, dict_max):

    x = list(dict_averages.keys())
    avg_y = list(dict_averages.values())
    max_y = [dict_max[state] for state in x]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x = x,
        y = avg_y,
        name="Average Elevation",
        marker_color = 'blue',
        width = 0.8,
        hovertemplate="Average Elevation: %{y:.1f}<extra></extra>"
    ))

    fig.add_trace(go.Scatter(
        x = x,
        y = max_y,
        name = "Maximum Elevation",
        mode = 'lines+markers',
        line=dict(color='red', width=2),
        hovertemplate="Maximum Elevation: %{y:.1f}<extra></extra>"
    ))

    fig.update_layout(
        title="Elevations in Feet of Airports by State",
        xaxis_title="State Name",
        yaxis_title="Elevation (ft)",
        barmode='overlay',
        hovermode="x"
    )

    return fig

def map(df):
    map_df = df.filter(["name", "latitude_deg", "longitude_deg","municipality", "ident"])

    view_state = pdk.ViewState(
        latitude=43.5,
        longitude=-69.5,
        zoom=5.5,
        pitch=0
    )

    layer = pdk.Layer('ScatterplotLayer',
                      data=map_df,
                      get_position='[longitude_deg , latitude_deg]',
                      get_radius=4000,
                      get_color=[80, 100, 250],
                      pickable = True)

    tool_tip = {'html': 'Airport: '
                        '<b>{name}</b>'
                        '<br/>City: {municipality}'
                        '<br/>Airport ID: {ident}',
                'style': {'backgroundColor': 'steelblue', 'color': 'white'}}

    map = pdk.Deck(map_style= 'mapbox://styles/mapbox/light-v9',
                   initial_view_state=view_state,
                   layers =[layer],
                   tooltip=tool_tip)

    st.pydeck_chart(map)

def counting(data):
    airport_count = data.shape[0]
    large_count = data['type'].value_counts().to_dict().get("large_airport", 0)
    medium_count = data['type'].value_counts().to_dict().get("medium_airport", 0)
    small_count = data['type'].value_counts().to_dict().get("small_airport", 0)

    return airport_count, large_count, medium_count, small_count

def main():
    st.title("Visualizing New England Airport Data using Python Charts")
    st.write("Welcome to this Airport Data in New England. Open the sidebar to begin!")

    st.sidebar.write("Please select your options to display data.")


    regions = st.sidebar.multiselect("Select a region: ", all_regions(),default=all_regions())
    max_altitude = st.sidebar.slider("Maximum Altitude: ", 0, 2500, value=2500)
    types = st.sidebar.multiselect("Select the type of Airport: ", all_types(), default=all_types())

    scheduled = st.sidebar.checkbox("Only show commercial airports", value=False)
    if scheduled:
        yesorno = ["yes"]
    else:
        yesorno = ["yes", "no"]

    data = filter_data(regions, max_altitude, types, yesorno)
    counts = count_airports(regions, data)
    st.pyplot(piechart(counts, regions))

    altitudes = airport_alt(data)
    averages = airport_alt_averages(altitudes)
    maximums = airport_alt_max(altitudes)

    st.plotly_chart(bar_chart(averages, maximums))


    map(data)
    airport_count,large_count,medium_count,small_count = counting(data)

    st.metric("Total Airports being Displayed", airport_count)
    st.metric("Large Airports: ", large_count)
    st.metric("Medium Airports: ", medium_count)
    st.metric("Small Airports: ", small_count)


if __name__ == '__main__':
    main()