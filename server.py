import json
import logging
import time
import re
import os
from flask import Flask, request, jsonify
from functools import wraps
from datetime import datetime

app = Flask(__name__)

# Pre-defined device IDs - set these to whatever you named them on the pico
VALID_DEVICE_IDS = {"NAME_OF_DEVICE1", "NAME_OF_DEVICE2", "NAME_OF_DEVICE3", "NAME_OF_DEVICE4", "NAME_OF_DEVICE5"}

# File to store device states
DEVICE_STATE_FILE = "device_states.json"

# Allowed states for the devices
ALLOWED_STATES = {"OFF", "RED", "GREEN", "BLUE", "NULL"}

# API key for authentication - Change to whatever
API_KEY = "A_RANDOM_STRING_OF_WHATEVER_PLEASE_CHANGE_ME"

# Log file paths
ERROR_LOG_FILE = "logs/server_error.log"
INFO_LOG_FILE = "logs/server_info.log"

# Ensure log directories exist
os.makedirs(os.path.dirname(ERROR_LOG_FILE), exist_ok=True)
os.makedirs(os.path.dirname(INFO_LOG_FILE), exist_ok=True)

# Set up custom logging for errors (will write to server_error.log)
error_handler = logging.FileHandler(ERROR_LOG_FILE)
error_handler.setLevel(logging.ERROR)
error_formatter = logging.Formatter('%(asctime)s ERROR: %(message)s', datefmt='%m/%d/%Y %I:%M%p')
error_handler.setFormatter(error_formatter)
app.logger.addHandler(error_handler)

# Set up custom logging for info messages (200 status code, will write to server_info.log)
info_handler = logging.FileHandler(INFO_LOG_FILE)
info_handler.setLevel(logging.INFO)
info_formatter = logging.Formatter('%(asctime)s Device "%(device_id)s" checked in as "%(state)s".', datefmt='%m/%d/%Y %I:%M%p')
info_handler.setFormatter(info_formatter)
app.logger.addHandler(info_handler)

# Load device states from file if it exists
try:
    with open(DEVICE_STATE_FILE, "r") as file:
        devices = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    devices = {}

def log_message(log_file, message_type, device_id=None, state=None, error=None):
    """
    Append a formatted log message to the specified log file.
    """
    timestamp = datetime.now().strftime("[%m/%d/%Y %I:%M%p]")
    if error:
        log_entry = f"{timestamp} ERROR: {error}"
    else:
        log_entry = f"{timestamp} Device \"{device_id}\" checked in as \"{state}\"."

    with open(log_file, "a") as file:
        file.write(log_entry + "\n")

def validate_device_id(device_id):
    """
    Validate the device ID by checking if it exists in the predefined set.
    """
    return device_id in VALID_DEVICE_IDS

def validate_state(state):
    """
    Check if the provided state is within allowed values.
    """
    return state in ALLOWED_STATES

def require_api_key(f):
    """
    Decorator to require API key for accessing the endpoint.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if not api_key or api_key != API_KEY:
            error_msg = "Unauthorized: Invalid or missing API key"
            log_message(ERROR_LOG_FILE, message_type="ERROR", error=error_msg)
            return jsonify({'error': error_msg}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/update_state', methods=['POST'])
@require_api_key
def update_state():
    try:
        data = request.get_json()
        if not data:
            error_msg = "Invalid input: No JSON payload provided"
            log_message(ERROR_LOG_FILE, message_type="ERROR", error=error_msg)
            return jsonify({'error': error_msg}), 400

        device_id = data.get('device_id')
        state = data.get('state')
        heartbeat = data.get('heartbeat')

        # Validate device_id
        if not device_id or not validate_device_id(device_id):
            error_msg = "Invalid device identifier"
            log_message(ERROR_LOG_FILE, message_type="ERROR", error=error_msg)
            return jsonify({'error': error_msg}), 400

        # Handle heartbeat updates
        if heartbeat == "alive":
            devices[device_id] = devices.get(device_id, {})
            devices[device_id]['last_updated'] = int(time.time())
            with open(DEVICE_STATE_FILE, "w") as file:
                json.dump(devices, file)
            return jsonify({'message': f'Device {device_id} heartbeat acknowledged'}), 200

        # Validate state
        if not state or not validate_state(state):
            error_msg = "Invalid state"
            log_message(ERROR_LOG_FILE, message_type="ERROR", error=error_msg)
            return jsonify({'error': error_msg}), 400

        # Update the device state with epoch time
        devices[device_id] = {
            'state': state,
            'last_updated': int(time.time())
        }

        # Write updated states to file
        with open(DEVICE_STATE_FILE, "w") as file:
            json.dump(devices, file)

        log_message(INFO_LOG_FILE, message_type="INFO", device_id=device_id, state=state)
        return jsonify({'message': f'Device {device_id} updated to state {state}'}), 200

    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        log_message(ERROR_LOG_FILE, message_type="ERROR", error=error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/api/get_state/<device_id>', methods=['GET'])
@require_api_key
def get_state(device_id):
    # Validate device_id
    if not validate_device_id(device_id):
        error_msg = "Invalid device identifier"
        log_message(ERROR_LOG_FILE, message_type="ERROR", error=error_msg)
        return jsonify({'error': error_msg}), 400

    # Get the device state
    device_data = devices.get(device_id)
    if device_data is None:
        error_msg = "Device not found"
        log_message(ERROR_LOG_FILE, message_type="ERROR", error=error_msg)
        return jsonify({'error': error_msg}), 404

    log_message(INFO_LOG_FILE, message_type="INFO", device_id=device_id, state=device_data['state'])
    return jsonify({'device_id': device_id, 'state': device_data['state'], 'last_updated': device_data['last_updated']}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

