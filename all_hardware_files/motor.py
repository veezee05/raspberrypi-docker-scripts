from gpiozero import PWMOutputDevice
from time import sleep

# Initialize the motor on GPIO 18
# We use PWMOutputDevice because your config specifies "PWM capable"
motor = PWMOutputDevice(18)

try:
    print("Starting motor test...")
    
    # 1. Slow Speed (20%)
    print("Running at 20% speed")
    motor.value = 0.2
    sleep(2)
    
    # 2. Medium Speed (50%)
    print("Running at 50% speed")
    motor.value = 0.5
    sleep(2)
    
    # 3. Full Speed (100%)
    print("Running at full speed")
    motor.value = 1.0
    sleep(3)
    
    # 4. Stop
    print("Stopping motor")
    motor.off()

except KeyboardInterrupt:
    print("\nTest interrupted by user")
    motor.off()

print("Test complete.")