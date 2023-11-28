# Jimmy trains animator board tmcc communications.

import board
import busio

uart = busio.UART(board.GP0, board.GP1, baudrate=9600, bits=8, parity=None, stop=1)

# the following is to help decode Lionel tmcc commands
while True:
    if uart.in_waiting >= 3:  # Check if at least 3 bytes are available to read
        received_data = uart.read(3)
        if len(received_data) == 3 and received_data[0] == 0x0F:
            word1, word2 = received_data[1], received_data[2]
            
            # Convert words to binary strings
            binary_word1 = format(word1, '016b')  # Represent as 16-bit binary
            binary_word2 = format(word2, '016b')  # Represent as 16-bit binary
            
            print("Received command:")
            print(f"Word 1: {binary_word1}")
            print(f"Word 2: {binary_word2}\n")
            
            # Reconstruct the command bytes
            reconstructed_word1 = int(binary_word1, 2).to_bytes(2, 'big')
            reconstructed_word2 = int(binary_word2, 2).to_bytes(2, 'big')
            
            # Construct the command to send back
            reconstructed_command = bytes([0x0F]) + reconstructed_word1 + reconstructed_word2
            
            # Echo back the received command
            uart.write(reconstructed_command)  # Echo back the received command
        else:
            # Invalid command format, discard the data
            uart.read(uart.in_waiting)