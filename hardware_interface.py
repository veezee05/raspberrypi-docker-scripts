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
        print("[HW] Drivers Loaded Successfully.")
    except ImportError:
        print("[HW] CRITICAL: Real Hardware libraries missing! Falling back to MOCK.")
        REAL_HARDWARE = False

class HardwareInterface:
    def __init__(self):
        print(f"[HW] Initializing Hardware Interface... (Mode: {'REAL' if REAL_HARDWARE else 'MOCK'})")
        self.lid_open = False
        if REAL_HARDWARE:
             self._setup_gpio()

    def _setup_gpio(self):
        # Using gpiozero which handles setmode internally
        # pull_up=True means the pin is HIGH by default, and button pulls it to GND (LOW).
        # This is the most common configuration for Raspberry Pi buttons.
        self.button = Button(24, pull_up=True, bounce_time=0.1) if REAL_HARDWARE else None
        self.motor = PWMOutputDevice(18) if REAL_HARDWARE else None
        
        status = "REAL" if REAL_HARDWARE else "MOCK"
        print(f"[HW] GPIO Configured ({status}): Button(24, pull_up=True), Motor(18)")

    def wait_for_button_press(self):
        """Blocks until the physical button is pressed."""
        if REAL_HARDWARE:
            print("[HW] Waiting for PHYSICAL button press on GPIO 24...")
            # wait_for_press blocks until the pin goes LOW (since pull_up=True)
            self.button.wait_for_press()
            print("[HW] PHYSICAL button pressed!")
        else:
            print("[HW] MOCK: Waiting for button... (Simulating 2s delay)")
            # In mock mode, we wait a bit so it doesn't "automatically" skip the page
            time.sleep(2)
            print("[HW] MOCK: Button simulation complete.")
        return True

    def read_smartcard(self):
        if REAL_HARDWARE:
            # Implement real pyscard logic
            r = readers()
            if len(r) > 0:
                conn = r[0].createConnection()
                conn.connect()
                return "REAL_CARD_ID"
            return None
        else:
            # Simulation Mode
            print("\n[HW] Waiting for Smartcard... (Press Enter to Simulate Swipe)")
            time.sleep(1) 
            card_id = "CARD123"
            print(f"[HW] Card Detected: {card_id}")
            return card_id

    def get_pin(self):
        if REAL_HARDWARE:
            # Implement Matrix Keypad Logic
            return "1234"
        else:
            return "1234" # Dummy PIN

    def get_weight(self):
        if REAL_HARDWARE:
            # Implement HX711 Logic
            return 5.0
        else:
            # Simulation Mode
            weight = random.uniform(0.0, 5.0)
            return weight

    def dispense_grain(self, target_weight):
        print(f"[HW] Dispensing {target_weight} kg...")
        self.lid_open = True
        
        if REAL_HARDWARE:
            # Motor ON (Full speed)
            self.motor.value = 1.0
        else:
            print("**DUMMY CASE: Auger Motor ON / Lid OPEN**")
        
        # Helper loop
        current_weight = 0.0
        while current_weight < target_weight:
            time.sleep(0.5)
            if REAL_HARDWARE:
                 # Read Scale
                 current_weight += 0.5 # Simulation-like increment for now
            else:
                 current_weight += random.uniform(0.5, 1.0)
            
            if current_weight > target_weight:
                current_weight = target_weight
            print(f"[HW] Dispensed: {current_weight:.2f} kg")
        
        self.lid_open = False
        if REAL_HARDWARE:
            # Motor OFF
            self.motor.off()
        else:
             print("**DUMMY CASE: Auger Motor OFF / Lid CLOSED**")
             
        return current_weight

    def print_receipt(self, tx_id, weight):
        """
        Simulates Thermal Printer.
        """
        print("-" * 30)
        print("      RECEIPT      ")
        print(f"TxID: {tx_id}")
        print(f"Weight: {weight:.2f} kg")
        print(f"Time: {time.ctime()}")
        print("-" * 30)
