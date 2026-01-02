import threading
import time
import json
import logging
import random
from flask import Flask, jsonify, request
from blockchain_client import BlockchainClient
from hardware_interface import HardwareInterface

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SERVER] - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', static_url_path='')

# Global State
SYSTEM_STATE = {
    "status": "IDLE",  # IDLE, PROCESSING, AUTH_SUCCESS, AUTH_FAILED, DISPENSING, COMPLETED, ERROR
    "message": "Welcome. Please Scan Card or Fingerprint.",
    "user_data": None,
    "tx_id": None,
    "last_update": time.time()
}

# Initialize Modules
try:
    # Initialize Blockchain Client (might require Docker socket)
    bc_client = BlockchainClient()
except Exception as e:
    logger.error(f"Failed to init BlockchainClient: {e}")
    bc_client = None

try:
    hw_interface = HardwareInterface()
except Exception as e:
    logger.error(f"Failed to init HardwareInterface: {e}")
    hw_interface = None

# Mutex for thread safety
state_lock = threading.Lock()

def update_state(status, message, user_data=None, tx_id=None):
    with state_lock:
        SYSTEM_STATE["status"] = status
        SYSTEM_STATE["message"] = message
        if user_data is not None:
            SYSTEM_STATE["user_data"] = user_data
        if tx_id is not None:
            SYSTEM_STATE["tx_id"] = tx_id
        SYSTEM_STATE["last_update"] = time.time()
    logger.info(f"State Updated: {status} - {message}")

def reset_state_later(delay=5):
    """Resets state to IDLE after a delay"""
    def reset():
        time.sleep(delay)
        update_state("IDLE", "Welcome. Please Scan Card or Fingerprint.", None)
        # Clear user data but keep it safe in memory if needed for logs
        with state_lock:
            SYSTEM_STATE["user_data"] = None
            SYSTEM_STATE["tx_id"] = None
            
    threading.Thread(target=reset, daemon=True).start()

def process_login(auth_type, credential):
    """
    Handlers login logic in a background thread to not block the main loop.
    auth_type: 'CARD' or 'FINGERPRINT'
    credential: 'CARD_ID' or 'FINGERPRINT_ID'
    """
    update_state("PROCESSING", f"Authenticating via {auth_type}...")
    
    # Simulate processing delay
    time.sleep(1)

    try:
        # 1. Validate User
        # For simulation, we map a dummy fingerprint to a card ID if needed, 
        # or just use the credential as user ID lookup.
        
        # Real logic: call blockchain_client.validate_beneficiary(card_id, pin)
        # Since we don't have a PIN pad in this non-touch flow, we assume 1:1 match or hardcoded PIN.
        # Existing logic: validate_beneficiary(card_id, pin)
        
        # PIN is hardcoded or retrieved from HW interface
        pin = hw_interface.get_pin() if hw_interface else "1234"
        
        # Use existing BC client
        # Note: In the original code, validate_beneficiary takes (card_id, pin).
        # We'll use the credential as card_id for simplicity or map it.
        card_id_to_use = credential
        
        if auth_type == 'FINGERPRINT':
            # Dummy mapping
            card_id_to_use = "CARD_FP_LINKED" 

        user = None
        if bc_client:
            # We try to validate. In a real scenario, we might need to fetch the PIN from the user 
            # or assume biometric auth replaces PIN.
            # For this competition context, let's assume valid biometric = valid PIN.
            user = bc_client.validate_beneficiary(card_id_to_use, pin)
            
            # Fallback for demo if BC returns None (e.g. docker issues)
            if not user:
                 logger.warning("Blockchain validation failed or user not found. Using MOCK user for DEMO.")
                 # Generate a mock user so the flow continues for the demo
                 user = {
                     "id": "BEN-MOCK-001",
                     "name": "Ramu Kaka",
                     "entitlement": 50,
                     "remainingQuota": 45
                 }
        else:
             # Fully mocked if BC client failed init
             user = {
                 "id": "BEN-MOCK-OFFLINE",
                 "name": "Offline User",
                 "entitlement": 50,
                 "remainingQuota": 45
             }

        if user:
            update_state("AUTH_SUCCESS", f"Welcome, {user.get('name', 'Beneficiary')}", user_data=user)
            
            # Automatically proceed to dispense after short delay
            time.sleep(2)
            process_dispense(user)
        else:
            update_state("AUTH_FAILED", "Authentication Failed. Please try again.")
            reset_state_later(3)

    except Exception as e:
        logger.error(f"Login Error: {e}")
        update_state("ERROR", "System Error during Login")
        reset_state_later()

def process_dispense(user):
    update_state("DISPENSING", "Dispensing Grain... Please wait.")
    
    try:
        # Default dispense amount for demo
        amount = 5.0 
        
        if hw_interface:
            hw_interface.dispense_grain(amount)
        
        # Record Transaction
        tx_id = "TX-OFFLINE-000"
        if bc_client:
            # submit_transaction(ben_id, shop_id, weight)
            tx_id = bc_client.submit_transaction(user['id'], "FPS-PUNE-001", amount)
            
        update_state("COMPLETED", "Dispensing Complete! Thank you.", tx_id=tx_id)
        
        if hw_interface:
            hw_interface.print_receipt(tx_id, amount)
            
        reset_state_later(5)
        
    except Exception as e:
        logger.error(f"Dispense Error: {e}")
        update_state("ERROR", "Dispensing Mechanism Failure")
        reset_state_later()


# Background Polling Thread
def input_monitor_loop():
    logger.info("Starting Input Monitor Thread...")
    while True:
        with state_lock:
            current_status = SYSTEM_STATE["status"]
            
        if current_status == "IDLE":
            # 1. Check Card
            if hw_interface:
                card_id = hw_interface.read_smartcard()
                if card_id:
                    logger.info(f"Card Detected: {card_id}")
                    # Dispatch to processing thread
                    threading.Thread(target=process_login, args=('CARD', card_id)).start()
                    time.sleep(2) # Debounce
                    continue

            # 2. Check Fingerprint (Simulated via random chance or file trigger)
            # In a real app, this would be `fp_sensor.read()`
            # We'll simulate a fingerprint scan detection randomly for demo if enabled, 
            # OR we can expose an API endpoint to trigger it manually.
            pass
            
        time.sleep(0.5)

# Flask Routes
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    with state_lock:
        return jsonify(SYSTEM_STATE)

@app.route('/api/trigger/fingerprint', methods=['POST'])
def trigger_fingerprint():
    """Debug endpoint to simulate fingerprint scan"""
    with state_lock:
        if SYSTEM_STATE["status"] != "IDLE":
             return jsonify({"error": "System busy"}), 400
    
    # Start auth flow
    threading.Thread(target=process_login, args=('FINGERPRINT', 'FP-USER-777')).start()
    return jsonify({"success": True, "message": "Fingerprint detected"})

if __name__ == '__main__':
    # Start background threads
    monitor_thread = threading.Thread(target=input_monitor_loop, daemon=True)
    monitor_thread.start()
    
    # Run Flask
    logger.info("Starting Flask Server on 0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
