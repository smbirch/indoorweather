import serial
import time
import aqi

import influx


ser = serial.Serial()
ser.port = "/dev/ttyUSB0"
ser.baudrate = 9600

if ser.isOpen() == False:
    ser.open()
ser.reset_input_buffer()
time.sleep(0.1)  # Giving some time for the buffer to clear
ser.reset_output_buffer()


def send_command(bytes_data):
    """Send byte data to SDS011

    Args:
        bytes_data (list): 18 byte packet with checksum
    """
    if ser.isOpen() == False:
        ser.open()
    ser.reset_input_buffer()
    time.sleep(0.1)
    ser.reset_output_buffer()
    time.sleep(0.1)
    try:
        ser.write(bytes_data)
    except Exception as e:
        print(f"Error sending message: {e}")


def calculate_checksum(data):
    datalist = []
    for byte in data:
        datalist.append(int.from_bytes(byte, "little"))  # Little endian

    checksum = sum(datalist) % 256
    return bytes([checksum])


def sensor_wake():
    send_command(b"\x01")


def set_command(data_byte_1, data_byte_2, data_byte_3, data_byte_4, data_byte_5):
    """Create byte array and prepare to send to sensor

    Args:
        data_byte_ (byte string): Bytes

    """
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
    bytes_data.append(b"\xAB")  # This is the tail bit as specified in the SDS011 docs

    send_command(b"".join(bytes_data))


# puts sensor to sleep
def sensor_sleep():
    set_command(b"\x06", b"\x01", b"\x00", b"\x00", b"\x00")


# wake sensor from sleep and set to "work" mode
def set_sensor_work():
    set_command(b"\x06", b"\x01", b"\x01", b"\x00", b"\x00")


# sets to active mode
def set_reporting_mode():
    set_command(b"\x02", b"\x01", b"\x00", b"\x00", b"\x00")


# set working mode to "continuous"
def set_working_period():
    set_command(b"\x08", b"\x01", b"\x00", b"\x00", b"\x00")


# When the SDS011 is in query mode this will query the sensor for new readings.
def get_data():
    set_command(b"\x04", b"\x00", b"\x00", b"\x00", b"\x00")


def sensor_read():
    ser.reset_input_buffer()
    time.sleep(0.1)
    ser.reset_output_buffer()
    time.sleep(0.1)

    data = []

    for _ in range(0, 10):
        datum = ser.read()
        data.append(datum)
    pmtwofive = int.from_bytes(b"".join(data[2:4]), byteorder="little") / 10
    pmten = int.from_bytes(b"".join(data[4:6]), byteorder="little") / 10
    print(f"Indoor PM2.5: {pmtwofive}")
    print(f"Indoor PM10: {pmten}")
    aqi = convert_to_aqi(pmtwofive, pmten)
    print("Indoor AQI: ", aqi)

    influx.indoor_aqi(pmtwofive, pmten, aqi)


def get_indoor_stats():
    set_sensor_work()
    time.sleep(15)  # clear the sensor for more before an accurate reading
    sensor_read()
    time.sleep(1)
    sensor_sleep()
    time.sleep(1)
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
    time.sleep(15)  # clear the sensor for more before an accurate reading
    sensor_read()
    time.sleep(1)
    sensor_sleep()
    time.sleep(1)
    ser.close()


if __name__ == "__main__":
    main()
