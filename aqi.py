import sds011
import serial
import logging
import time

# sensor = SDS011("/dev/ttyUSB0", use_query_mode=True)
# sensor.set_work_period(work_time=0)  # work_time is continuous
# logging.debug("waking sensor")
# sensor.sleep(sleep=False)  # wake sensor
# logging.debug("waiting 30 seconds")
# time.sleep(30)  # capture 30 seconds of data
# logging.debug("running sensor query")
# result = sensor.query()
# logging.debug("sleeping sensor")
# sensor.sleep()  # sleep sensor

# pm25, pm10 = result
# print(f"    PMT2.5: {pm25} μg/m3    PMT10 : {pm10} μg/m3")


import serial, time, struct, sys


ser = serial.Serial()
ser.port = "/dev/ttyUSB0"
ser.baudrate = 9600

if ser.isOpen() == False:
    ser.open()
ser.reset_input_buffer()


def dump_data(d):
    print(" ".join(x.encode("hex") for x in d))


def sensor_wake():
    # s = "\x01"
    # b = s.encode()
    ser.write("\x01".encode())


def set_working_period():
    bytes = [
        "\xaa",  # head
        "\xb4",  # command 1
        "\x08",  # data byte 1
        "\x01",  # data byte 2 (set mode)
        "\x00",  # data byte 3 (continuous working period)
        "\x00",  # data byte 4
        "\x00",  # data byte 5
        "\x00",  # data byte 6
        "\x00",  # data byte 7
        "\x00",  # data byte 8
        "\x00",  # data byte 9
        "\x00",  # data byte 10
        "\x00",  # data byte 11
        "\x00",  # data byte 12
        "\x00",  # data byte 13
        "\xff",  # data byte 14 (device id byte 1)
        "\xff",  # data byte 15 (device id byte 2)
        "\x05",  # checksum
        "\xab",  # tail
    ]
    for b in bytes:
        ser.write(b.encode())


def set_reporting_mode():
    bytes = [
        "\xaa",  # head
        "\xb4",  # command 1
        "\x02",  # data byte 1
        "\x01",  # data byte 2 (set mode)
        "\x00",  # data byte 3 (setting to active mode)
        "\x00",  # data byte 4
        "\x00",  # data byte 5
        "\x00",  # data byte 6
        "\x00",  # data byte 7
        "\x00",  # data byte 8
        "\x00",  # data byte 9
        "\x00",  # data byte 10
        "\x00",  # data byte 11
        "\x00",  # data byte 12
        "\x00",  # data byte 13
        "\xff",  # data byte 14 (device id byte 1)
        "\xff",  # data byte 15 (device id byte 2)
        "\x05",  # checksum
        "\xab",  # tail
    ]
    for b in bytes:
        ser.write(b.encode())


def sensor_sleep():
    bytes = [
        "\xaa",  # head
        "\xb4",  # command 1
        "\x06",  # data byte 1
        "\x01",  # data byte 2 (set mode)
        "\x00",  # data byte 3 (sleep)
        "\x00",  # data byte 4
        "\x00",  # data byte 5
        "\x00",  # data byte 6
        "\x00",  # data byte 7
        "\x00",  # data byte 8
        "\x00",  # data byte 9
        "\x00",  # data byte 10
        "\x00",  # data byte 11
        "\x00",  # data byte 12
        "\x00",  # data byte 13
        "\xff",  # data byte 14 (device id byte 1)
        "\xff",  # data byte 15 (device id byte 2)
        "\x05",  # checksum
        "\xab",  # tail
    ]
    for b in bytes:
        ser.write(b.encode())


def sensor_read():
    for i in range(0, 10):
        data = []
        for _ in range(0, 10):
            datum = ser.read()
            data.append(datum)

        pmtwofive = int.from_bytes(b"".join(data[2:4]), byteorder="little") / 10
        print(f"PM2.5 #{i+1}: {pmtwofive}")
        pmten = int.from_bytes(b"".join(data[4:6]), byteorder="little") / 10
        print(f"PM10 #{i+1}: {pmten}\n")
        time.sleep(2)


def main():
    sensor_wake()
    time.sleep(10)
    ser.reset_input_buffer()
    set_working_period()
    ser.reset_input_buffer()
    set_reporting_mode()
    ser.reset_input_buffer()
    sensor_read()
    sensor_sleep()


if __name__ == "__main__":
    main()
