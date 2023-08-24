import requests
import configparser
import json


def get_current_weather():
    config = configparser.ConfigParser()
    config.read("config.ini")
    api_key = config.get("API", "api_key")
    lat = config.get("COORDS", "lat")
    lon = config.get("COORDS", "lon")

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&exclude=hourly,daily,minutely,alerts&appid={api_key}"
    response = requests.get(url)
    data = json.loads(response.text)
    print(data)
    print(response)
