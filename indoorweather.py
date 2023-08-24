import time
import serial
import Adafruit_DHT
import sds011

# import outdoorweather


def celsius_to_fahrenheit(degrees_celsius):
    return (degrees_celsius * 9 / 5) + 32


def get_tempandhumidity():
    sensor = Adafruit_DHT.DHT22
    sensor_pin = 4

    try:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, sensor_pin)
    except RuntimeError as e:
        print(f"RuntimeError: {e}")
        print("GPIO Access may need sudo permissions.")
        time.sleep(2.0)
        return

    print(
        "Temp: {0:0.1f}*F, Humidity: {1:0.1f}%".format(
            celsius_to_fahrenheit(temperature), humidity
        )
    )


def set_sdsstate(sds):
    sds.sleep(sleep=True)
    sds.set_working_period(rate=0)


# Get particulate matter
def get_PM(sds):
    measurements = sds.read_measurement()
    print(f"PM2.5: {measurements['pm2.5']} PM10: {measurements['pm10']}")


def main():
    port = "/dev/ttyUSB0"
    sds = sds011.SDS011(port=port)
    set_sdsstate(sds)

    while True:
        get_PM(sds)
        get_tempandhumidity()
        # outdoorweather.get_current_weather()


if __name__ == "__main__":
    main()
