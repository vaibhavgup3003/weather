import requests

# Function to validate the API key
def check_api_key(api_key):
    test_url = f'http://api.openweathermap.org/data/2.5/weather?q=Delhi&appid={api_key}'
    response = requests.get(test_url)
    return response.status_code == 200

# Function to convert temperature units (Kelvin to Celsius or Fahrenheit)
def convert_temperature(temp_k, unit):
    if unit == 'Celsius':
        return temp_k - 273.15  # Kelvin to Celsius
    elif unit == 'Fahrenheit':
        return (temp_k - 273.15) * 9 / 5 + 32  # Kelvin to Fahrenheit
    else:
        return temp_k  # Kelvin remains as Kelvin
