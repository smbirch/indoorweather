import requests
import configparser
import json

from prometheus_client import Gauge

# Prometheus gauges
outdoor_temperature_gauge = Gauge(
    "outdoor_temperature", "Outdoor temperature in Fahrenheit"
)
outdoor_humidity_gauge = Gauge("outdoor_humidity", "Outdoor humidity percentage")
outdoor_pm2_5_gauge = Gauge("outdoor_pm2_5", "Outdoor PM2.5 level")
outdoor_pm10_gauge = Gauge("outdoor_pm10", "Outdoor PM10 level")
outdoor_aqi_gauge = Gauge("outdoor_aqi", "Outdoor AQI value")


def get_current_weather():
    config = configparser.ConfigParser()
    config.read("config.ini")
    api_key = config.get("API", "api_key")
    lat = config.get("COORDS", "lat")
    lon = config.get("COORDS", "lon")

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&exclude=hourly,daily,minutely,alerts&appid={api_key}&units=imperial"
    response = requests.get(url)
    data = json.loads(response.text)

    temperature = data["main"]["temp"]
    humidity = data["main"]["humidity"]

    print("Outdoor Temperature:", temperature)
    print("Outdoor Humidity:", humidity)

    # Set Prometheus Gauges
    outdoor_temperature_gauge.set(temperature)
    outdoor_humidity_gauge.set(humidity)


def get_current_aqi():
    config = configparser.ConfigParser()
    config.read("config.ini")
    api_key = config.get("API", "api_key")
    lat = config.get("COORDS", "lat")
    lon = config.get("COORDS", "lon")

    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    response = requests.get(url)
    data = json.loads(response.text)

    pm2_5 = data["list"][0]["components"]["pm2_5"]
    pm10 = data["list"][0]["components"]["pm10"]
    aqi = data["list"][0]["main"]["aqi"]

    print("Outdoor PM2.5: ", pm2_5)
    print("Outdoor PM10: ", pm10)
    print("Outdoor AQI: ", aqi)

    # Set Prometheus Gauges
    outdoor_pm2_5_gauge.set(pm2_5)
    outdoor_pm10_gauge.set(pm10)
    outdoor_aqi_gauge.set(aqi)


if __name__ == "__main__":
    get_current_weather()
    get_current_aqi()
