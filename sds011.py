import serial
import time
import aqi

from prometheus_client import Gauge


indoor_pm2_5_gauge = Gauge("indoor_pm2_5", "Indoor PM2.5 level")
indoor_pm10_gauge = Gauge("indoor_pm10", "Indoor PM10 level")
indoor_aqi_gauge = Gauge("indoor_aqi", "Indoor AQI value")


ser = serial.Serial()
ser.port = "/dev/ttyUSB0"
ser.baudrate = 9600

if ser.isOpen() == False:
    ser.open()
ser.reset_input_buffer()
ser.reset_output_buffer()


def send_command(bytes_data):
    if ser.isOpen() == False:
        ser.open()
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    try:
        ser.write(bytes_data)
    except Exception as e:
        print(f"Error sending message: {e}")


def calculate_checksum(data):
    datalist = []
    for byte in data:
        datalist.append(int.from_bytes(byte, "little"))

    checksum = sum(datalist) % 256
    return bytes([checksum])


def sensor_wake():
    send_command(b"\x01")


def set_command(data_byte_1, data_byte_2, data_byte_3, data_byte_4, data_byte_5):
    bytes_data = [
        b"\xAA",  # head
        b"\xB4",  # command
        data_byte_1,  # data byte 1
        data_byte_2,  # data byte 2 (set mode)
        data_byte_3,  # data byte 3
        data_byte_4,  # data byte 4
        data_byte_5,  # data byte 5
        b"\x00",  # data byte 6
        b"\x00",  # data byte 7
        b"\x00",  # data byte 8
        b"\x00",  # data byte 9
        b"\x00",  # data byte 10
        b"\x00",  # data byte 11
        b"\x00",  # data byte 12
        b"\x00",  # data byte 13
        b"\xFF",  # data byte 14 (device id byte 1)
        b"\xFF",  # data byte 15 (device id byte 2)
    ]
    checksum = calculate_checksum(bytes_data[2:])
    bytes_data.append(checksum)
    bytes_data.append(b"\xAB")

    send_command(b"".join(bytes_data))


# puts sensor to sleep
def sensor_sleep():
    set_command(b"\x06", b"\x01", b"\x00", b"\x00", b"\x00")
    # print("Going to sleep")


# wake sensor from sleep and set to "work" mode
def set_sensor_work():
    set_command(b"\x06", b"\x01", b"\x01", b"\x00", b"\x00")
    # print("Setting to work mode")


# sets to active mode
def set_reporting_mode():
    set_command(b"\x02", b"\x01", b"\x00", b"\x00", b"\x00")
    # print("Setting to active mode")


# set working mode to "continuous"
def set_working_period():
    set_command(b"\x08", b"\x01", b"\x00", b"\x00", b"\x00")
    # print("Setting working period")


def get_data():
    set_command(b"\x04", b"\x00", b"\x00", b"\x00", b"\x00")


# need to flush input, getting same readings over x minutes
def sensor_read():
    for _ in range(1):
        data = []
        get_data()
        # print("\nWaiting for data...\n")
        for _ in range(0, 10):
            datum = ser.read()
            data.append(datum)
        pmtwofive = int.from_bytes(b"".join(data[2:4]), byteorder="little") / 10
        pmten = int.from_bytes(b"".join(data[4:6]), byteorder="little") / 10
        print(f"Indoor PM2.5: {pmtwofive}")
        print(f"Indoor PM10: {pmten}")
        aqi = convert_to_aqi(pmtwofive, pmten)
        print("Indoor AQI: ", aqi)

        indoor_pm2_5_gauge.set(pmtwofive)
        indoor_pm10_gauge.set(pmten)
        indoor_aqi_gauge.set(aqi)


def get_indoor_stats():
    set_sensor_work()
    time.sleep(5)

    set_reporting_mode()
    time.sleep(5)

    set_working_period()
    time.sleep(5)

    sensor_read()

    sensor_sleep()
    ser.close()


def convert_to_aqi(pmtwofive, pmten):
    indooraqi = aqi.to_aqi(
        [
            (aqi.POLLUTANT_PM25, pmtwofive),
            (aqi.POLLUTANT_PM10, pmten),
        ]
    )
    return indooraqi


def main():
    set_sensor_work()
    time.sleep(5)
    set_reporting_mode()
    time.sleep(5)
    set_working_period()
    time.sleep(5)
    sensor_read()
    sensor_sleep()
    ser.close()


if __name__ == "__main__":
    main()
