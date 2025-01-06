import serial
import serial.tools.list_ports
import sys
import select
import threading

# Function to list all available serial ports
def list_serial_ports():
    ports = list(serial.tools.list_ports.comports())
    available_ports = [port.device for port in ports]
    return available_ports

# Open the serial connection
def open_serial_connection(port, baud_rate=115200):
    ser = serial.Serial(port, baud_rate, timeout=1)
    return ser

# Function to send data in hex
def send_data(ser, data):
    hex_data = bytes.fromhex(data)
    ser.write(hex_data)

# Function to continuously read from the serial port
def read_from_serial(ser):
    while True:
        if ser.in_waiting > 0:
            received_hex = ser.read(ser.in_waiting)  # Read all available data
            print(f"Received data in hex: {received_hex.hex()}")

# Scan and list available serial ports
ports = list_serial_ports()
print("Available serial ports:", ports)

# Connect to the specific port if available
target_port = "/dev/ttyUSB0"
if target_port in ports:
    ser = open_serial_connection(target_port)
    print(f"Connected to {target_port}")

    # Start a thread to continuously read from the serial port
    read_thread = threading.Thread(target=read_from_serial, args=(ser,))
    read_thread.daemon = True  # This makes the thread exit when the main program exits
    read_thread.start()

    print("Type something to send to the serial port, and press Enter.")
    print("Press Ctrl+C to exit.")

    try:
        while True:
            # Read user input and send data
            user_input = input("Enter data to send in hex: ")

            # Convert input to hex and send it
            hex_data = ' '.join(f"{ord(c):02x}" for c in user_input)  # Convert each char to hex
            send_data(ser, hex_data)

            print(f"Sent data: {hex_data}")

    except KeyboardInterrupt:
        print("\nExiting program.")
        ser.close()
else:
    print(f"{target_port} not found in available ports.")
