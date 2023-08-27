import influxdb_client
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

import configparser

config = configparser.ConfigParser()
config.read("config.ini")
influx_token = config.get("INFLUX", "token")
org = "smbirch"
url = "http://localhost:8086"
bucket = "indoorweather"


write_client = influxdb_client.InfluxDBClient(url=url, token=influx_token, org=org)
write_api = write_client.write_api(write_options=SYNCHRONOUS)


def indoor_temp_humidity(temp, humidity):
    point = (
        Point("indoorvalues")
        .tag("indoor_temp_humidity", "rpi4")
        .field("indoortemp", float(temp))
        .field("indoorhumidity", float(humidity))
    )
    write_api.write(bucket=bucket, org="smbirch", record=point)


def indoor_aqi(pmtwofive, pmten, aqi):
    point = (
        Point("indoorvalues")
        .tag("indoor_aqi", "rpi4")
        .field("indoorpm25", float(pmtwofive))
        .field("indoorpmten", float(pmten))
        .field("indooraqi", float(aqi))
    )
    write_api.write(bucket=bucket, org="smbirch", record=point)


def outdoor_temp_humidity(temp, humidity):
    point = (
        Point("outdoorvalues")
        .tag("outdoor_temp_humidity", "rpi4")
        .field("outdoortemp", float(temp))
        .field("outdoorhumidity", float(humidity))
    )
    write_api.write(bucket=bucket, org="smbirch", record=point)


def outdoor_aqi(pmtwofive, pmten, aqi):
    point = (
        Point("outdoorvalues")
        .tag("outdoor_aqi", "rpi4")
        .field("outdoorpm25", float(pmtwofive))
        .field("outdoorpmten", float(pmten))
        .field("outdooraqi", float(aqi))
    )
    write_api.write(bucket=bucket, org="smbirch", record=point)
