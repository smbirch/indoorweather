import time

import influx

import Adafruit_DHT


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
    temp_f = celsius_to_fahrenheit(temperature)
    print(f"Indoor Temp: {temp_f:.1f}\nIndoor Humidity: {humidity:.1f}")

    influx.indoor_temp_humidity(temp_f, humidity)

    return temp_f, humidity


def main():
    get_tempandhumidity()


if __name__ == "__main__":
    main()
