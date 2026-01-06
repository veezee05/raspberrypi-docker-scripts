from gpiozero import Button
from time import time
from signal import pause

# Ignores any changes that happen within 0.05 seconds of the first change
button = Button(24, bounce_time=0.05)

# Variable to store the start time
start_time = 0

def pressed():
    global start_time
    # Capture the exact time the button went DOWN
    start_time = time()

def released():
    global start_time
    # Capture the time the button went UP
    end_time = time()
    
    # Calculate duration
    duration = end_time - start_time
    
    # Only print one entry once the cycle is complete
    print(f"Button event completed! Held for: {duration:.2f} seconds")

# Link the events
button.when_pressed = pressed
button.when_released = released

print("Ready! Press and hold the button, then release.")
pause()