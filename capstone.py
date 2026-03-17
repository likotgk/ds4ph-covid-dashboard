import streamlit as st
import pandas as pd
import plotly.express as px

# Main title for the App
st.title("COVID-19 Global Tracker")


# cache data to avoid reloading on every interaction
@st.cache_data
def fetch_and_clean_data(url):
    data = pd.read_csv(url)
    data = data.drop(columns=["Province/State", "Lat", "Long"])
    data = data.groupby("Country/Region").sum()
    data = data.T
    data.index = pd.to_datetime(data.index, format="%m/%d/%y")
    return data


# URLs for the JHU CSSE COVID-19 datasets
confirmed_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
deaths_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"

# Load data with a status bar to indicate progress
confirmed = fetch_and_clean_data(confirmed_url)
deaths = fetch_and_clean_data(deaths_url)

# configure data type selection
confirmed_or_deaths = st.radio(
    "Select Data Type", ("Confirmed Cases", "Deaths"), horizontal=True
)
if confirmed_or_deaths == "Confirmed Cases":
    data_to_plot = confirmed
else:
    data_to_plot = deaths

# configure calculation type selection
calculation_type = st.radio(
    "Select Calculation Type", ("Cumulative", "Daily New"), horizontal=True
)
if calculation_type == "Daily New":
    data_to_plot = data_to_plot.diff().fillna(0).clip(lower=0)

# create a fragment for the chart to allow for better organization and potential reuse


@st.fragment
def plot_covid_chart():
    countries = st.multiselect(
        "Select Countries/Locations", options=data_to_plot.columns)

# filter data based on selected countries
    if len(countries) > 0:
        filtered_data = data_to_plot[countries]

    # create a date range selector with a default range of all data
        use_custom_range = st.checkbox("Use Custom Date Range", value=False)
        if use_custom_range:
            min_date = filtered_data.index.min()
            max_date = filtered_data.index.max()
            selected_range = st.date_input(
                "Select Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
            )
            if len(selected_range) == 2:
                start_date, end_date = selected_range
                filtered_data = filtered_data.loc[start_date:end_date]
            else:
                st.warning("Please select a valid date range.")

    # create the line chart using Plotly Express
        fig = px.line(
            filtered_data,
            x=filtered_data.index,
            y=filtered_data.columns,
            title=f"{calculation_type} {confirmed_or_deaths} Over Time",
            render_mode="svg",
        )
        fig.update_traces(
            hovertemplate="Date: %{x}<br>"
            + f"{calculation_type} {confirmed_or_deaths}: "
            + "<b>%{y:,.0f}</b>"
        )
        fig.update_layout(
            hovermode="x unified",
            xaxis_title="Date",
            yaxis_title=f"{calculation_type} {confirmed_or_deaths}",
            xaxis=dict(
                type="date",
                rangeslider=dict(visible=True, thickness=0.15),
                rangeselector=dict(
                    visible=True,
                    buttons=list(
                        [
                            dict(count=1, label="1m", step="month",
                                 stepmode="backward"),
                            dict(count=6, label="6m", step="month",
                                 stepmode="backward"),
                            dict(count=1, label="YTD",
                                 step="year", stepmode="todate"),
                            dict(count=1, label="1y", step="year",
                                 stepmode="backward"),
                            dict(step="all"),
                        ]
                    ),
                ),
            ),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Please select at least one country to display the chart.")

# call the chart plotting function to display the chart in the app
plot_covid_chart()

st.markdown("---")
st.markdown(
    "**© 2026 DS4PH Capstone Project | Developed by Guangkai Tang**",
    unsafe_allow_html=True
)