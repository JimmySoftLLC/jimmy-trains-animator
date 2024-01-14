import board
import digitalio
import busio

print("Hello blinka!")

# Try to great a Digital input
pin = digitalio.DigitalInOut(board.D17) #SW-1
pin = digitalio.DigitalInOut(board.D27) #SW-2
pin = digitalio.DigitalInOut(board.D22) #SW-3
pin = digitalio.DigitalInOut(board.D5) #SW-4
pin = digitalio.DigitalInOut(board.D6) #M-1
pin = digitalio.DigitalInOut(board.D13) #M-2
pin = digitalio.DigitalInOut(board.D23) #M-3
pin = digitalio.DigitalInOut(board.D24) #M-4
pin = digitalio.DigitalInOut(board.D25) #M-5
pin = digitalio.DigitalInOut(board.D12) #M-6
pin = digitalio.DigitalInOut(board.D16) #M-7
pin = digitalio.DigitalInOut(board.D20) #M-8

print("Digital IO ok!")

# Try to create an I2C device
i2c = busio.I2C(board.SCL, board.SDA)
print("I2C ok!")

# Try to create an SPI device
spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)
print("SPI ok!")

print("done!")