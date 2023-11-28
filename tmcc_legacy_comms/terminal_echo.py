# Jimmy trains animator board basic UART communications.

import board
import busio

uart = busio.UART(board.GP0, board.GP1, baudrate=9600, bits=8, parity=None, stop=1)

#basic terminal echo to see if uart is working on animator board
while True:
    # Check if there's any data available to read from UART
    if uart.in_waiting > 0:
        # Read data from UART and decode it
        received_data = uart.read(uart.in_waiting).decode('utf-8')
        print("Received: ", received_data)
        if received_data == '\r': received_data='\r\n'
        # Echo back the received data
        uart.write(received_data.encode('utf-8'))
