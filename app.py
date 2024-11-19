"""
Joseph Arman
CS230: Section 5
Data: Which data set you used URL: https://ourairports.com/data/
Link to your web application on Streamlit Cloud (if posted): https://finalpython.streamlit.app/
Description: This program visualizes airport data for New England states using interactive Streamlit widgets,
charts, and maps.
"""
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


states = {
    "US-MA": "Massachusetts",
    "US-CT": "Connecticut",
    "US-RI": "Rhode Island",
    "US-NH": "New Hampshire",
    "US-VT": "Vermont",
    "US-ME": "Maine"
}

def read_data():
    try:
        df = pd.read_csv("airports.csv").set_index("id")
        df = df.loc[df["iso_region"].isin(["US-MA", "US-CT", "US-RI", "US-NH", "US-VT", "US-ME"])]
        df = df.loc[df["type"].isin(["small_airport", "medium_airport", "large_airport"])]
        df = df.sort_values(by="elevation_ft", ascending=True)
        df["iso_region"] = df["iso_region"].map(states)
        return df
    except FileNotFoundError:
        st.error("Error: The data file 'airports.csv' is missing.")


def filter_data(user_selection, user_elevation, user_type, yesorno):
    df = read_data()
    if df.empty:
        return df
    user_selection = [states.get(region, region) for region in user_selection]
    df = df.loc[df["iso_region"].isin(user_selection)]
    df = df.loc[df["elevation_ft"] < user_elevation]
    df = df.loc[df["type"].isin(user_type)]
    df = df.loc[df["scheduled_service"].isin(yesorno)]
    return df


def all_regions():
    df = read_data()
    return list(df["iso_region"].unique()) if not df.empty else []

def all_types():
    df = read_data()
    return list(df["type"].unique()) if not df.empty else []

    
def count_airports(iso_regions, df):
    lst = [df.loc[df["iso_region"].isin([iso_region])].shape[0] for iso_region in iso_regions]

    return lst

def piechart(counts, user_selection):
    fig = px.pie(
        values=counts,
        names=user_selection,
        title="Airports in New England Area",
        hole=0.3
    )
    return fig


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
    size_mapping = {
        "small_airport": 3,
        "medium_airport": 7,
        "large_airport": 11
    }
    df["size"] = df["type"].map(size_mapping)

    df["formatted_city"] = "City: " + df["municipality"]

    fig = px.scatter_mapbox(
        df,
        lat="latitude_deg",
        lon="longitude_deg",
        color="type",
        size="size",
        hover_name="name",
        custom_data=["formatted_city"],
        color_discrete_map={
            "small_airport": "blue",
            "medium_airport": "green",
            "large_airport": "red"
        },
        size_max=11,
        zoom=5.3,
        title="Airports in New England by Type and Size"
    )

    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>" 
                      "%{customdata[0]}<br>" 
                      "<extra></extra>"
    )

    fig.update_layout(
        mapbox_style="carto-positron",
        width=900,
        height=650,
        hoverlabel=dict(
            font_size=15
        )
    )

    st.plotly_chart(fig, use_container_width=True)



def counting(data):
    airport_count = data.shape[0]
    large_count = data['type'].value_counts().to_dict().get("large_airport", 0)
    medium_count = data['type'].value_counts().to_dict().get("medium_airport", 0)
    small_count = data['type'].value_counts().to_dict().get("small_airport", 0)

    return airport_count, large_count, medium_count, small_count

def main():
    st.title("Visualizing New England Airport Data using Python Charts")
    st.write("Welcome to this Airport Data in New England. Open the sidebar to begin!")

    st.sidebar.write("### Select Your Options:")

    st.sidebar.write("**Choose one or more states to filter:**")
    regions = st.sidebar.multiselect(
        "Select a region:",
        all_regions(),
        default=all_regions()
    )
    st.sidebar.write("----------------------------------")

    st.sidebar.write("**Adjust the slider to filter by airport elevation:**")
    max_altitude = st.sidebar.slider(
        "Maximum Altitude:",
        0,
        2500,
        value=2500
    )

    st.sidebar.write("----------------------------------")

    st.sidebar.write("**Choose the types of airports to display:**")
    types = st.sidebar.multiselect(
        "Select the type of Airport:",
        all_types(),
        default=all_types()
    )

    st.sidebar.write("----------------------------------")
    st.sidebar.write("**Toggle to show only airports with scheduled services:**")
    scheduled = st.sidebar.checkbox(
        "Only show commercial airports",
        value=False
    )

    if scheduled:
        yesorno = ["yes"]
    else:
        yesorno = ["yes", "no"]

    data = filter_data(regions, max_altitude, types, yesorno)
    counts = count_airports(regions, data)
    st.plotly_chart(piechart(counts, regions))

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