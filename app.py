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
import altair as alt


states = {
    "US-MA": "Massachusetts",
    "US-CT": "Connecticut",
    "US-RI": "Rhode Island",
    "US-NH": "New Hampshire",
    "US-VT": "Vermont",
    "US-ME": "Maine"
}

def read_data():
    ##Reads and cleans the airport data, filters it for New England states, and maps state codes to full names.
    # [PY3] Error checking with try/except
    try:
        df = pd.read_csv("airports.csv").set_index("id")
        # [DA1] Clean or manipulate data, lambda function
        df["elevation_ft"] = df["elevation_ft"].apply(lambda x: x if x > 0 else None)
        df = df.loc[df["iso_region"].isin(["US-MA", "US-CT", "US-RI", "US-NH", "US-VT", "US-ME"])]
        # [PY5] A dictionary with access to keys, values, or items
        df = df.loc[df["type"].isin(["small_airport", "medium_airport", "large_airport"])]
        # [DA2] Sort data in ascending order
        df = df.sort_values(by="elevation_ft", ascending=True)
        df["iso_region"] = df["iso_region"].map(states)
        return df
    except FileNotFoundError:
        st.error("Error: The data file 'airports.csv' is missing.")


def filter_data(user_selection, user_elevation, user_type, yesorno):
    ## Filters the dataset based on user-selected states, maximum elevation, airport type, and scheduled service.
    # [PY1] A function with two or more parameters, one with a default value
    df = read_data()
    if df.empty:
        return df
    user_selection = [states.get(region, region) for region in user_selection]
    df = df.loc[df["iso_region"].isin(user_selection)]
    # [DA4] Filter data by one condition
    df = df.loc[df["elevation_ft"] < user_elevation]
    # [DA5] Filter data by two or more conditions
    df = df.loc[df["type"].isin(user_type)]
    df = df.loc[df["scheduled_service"].isin(yesorno)]
    return df


def all_regions():
    ## Retrieves a list of unique regions available in the dataset.
    df = read_data()
    return list(df["iso_region"].unique()) if not df.empty else []


def all_types():
    ## Retrieves a list of unique airport types available in the dataset.
    df = read_data()
    return list(df["type"].unique()) if not df.empty else []

def count_airports(iso_regions, df):
    ## Counts the number of airports in each selected region using a list comprehension.
    # [PY4] A list comprehension
    lst = [df.loc[df["iso_region"].isin([iso_region])].shape[0] for iso_region in iso_regions]

    return lst

def piechart(counts, user_selection):
    ## Creates a pie chart to visualize the distribution of airports across selected regions.
    color_map = px.colors.qualitative.Set3

    fig = px.pie(
        values=counts,
        names=user_selection,
        title="Distribution of Airports Across New England States",
        color=user_selection,
        color_discrete_sequence=color_map
    )

    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>"  
                      "Airports: %{value}<br>" 
                      "Percentage: %{percent}<br>" 
                      "<extra></extra>"
    )

    fig.update_layout(
        title=dict(
            text="Distribution of Airports Across New England States",
            font=dict(
                size=20,
                color="black",
            ),
            x=0.4,
            xanchor="center",
            yanchor="top"
        ),
        legend=dict(
            title="Regions",
            orientation="v",
            y=0.5,
            x=-0.2,
            xanchor="right",
            yanchor="middle",
            font=dict(
                size=16,
                color="black"
            ),
            title_font=dict(
                size=18
            )
        ),
        hoverlabel=dict(
            font_size=13,
            font_family="Arial"
        ),
        height=550,
        width=800,

    )

    return fig


def airport_alt(df):
    ## Groups airport elevation data by region and stores it as a dictionary.
    # [DA9] Add a new column or perform calculations on DataFrame columns
    dict_alt = df.groupby("iso_region")["elevation_ft"].apply(list).to_dict()
    return dict_alt


def airport_alt_max(dict_alt):
    ## Calculates the maximum elevation of airports for each region.
    dict_max = {}
    for key in dict_alt.keys():
        dict_max[key] = np.max(dict_alt[key])

    return dict_max


def airport_alt_averages(dict_alt):
    ## Calculates the average elevation of airports for each region.
    dict_averages = {}
    for key in dict_alt.keys():
        dict_averages[key] = np.mean(dict_alt[key])

    return dict_averages


def bar_chart(dict_averages, dict_max):
    ## Creates a bar chart to compare average and maximum airport elevations by region.
    x = list(dict_averages.keys())
    avg_y = list(dict_averages.values())
    max_y = [dict_max[state] for state in x]

    bar_colors = px.colors.qualitative.Set2

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=x,
        y=avg_y,
        name="Average Elevation",
        marker_color=bar_colors[:len(x)],
        width=0.6,
        hovertemplate="State: %{x}<br>Average Elevation: %{y:.1f} ft<extra></extra>"
    ))

    fig.add_trace(go.Scatter(
        x=x,
        y=max_y,
        name="Maximum Elevation",
        mode='lines+markers',
        line=dict(color='darkred', width=3),
        marker=dict(size=8, symbol='circle'),
        hovertemplate="State: %{x}<br>Maximum Elevation: %{y:.1f} ft<extra></extra>"
    ))

    fig.update_layout(
        title=dict(
            text="Elevations in Feet of Airports by State",
            font=dict(size=20, color="black"),
            x=0.5,
            xanchor="center"
        ),
        xaxis=dict(
            title="State Name",
            tickangle=45,
            title_font=dict(size=14),
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title="Elevation (ft)",
            title_font=dict(size=14),
            tickfont=dict(size=12)
        ),
        legend=dict(
            title=" ",
            font=dict(size=14),
            orientation="h",
            y=1.15,
            x=0.5,
            xanchor="center"
        ),
        height=600,
        width=900,
        barmode='overlay',
        hovermode="x unified"
    )

    return fig


def map(df):
    ## Generates a detailed map displaying airports by location, size, and type.

    size_mapping = {
        "small_airport": 4,
        "medium_airport": 8,
        "large_airport": 12
    }
    df["size"] = df["type"].map(size_mapping)
    #[DA7] Add/Drop/Select/Create New/Group Columns

    df["formatted_city"] = "City: " + df["municipality"]

    type_labels = {
        "small_airport": "Small Airport",
        "medium_airport": "Medium Airport",
        "large_airport": "Large Airport"
    }

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
        labels={"type": "Airport Type"},
        size_max=12,
        zoom=6,
        title="Airports in New England by Type and Size"
    )

    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>"
                      "%{customdata[0]}<br>"
                      "<extra></extra>"
    )

    fig.update_layout(
        title=dict(
            text="Airports in New England by Type and Size",
            font=dict(size=24, color="black"),
            x=0.5,
            xanchor="center"
        ),
        mapbox_style="open-street-map",
        legend=dict(
            title=dict(text="<b>Airport Type</b>", font=dict(size=14)),
            font=dict(size=13),
            orientation="v",
            y=0.5,
            x=1.02,
            xanchor="left",
            yanchor="middle",
            bgcolor="rgba(255,255,255,0.7)",
            bordercolor="black",
            borderwidth=1
        ),
        margin=dict(l=10, r=10, t=50, b=10),
        width=1000,
        height=700,
        hoverlabel=dict(
            font_size=14,
            font_family="Arial"
        )
    )
    for i, trace in enumerate(fig.data):
        fig.data[i].name = type_labels[trace.name]

    st.plotly_chart(fig, use_container_width=False)


def counting(data):
    #[PY2] A function that returns more than one value
    ## Counts the total number of airports and the number of large, medium, and small airports.
    airport_count = data.shape[0]
    # [DA3] Find Top largest or smallest values
    large_count = data['type'].value_counts().to_dict().get("large_airport", 0)
    medium_count = data['type'].value_counts().to_dict().get("medium_airport", 0)
    small_count = data['type'].value_counts().to_dict().get("small_airport", 0)

    return airport_count, large_count, medium_count, small_count


def donut(data):
    ## Creates a donut chart to visualize the distribution of airport types.
    airport_count, large_count, medium_count, small_count = counting(data)

    chart_data = pd.DataFrame({
        "Airport Type": ["Large Airports", "Medium Airports", "Small Airports"],
        "Count": [large_count, medium_count, small_count],
        "Color": ["Red", "Green", "Blue"]
    })

    donut_chart = alt.Chart(chart_data).mark_arc(innerRadius=50).encode(
        theta=alt.Theta("Count:Q", title=""),
        color=alt.Color("Airport Type:N", scale=alt.Scale(domain=["Large Airports", "Medium Airports", "Small Airports"],
                                                         range=["Red", "Green", "Blue"])),
        tooltip=["Airport Type:N", "Count:Q"]
    ).properties(
        title="Airport Distribution by Type",
        width=500,
        height=400
    ).configure_title(
        fontSize=18,
        anchor="start",
        color="black"
    ).configure_legend(
        titleFontSize=14,
        labelFontSize=12
    )

    st.write(f"### Total Airports Displayed: {airport_count}")
    st.altair_chart(donut_chart, use_container_width=True)


def main():
    ## Main function to set up the Streamlit, implement controls, and display visualizations.
    st.set_page_config(page_title="Airport Data Visualization", page_icon="✈️", layout="wide")

    st.markdown("<h1 style='text-align: center; color: #1E90FF;'>Visualizing New England Airport Data</h1>",
                unsafe_allow_html=True)
    st.markdown(
        # [ST4] Customized page design
        "<h3 style='text-align: center; color: gray;'>Explore the airport data across New England states using interactive charts and maps.</h3>",
        unsafe_allow_html=True)

    st.markdown("---")

    st.sidebar.markdown("### Filter Options")
    st.sidebar.write("Use the filters below to customize the data displayed.")

    regions = st.sidebar.multiselect(
        #[ST1] Dropdown widget
        "Select Regions:",
        all_regions(),
        default=all_regions()
    )
    #[ST2] Slider widget
    max_altitude = st.sidebar.slider("Maximum Altitude (ft):", 0, 2500, value=2500)


    types = st.sidebar.multiselect(
        "Select Airport Types:",
        all_types(),
        default=all_types()
    )
    #[ST3] Checkbox widget
    scheduled = st.sidebar.checkbox("Show Commercial Airports Only", value=False)

    if scheduled:
        yesorno = ["yes"]
    else:
        yesorno = ["yes", "no"]

    data = filter_data(regions, max_altitude, types, yesorno)

    st.markdown("### Airport Distribution Across New England States")
    st.plotly_chart(piechart(count_airports(regions, data), regions), use_container_width=True)
    #[VIZ1] Pie Chart

    st.markdown("### Elevation Data for Airports")
    st.plotly_chart(bar_chart(airport_alt_averages(airport_alt(data)), airport_alt_max(airport_alt(data))),
                    #[VIZ2] Bar Chart
                    use_container_width=True)

    st.markdown("### Airports by Type and Size on the Map")
    map(data)
    #[MAP] Detailed Map
    donut(data)
    #[VIZ3] Donut Chart


if __name__ == '__main__':
    main()