import streamlit as st
import requests
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import os
from dotenv import load_dotenv
from weather import display_weather
from utils import check_api_key

load_dotenv()
API_KEY = os.getenv("API_KEY")

# Streamlit app configuration
st.set_page_config(page_title="Real-Time Weather App", page_icon="🌤", layout="centered", initial_sidebar_state="auto")

# Check if the API key is valid
if not check_api_key(API_KEY):
    st.error("Invalid API key. Please check your OpenWeatherMap API key.")
    st.stop()  # Stop execution if API key is invalid
else:
    print('API working fine!')


def add_bg_from_url():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("https://images.pexels.com/photos/1183099/pexels-photo-1183099.jpeg?auto=compress&cs=tinysrgb&w=600");
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# Call this function at the beginning of your app
add_bg_from_url()


# Function to fetch weather data
def fetch_weather(city):
    try:
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}'
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data for {city}: {e}")
        return None


# List of metro cities in India
metro_cities = ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad']

# This will refresh the page every 60 seconds
update_interval_ms = 10 * 1000
st_autorefresh(interval=update_interval_ms, key="data_refresh")

# Add print statements to indicate refresh
print(f"Page refreshed at: {datetime.now()}")

# Manual refresh button
refresh_button = st.sidebar.button("Refresh Weather Data")
if refresh_button:
    st.session_state.unit = 'Celsius'  # Reset unit to Celsius after refresh
    st.experimental_rerun()


def get_weather_data(city, unit, lower_bound, upper_bound):
    print(f"Fetching weather data for {city} at {datetime.now()}")
    display_weather(city, unit, lower_bound, upper_bound)


# Set default temperature unit to 'Celsius'
if 'unit' not in st.session_state:
    st.session_state.unit = 'Celsius'

# Sidebar for selecting temperature units and setting alert thresholds
st.sidebar.title("Settings")
st.sidebar.radio("Select temperature unit", ('Celsius', 'Fahrenheit', 'Kelvin'), key='unit')

# User-configurable alert thresholds for temperature
st.sidebar.subheader("Set Alert Thresholds")
if st.session_state.unit == 'Celsius':
    lower_bound = st.sidebar.number_input(f"Lower temperature bound (°C)", value=10.0, step=1.0, format="%.2f")
    upper_bound = st.sidebar.number_input(f"Upper temperature bound (°C)", value=30.0, step=1.0, format="%.2f")
elif st.session_state.unit == 'Fahrenheit':
    lower_bound = st.sidebar.number_input(f"Lower temperature bound (°F)", value=50.0, step=1.0, format="%.2f")
    upper_bound = st.sidebar.number_input(f"Upper temperature bound (°F)", value=86.0, step=1.0, format="%.2f")
else:
    lower_bound = st.sidebar.number_input(f"Lower temperature bound (K)", value=283.0, step=1.0, format="%.2f")
    upper_bound = st.sidebar.number_input(f"Upper temperature bound (K)", value=303.0, step=1.0, format="%.2f")

# Display app header
st.markdown("<h1 style='text-align: center;'>Real-Time Weather Application</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Stay updated with the latest weather data for metro cities in India!</p>",
            unsafe_allow_html=True)

# Display weather for metro cities
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>Weather in Indian Metro Cities</h2>", unsafe_allow_html=True)

for city in metro_cities:
    st.markdown("<hr>", unsafe_allow_html=True)
    get_weather_data(city, st.session_state.unit, lower_bound, upper_bound)  # Call the cached function

# User input for a city
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>Check Weather for Any City</h2>", unsafe_allow_html=True)
user_city = st.text_input("Enter a city to get weather information:")

if user_city:
    get_weather_data(user_city, st.session_state.unit, lower_bound, upper_bound)  # Call the cached function
