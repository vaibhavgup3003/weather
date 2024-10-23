import requests
import streamlit as st
import os
import json
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from utils import convert_temperature

DATA_DIR = 'weather_data'  # Directory to store data files

# Ensure the data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


# Fetch current weather data
def fetch_weather(city, api_key):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}'
    response = requests.get(url)
    return response.json()


# Save weather data to a file
def save_weather_data(city, data_point):
    file_path = os.path.join(DATA_DIR, f'{city.lower()}.json')
    data = []
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
    data.append(data_point)
    with open(file_path, 'w') as f:
        json.dump(data, f)


# Load weather data from the file
def load_weather_data(city):
    file_path = os.path.join(DATA_DIR, f'{city.lower()}.json')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    else:
        return []


# Clean data older than 24 hours
def clean_old_data(data):
    cutoff_time = datetime.utcnow() - timedelta(hours=24)
    return [d for d in data if datetime.fromisoformat(d['timestamp']) > cutoff_time]


# Calculate statistics: max, min, and dominant weather condition
def calculate_statistics(data, unit):
    if not data:
        return None, None, None, None
    temps = [convert_temperature(d['temp_k'], unit) for d in data]
    conditions = [d['condition'] for d in data]
    max_temp = max(temps)
    min_temp = min(temps)
    avg_temp = sum(temps) / len(temps)
    dominant_condition = max(set(conditions), key=conditions.count)
    return max_temp, min_temp, avg_temp, dominant_condition


# Fetch the weather icon URL from OpenWeatherMap based on the condition
def fetch_weather_icon(condition):
    icon_mapping = {
        "clear sky": "01d",
        "few clouds": "02d",
        "scattered clouds": "03d",
        "broken clouds": "04d",
        "shower rain": "09d",
        "rain": "10d",
        "thunderstorm": "11d",
        "snow": "13d",
        "mist": "50d"
    }
    icon_code = icon_mapping.get(condition, "01d")  # Default to clear sky
    return f"http://openweathermap.org/img/wn/{icon_code}@2x.png"


# Display the weather, temperature statistics, and bar graph
def display_weather(city, unit, lower_bound=None, upper_bound=None):
    api_key = os.getenv("API_KEY")
    weather_data = fetch_weather(city, api_key)

    if weather_data.get('main'):
        # Extract current weather data
        temp_k = weather_data['main']['temp']
        feels_like_k = weather_data['main']['feels_like']
        min_temp_k = weather_data['main']['temp_min']
        max_temp_k = weather_data['main']['temp_max']
        time_stamp = datetime.utcnow().isoformat()
        condition = weather_data['weather'][0]['description']

        # Save current weather data point
        data_point = {
            'timestamp': time_stamp,
            'temp_k': temp_k,
            'condition': condition
        }
        save_weather_data(city, data_point)

        # Load and clean data from the past 24 hours
        data = load_weather_data(city)
        data = clean_old_data(data)
        # Save cleaned data
        file_path = os.path.join(DATA_DIR, f'{city.lower()}.json')
        with open(file_path, 'w') as f:
            json.dump(data, f)

        # Calculate statistics
        max_temp_24h, min_temp_24h, avg_temp_24h, dominant_condition = calculate_statistics(data, unit)

        # Convert current temperatures
        temp = convert_temperature(temp_k, unit)
        feels_like = convert_temperature(feels_like_k, unit)
        min_temp = convert_temperature(min_temp_k, unit)
        max_temp = convert_temperature(max_temp_k, unit)

        # Use Streamlit columns to split the layout
        col1, col2 = st.columns([1, 1])  # Two equally sized columns

        # Left column for current weather details
        with col1:
            st.markdown(f"<h3 style='text-align: center;'>{city}</h3>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='text-align: center; color: #FFA07A;'>{temp:.2f}°{unit[0]}</h1>",
                        unsafe_allow_html=True)
            st.markdown(f"<h5 style='text-align: center; color: #87CEFA;'>Feels like: {feels_like:.2f}°{unit[0]}</h5>",
                        unsafe_allow_html=True)
            st.markdown(
                f"<p style='text-align: center;'>Min Temp: {min_temp:.2f}°{unit[0]}</p>",
                unsafe_allow_html=True)
            st.markdown(
                f"<p style='text-align: center;'>Max Temp: {max_temp:.2f}°{unit[0]}</p>",
                unsafe_allow_html=True)
            st.markdown(
                f"<p style='text-align: center; font-weight:bold; color: #4682B4;'>{condition.capitalize()}</p>",
                unsafe_allow_html=True)

        # Right column for weather statistics and bar graph
        with col2:
            if max_temp_24h is not None:
                st.markdown(f"<h4 style='text-align: center;'>Last 24 Hours Statistics</h4>", unsafe_allow_html=True)

                # Show weather icon
                weather_icon_url = fetch_weather_icon(dominant_condition)
                st.image(weather_icon_url, width=80)

                # Create and show bar chart with max, min, and average temperature
                fig, ax = plt.subplots()
                labels = ['Max Temp', 'Min Temp', 'Avg Temp']
                temps = [max_temp_24h, min_temp_24h, avg_temp_24h]
                ax.bar(labels, temps, color=['red', 'blue', 'green'])
                ax.set_ylabel(f"Temperature (°{unit[0]})")
                ax.set_title(f"Weather Overview - Last 24 Hours")
                st.pyplot(fig)

                # Display text information below the graph
                st.write(f"Max Temperature: {max_temp_24h:.2f}°{unit[0]}")
                st.write(f"Min Temperature: {min_temp_24h:.2f}°{unit[0]}")
                st.write(f"Average Temperature: {avg_temp_24h:.2f}°{unit[0]}")
                st.write(f"Dominant Condition: {dominant_condition.capitalize()}")
            else:
                st.write("No data available for the last 24 hours.")

        # Check for temperature thresholds
        if lower_bound is not None and temp < lower_bound:
            st.write(f"ALERT: The temperature is below {lower_bound}°{unit[0]}")
        if upper_bound is not None and temp > upper_bound:
            st.write(f"ALERT: The temperature is above {upper_bound}°{unit[0]}")
    else:
        st.error(f"Could not retrieve weather data for {city}")
