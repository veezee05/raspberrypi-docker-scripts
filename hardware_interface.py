import time
import random
import os

# Set this to "TRUE" in environment when deploying to Raspberry Pi
REAL_HARDWARE = os.getenv("REAL_HARDWARE", "FALSE").upper() == "TRUE"

if REAL_HARDWARE:
    try:
        import RPi.GPIO as GPIO
        from gpiozero import Button, PWMOutputDevice
        from hx711 import HX711
        from smartcard.System import readers
        # Integrated from vl53l0x.py
        import board
        import busio
        from adafruit_vl53l0x import VL53L0X
        print("[HW] Drivers Loaded Successfully.")
    except ImportError:
        print("[HW] CRITICAL: Real Hardware libraries missing! Falling back to MOCK.")
        REAL_HARDWARE = False

class HardwareInterface:
    def __init__(self):
        print(f"[HW] Initializing Hardware Interface... (Mode: {'REAL' if REAL_HARDWARE else 'MOCK'})")
        self.lid_open = False
        # From button.py: state for timing
        self.button_start_time = 0 
        
        if REAL_HARDWARE:
             self._setup_gpio()
             self._setup_sensors()

    def _setup_gpio(self):
        # Integrated from button.py and original hardware_interface.py
        # pull_up=True means pin is HIGH by default, button pulls to GND
        self.button = Button(24, pull_up=True, bounce_time=0.05) if REAL_HARDWARE else None
        
        # Link events from button.py logic
        if REAL_HARDWARE:
            self.button.when_pressed = self._button_pressed_callback
            self.button.when_released = self._button_released_callback

        # Integrated from motor.py: PWM on GPIO 18
        self.motor = PWMOutputDevice(18) if REAL_HARDWARE else None
        
        status = "REAL" if REAL_HARDWARE else "MOCK"
        print(f"[HW] GPIO Configured ({status}): Button(24, pull_up=True), Motor(18)")

    def _setup_sensors(self):
        """Integrated from vl53l0x.py for I2C distance sensing."""
        if REAL_HARDWARE:
            try:
                self.i2c = busio.I2C(board.SCL, board.SDA)
                self.tof_sensor = VL53L0X(self.i2c)
                print("[HW] VL53L0X Distance Sensor Initialized.")
            except Exception as e:
                print(f"[HW] VL53L0X Init Error: {e}")
                self.tof_sensor = None

    # --- Button Logic from button.py ---
    def _button_pressed_callback(self):
        self.button_start_time = time.time()

    def _button_released_callback(self):
        duration = time.time() - self.button_start_time
        print(f"[HW] Button event completed! Held for: {duration:.2f} seconds")

    def wait_for_button_press(self):
        """Blocks until the physical button is pressed."""
        if REAL_HARDWARE:
            print("[HW] Waiting for PHYSICAL button press on GPIO 24...")
            self.button.wait_for_press()
            print("[HW] PHYSICAL button pressed!")
        else:
            print("[HW] MOCK: Waiting for button... (Simulating 2s delay)")
            time.sleep(2)
            print("[HW] MOCK: Button simulation complete.")
        return True

    # --- Sensor Logic from vl53l0x.py ---
    def get_container_level(self):
        """Reads distance from VL53L0X sensor in mm."""
        if REAL_HARDWARE and self.tof_sensor:
            try:
                return self.tof_sensor.range
            except Exception as e:
                print(f"[HW] Distance Sensor Error: {e}")
                return -1
        return random.randint(50, 200) # Mock distance

    # --- Existing Functionality ---
    def read_smartcard(self):
        if REAL_HARDWARE:
            r = readers()
            if len(r) > 0:
                conn = r[0].createConnection()
                conn.connect()
                return "REAL_CARD_ID"
            return None
        else:
            print("\n[HW] Waiting for Smartcard... (Press Enter to Simulate Swipe)")
            time.sleep(1)
            card_id = "CARD123"
            print(f"[HW] Card Detected: {card_id}")
            return card_id

    def get_pin(self):
        return "1234" # Placeholder

    def get_weight(self):
        if REAL_HARDWARE:
            # Placeholder for HX711 logic
            return 5.0
        else:
            return random.uniform(0.0, 5.0)

    def dispense_grain(self, target_weight):
        print(f"[HW] Dispensing {target_weight} kg...")
        self.lid_open = True
        
        if REAL_HARDWARE:
            # Motor ON - Integrated from motor.py speed tests
            self.motor.value = 1.0
        else:
            print("**DUMMY CASE: Auger Motor ON / Lid OPEN**")
        
        current_weight = 0.0
        while current_weight < target_weight:
            time.sleep(0.5)
            if REAL_HARDWARE:
                 current_weight += 0.5 # Logic for HX711 integration
            else:
                 current_weight += random.uniform(0.5, 1.0)
            
            if current_weight > target_weight:
                current_weight = target_weight
            print(f"[HW] Dispensed: {current_weight:.2f} kg")
        
        self.lid_open = False
        if REAL_HARDWARE:
            self.motor.off() # Integrated from motor.py
        else:
             print("**DUMMY CASE: Auger Motor OFF / Lid CLOSED**")
             
        return current_weight

    def print_receipt(self, tx_id, weight):
        print("-" * 30)
        print("      RECEIPT      ")
        print(f"TxID: {tx_id}")
        print(f"Weight: {weight:.2f} kg")
        print(f"Time: {time.ctime()}")
        print("-" * 30)