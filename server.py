import threading
import time
import json
import logging
import random
import os
from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from blockchain_client import BlockchainClient
from hardware_interface import HardwareInterface

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SERVER] - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', static_url_path='')
app.secret_key = os.urandom(24)

# File for temporary local storage of new fingerprints
LOCAL_STORE = "local_fingerprints.json"

# Initialize Modules
try:
    bc_client = BlockchainClient()
except Exception as e:
    logger.error(f"Failed to init BlockchainClient: {e}")
    bc_client = None

try:
    hw_interface = HardwareInterface()
except Exception as e:
    logger.error(f"Failed to init HardwareInterface: {e}")
    hw_interface = None

# --- Helpers ---

def save_local_fingerprint(fp_data):
    """Saves fingerprint locally for temporary storage until Gov update"""
    data = []
    if os.path.exists(LOCAL_STORE):
        with open(LOCAL_STORE, 'r') as f:
            try:
                data = json.load(f)
            except:
                data = []
    data.append({
        "timestamp": time.time(),
        "data": fp_data
    })
    with open(LOCAL_STORE, 'w') as f:
        json.dump(data, f, indent=4)
    logger.info(f"**DUMMY CASE: Fingerprint {fp_data} saved locally (TEMP STORAGE)**")

# --- Routes ---

@app.route('/')
def index():
    return render_template('welcome.html')

@app.route('/api/check-button')
def check_button():
    if hw_interface:
        hw_interface.wait_for_button_press()
        return jsonify({"status": "success"})
    else:
        # If no hardware, just succeed immediately for testing (same as mock)
        time.sleep(1)
        return jsonify({"status": "success"})

@app.route('/api/container-level')
def container_level():
    """Returns the current grain level in the container."""
    if hw_interface:
        level = hw_interface.get_container_level()
        # Assume 200mm is empty and 50mm is full for the logic
        percentage = max(0, min(100, int((200 - level) / 1.5))) 
        return jsonify({"status": "success", "level_mm": level, "percentage": percentage})
    return jsonify({"status": "success", "level_mm": 100, "percentage": 50})

@app.route('/scan-rfid', methods=['GET', 'POST'])
def scan_rfid():
    if request.method == 'POST':
        # Simulated RFID input from keyboard (number keys)
        rfid_id = request.form.get('rfid_input')
        logger.info(f"**DUMMY CASE: RFID Card {rfid_id} scanned via keyboard input**")
        
        # Phase: Blockchain Check
        session['rfid'] = rfid_id
        return redirect(url_for('processing', step='blockchain'))
    return render_template('rfid_scan.html')

@app.route('/processing/<step>')
def processing(step):
    return render_template('loading.html', step=step)

@app.route('/api/verify-rfid')
def verify_rfid():
    rfid_id = session.get('rfid')
    logger.info(f"Checking Blockchain (DFO/Gov) for User with RFID: {rfid_id}...")
    
    # Simulate Blockchain delay
    time.sleep(2)
    
    user = None
    if bc_client and rfid_id:
        # Try real validation if card_id matches (in dummy mode we use 1-9)
        # For dummy, we accept 1, 2, 3 as valid users
        if rfid_id in ["1", "2", "3"]:
            user = {
                "id": f"BEN-{rfid_id}",
                "name": "Beneficiary User",
                "entitlement": 50,
                "remainingQuota": 45
            }
    
    if user:
        session['user'] = user
        logger.info(f"**DUMMY CASE: User {user['id']} found in Blockchain database**")
        return jsonify({"status": "success", "next": url_for('scan_fingerprint')})
    else:
        logger.error(f"**DUMMY CASE: No user found for RFID {rfid_id} in Blockchain**")
        return jsonify({"status": "error", "message": "ALERT ERROR: User not found in database!"})

@app.route('/scan-fingerprint', methods=['GET', 'POST'])
def scan_fingerprint():
    if request.method == 'POST':
        # Simulated Fingerprint input from keyboard (number keys)
        fp_id = request.form.get('fp_input')
        logger.info(f"**DUMMY CASE: Fingerprint {fp_id} scanned via keyboard input**")
        
        session['fingerprint'] = fp_id
        return redirect(url_for('processing', step='government'))
    return render_template('fingerprint_scan.html')

@app.route('/api/verify-fingerprint')
def verify_fingerprint():
    fp_id = session.get('fingerprint')
    logger.info(f"Sending Fingerprint data to Government for verification: {fp_id}...")
    
    # Simulate Government verification delay
    time.sleep(2)
    
    # Dummy logic: match if fp_id is same as rfid_id (e.g. key 1 for both)
    rfid_id = session.get('rfid')
    
    if fp_id == rfid_id:
        logger.info(f"**DUMMY CASE: Fingerprint match found in Government records**")
        return jsonify({"status": "success", "next": url_for('dispense')})
    else:
        # Save locally if not found (Legacy simulation, still logging)
        save_local_fingerprint(fp_id)
        logger.error(f"**DUMMY CASE: Fingerprint MISMATCH. Access Denied.**")
        return jsonify({"status": "error", "message": "SECURITY ALERT: Biometric data does not match the provided ID!"})

@app.route('/dispense')
def dispense():
    user = session.get('user')
    return render_template('dispense.html', user=user)

@app.route('/api/start-dispense')
def start_dispense():
    user = session.get('user', {"id": "GUEST"})
    amount = 5.0
    
    logger.info(f"**DUMMY CASE: Starting AUGER ROTATION (Motor Simulation)**")
    
    if hw_interface:
        hw_interface.dispense_grain(amount)
    else:
        # Simulated dispense time
        time.sleep(3)
        
    # Send last transaction to Hyperledger Fabric
    tx_id = "TX-MOCK-FINAL"
    if bc_client:
        tx_id = bc_client.submit_transaction(user['id'], "FPS-PUNE-001", amount)
    
    logger.info(f"**DUMMY CASE: Final transaction {tx_id} sent to Hyperledger Fabric**")
    
    return jsonify({"status": "completed", "tx_id": tx_id})

@app.route('/error')
def error():
    message = request.args.get('message', 'An unknown error occurred.')
    return render_template('error.html', message=message)

if __name__ == '__main__':
    # Add templates folder if not exists
    if not os.path.exists('templates'):
        os.makedirs('templates')
        
    # Run Flask with reduced overhead to mitigate overheating
    logger.info("Starting SSR Flask Server on 0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
