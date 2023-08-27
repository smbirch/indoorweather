import requests
import configparser
import json

import aqi

import influx


def get_current_weather():
    """Calls Open Weather API and pulls temperature and humidity for the location specified in the config file"""
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

    # Send data to InfluxDB
    influx.outdoor_temp_humidity(temperature, humidity)


def get_current_aqi():
    """Calls Open Weather API and pulls AQI data for the location specified in the config file"""
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

    convertedaqi = convert_to_aqi(pm2_5, pm10)

    print("Outdoor PM2.5: ", pm2_5)
    print("Outdoor PM10: ", pm10)
    print("Outdoor AQI: ", convertedaqi)

    influx.outdoor_aqi(pm2_5, pm10, convertedaqi)


def convert_to_aqi(pm2_5, pm10):
    """Convert particulate matter datapoints into EPA AQI

    Args:
        pm2_5 (float)
        pm10 (float)

    Returns:
        float: AQI after conversion
    """
    convertedaqi = aqi.to_aqi(
        [
            (aqi.POLLUTANT_PM25, pm2_5),
            (aqi.POLLUTANT_PM10, pm10),
        ]
    )
    return convertedaqi


if __name__ == "__main__":
    get_current_weather()
    get_current_aqi()
