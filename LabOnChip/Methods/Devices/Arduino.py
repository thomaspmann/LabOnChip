import serial
import time
import re


class Arduino:
    def __init__(self):
        super(Arduino, self).__init__()
        # Setup serial port to communicate with arduino
        self.ser = serial.Serial(
            port='COM3',
            baudrate=115200,
            timeout=5
        )

        # Initialise variables
        self.tempC = 0
        self.humidity = 0
        self.t_in = 0
        self.t_out = 0

        # Wait for arduino to fire up
        time.sleep(3)

        # Get current variable status
        self.request_data()
        time.sleep(3)
        self.get_data()
        self.request_data()

    def request_data(self):
        # Serial request temperature, humidity and thermocouple data (ArduinoV3)
        self.ser.write(b'UPDATE\n')

    def get_data(self):
        buffer_string = ''
        buffer_string += self.ser.read(self.ser.inWaiting()).decode('utf-8')
        if '\n' in buffer_string:
            last_received = buffer_string[:-2]  # Remove \n and \r
            # print(last_received)
            # Extract data from string
            result = re.findall(r"\d+\.\d+", last_received)
            # Convert to floats
            result = map(float, result)
            # Store results
            [self.tempC, self.humidity, self.t_in, self.t_out] = result
            # print(self.tempC, self.humidity, self.t_in, self.t_out)

    def log_arduino(self):
        # Used when arduino is constantly pumping out updates (i.e. threading required)
        buffer_string = ''
        while True:
            buffer_string += self.ser.read(self.ser.inWaiting()).decode('utf-8')
            if '\n' in buffer_string:
                last_received = buffer_string[:-2]  # Remove \n and \r
                print(last_received)
                # Extract data from string
                [self.tempC, self.humidity, self.t_in, self.t_out] = re.findall(r"\d+\.\d+", last_received)
                buffer_string = ''  # Reset buffer string
                print(self.tempC, self.humidity, self.t_in, self.t_out)

if __name__ == "__main__":
    arduino = Arduino()