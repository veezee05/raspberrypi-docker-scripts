import board
import busio
from adafruit_vl53l0x import VL53L0X
import time

# Initialize I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Create sensor object
sensor = VL53L0X(i2c)

print("Reading distances (mm):")
while True:
    try:
        distance = sensor.range
        print(f"Distance: {distance} mm ({distance / 10:.1f} cm)")
        time.sleep(0.5) # Add delay between readings
    except OSError as e:
        print(f"I2C Error: {e}")
        print("Retrying...")
        time.sleep(1)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(1)