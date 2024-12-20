import json
import time
from datetime import datetime
from collections import defaultdict

# File paths
DEVICE_STATE_FILE = "device_states.json"
SCOREBOARD_FILE = "scoreboard.json"

# Duration in seconds to consider a device as online (5 minutes)
ONLINE_THRESHOLD_SECONDS = 5 * 60

# Initialize a persistent scoreboard
scoreboard = defaultdict(lambda: {"score": 0, "trees": 0})

# Load existing scores from the scoreboard file on startup
try:
    with open(SCOREBOARD_FILE, "r") as file:
        existing_data = json.load(file)
        for color in ["red", "green", "blue"]:
            scoreboard[color]["score"] = existing_data.get(color, {}).get("score", 0)
            scoreboard[color]["trees"] = 0  # Trees are recalculated live, so reset them
except (FileNotFoundError, json.JSONDecodeError):
    # If the file doesn't exist or is invalid, start with an empty scoreboard
    print("No valid scoreboard.json found. Starting fresh.")

# Track the previous state of each device
device_previous_states = {}

while True:
    # Get the current day and time
    now = datetime.now()

    # Check if today is a weekday (Monday to Friday) and the current time is between 8:00 AM and 4:30 PM
    if now.weekday() in range(0, 5) and now.time() >= datetime.strptime("08:00", "%H:%M").time() and now.time() <= datetime.strptime("22:30", "%H:%M").time():
        try:
            # Load device states from file
            with open(DEVICE_STATE_FILE, "r") as file:
                devices = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            devices = {}

        # Get the current epoch time
        current_epoch_time = int(time.time())

        # Iterate over each device and update the scoreboard
        for device, data in devices.items():
            state = data.get("state", "").upper()
            last_updated = data.get("last_updated")

            # Skip devices with invalid or missing last_updated
            if not last_updated:
                print(f"Skipping device {device} due to missing last_updated.")
                continue

            # Check if the device is online
            is_online = (current_epoch_time - last_updated) <= ONLINE_THRESHOLD_SECONDS

            # Handle devices that are online
            if is_online:
                if state in {"RED", "GREEN", "BLUE"}:
                    # Increment the score for the current state
                    scoreboard[state.lower()]["score"] += 1

                    # Handle state changes
                    previous_state = device_previous_states.get(device)
                    if previous_state != state:
                        # Update tree counts for state transitions
                        if previous_state and previous_state in {"RED", "GREEN", "BLUE"}:
                            scoreboard[previous_state.lower()]["trees"] -= 1
                        scoreboard[state.lower()]["trees"] += 1

                    # Update the device's previous state
                    device_previous_states[device] = state

                else:
                    # If the state is invalid (e.g., "NULL"), treat it as offline
                    # print(f"Device {device} has invalid state '{state}', treating as offline.")
                    previous_state = device_previous_states.get(device)
                    if previous_state and previous_state in {"RED", "GREEN", "BLUE"}:
                        scoreboard[previous_state.lower()]["trees"] -= 1
                    device_previous_states.pop(device, None)

            # Handle offline devices or devices with invalid states
            else:
                previous_state = device_previous_states.get(device)
                if previous_state and previous_state in {"RED", "GREEN", "BLUE"}:
                    scoreboard[previous_state.lower()]["trees"] -= 1
                device_previous_states.pop(device, None)

            # Delay before processing the next device and write the scoreboard after each device
            with open(SCOREBOARD_FILE, "w") as file:
                json.dump(scoreboard, file)
            time.sleep(0.4)

    # Wait before the next iteration of the main loop
    time.sleep(0.4)

