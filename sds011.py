import serial
import time
import aqi
import influx

class SDS011Sensor:
    """Class to handle SDS011 sensor interactions"""

    def __init__(self, port="/dev/ttyUSB0", baudrate=9600):
        """Initialize the sensor with the given port and baudrate"""
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = baudrate
        self.serial_open()

    def serial_open(self):
        """Open the serial connection if not already open"""
        if not self.ser.isOpen():
            try:
                self.ser.open()
                self.ser.reset_input_buffer()
                time.sleep(0.1)
                self.ser.reset_output_buffer()
                time.sleep(0.1)
                return True
            except Exception as e:
                print(f"Error opening serial port: {e}")
                return False
        return True

    def serial_close(self):
        """Close the serial connection if open"""
        if self.ser.isOpen():
            self.ser.close()

    def send_command(self, bytes_data):
        """Send byte data to SDS011"""
        if not self.serial_open():
            return False

        try:
            self.ser.write(bytes_data)
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            return False

    def calculate_checksum(self, data):
        """Calculate checksum for the command packet"""
        datalist = []
        for byte in data:
            datalist.append(int.from_bytes(byte, "little"))

        checksum = sum(datalist) % 256
        return bytes([checksum])

    def set_command(self, data_byte_1, data_byte_2, data_byte_3, data_byte_4, data_byte_5):
        """Create byte array and prepare to send to sensor"""
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
        checksum = self.calculate_checksum(bytes_data[2:])
        bytes_data.append(checksum)
        bytes_data.append(b"\xAB")  # tail

        return self.send_command(b"".join(bytes_data))

    def sleep(self):
        """Put sensor to sleep"""
        return self.set_command(b"\x06", b"\x01", b"\x00", b"\x00", b"\x00")

    def wake(self):
        """Wake sensor from sleep and set to 'work' mode"""
        return self.set_command(b"\x06", b"\x01", b"\x01", b"\x00", b"\x00")

    def set_reporting_mode(self):
        """Set to active mode"""
        return self.set_command(b"\x02", b"\x01", b"\x00", b"\x00", b"\x00")

    def set_working_period(self):
        """Set working mode to 'continuous'"""
        return self.set_command(b"\x08", b"\x01", b"\x00", b"\x00", b"\x00")

    def query_data(self):
        """Query the sensor for new readings"""
        return self.set_command(b"\x04", b"\x00", b"\x00", b"\x00", b"\x00")

    def read_measurement(self):
        """Read a measurement from the sensor"""
        if not self.serial_open():
            return None, None

        self.ser.reset_input_buffer()
        time.sleep(0.1)
        self.ser.reset_output_buffer()
        time.sleep(0.1)

        # Wait for data availability
        timeout = time.time() + 3.0  # 3 second timeout
        while self.ser.in_waiting < 10:
            if time.time() > timeout:
                print("Timeout waiting for sensor data")
                return None, None
            time.sleep(0.1)

        data = []
        for _ in range(0, 10):
            try:
                datum = self.ser.read()
                data.append(datum)
            except Exception as e:
                print(f"Error reading from sensor: {e}")
                return None, None

        # Validate packet structure
        if data[0] != b'\xaa' or data[9] != b'\xab':
            print("Invalid packet structure")
            return None, None

        # Extract PM values
        pmtwofive = int.from_bytes(b"".join(data[2:4]), byteorder="little") / 10
        pmten = int.from_bytes(b"".join(data[4:6]), byteorder="little") / 10

        return pmtwofive, pmten

    def convert_to_aqi(self, pmtwofive, pmten):
        """Convert PM measurements to AQI using EPA formula"""
        if pmtwofive is None or pmten is None:
            return None

        # Safety check for extremely high values
        if pmtwofive >= 500:
            return 500  # AQI scales typically max out at 500

        try:
            # Using the PM2.5 as the primary determinant of AQI
            calculated_aqi = aqi.to_aqi([(aqi.POLLUTANT_PM25, pmtwofive)])
            return calculated_aqi
        except Exception as e:
            print(f"Error converting to AQI: {e}")
            return None

# Functions for use in the main application

def get_indoor_stats():
    """Get indoor air quality measurements and send to InfluxDB"""
    sensor = SDS011Sensor()

    try:
        # Wake up the sensor
        sensor.wake()
        # Wait for the sensor to warm up and clear the chamber
        print("Warming up SDS011 sensor...")
        time.sleep(20)

        # Query for new data
        sensor.query_data()
        time.sleep(0.5)

        # Read measurement
        pmtwofive, pmten = sensor.read_measurement()

        if pmtwofive is not None and pmten is not None:
            print(f"Indoor PM2.5: {pmtwofive}")
            print(f"Indoor PM10: {pmten}")

            # Convert to AQI
            aqi_value = sensor.convert_to_aqi(pmtwofive, pmten)

            if aqi_value is not None:
                print(f"Indoor AQI: {aqi_value}")
                # Send to InfluxDB
                influx.indoor_aqi(pmtwofive, pmten, aqi_value)
            else:
                print("Failed to calculate AQI")

        else:
            print("Failed to get PM measurements")

    except Exception as e:
        print(f"Error in get_indoor_stats: {e}")

    finally:
        # Put sensor to sleep to save its lifespan
        sensor.sleep()
        time.sleep(0.5)
        # Close the serial connection
        sensor.serial_close()

def main():
    """Test function for direct module execution"""
    get_indoor_stats()

if __name__ == "__main__":
    main()