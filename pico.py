import time
import network
import urequests
from machine import Pin, Timer
from neopixel import NeoPixel

# Customizable variables below
# WiFi Credentials (List of SSID-password pairs)
WIFI_CREDENTIALS = [
    ("SSID_1", "PASSWORD_1"),
    ("SSID_2", "PASSWORD_2"),
    ("SSID_3", "PASSWORD_3"),
    ("SSID_4", "PASSWORD_4"),
]
# Device Name - Useful in logs
device_name = "NAME_OF_DEVICE1"
# API Key - Set to a random string of whatever
API_KEY = "A_RANDOM_STRING_OF_WHATEVER_PLEASE_CHANGE_ME"
# SERVER URL - UPDATE THIS AS NEEDED
API_URL = "http://192.168.1.10:5000/api/update_state"

# End of customizable variables. Edit below at your own peril

# LED Pin and Colors
GRBled = NeoPixel(Pin(2), 3)
red = (0, 255, 0)
green = (255, 0, 0)
blue = (0, 0, 255)
led_off = (0, 0, 0)

# Buttons
button1 = Pin(13, Pin.IN, Pin.PULL_DOWN)
button2 = Pin(8, Pin.IN, Pin.PULL_DOWN)
button3 = Pin(3, Pin.IN, Pin.PULL_DOWN)

# Variable to store the last button state
last_state = "NULL"

# Connect to WiFi
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    connected = False

    # Perform Wi-Fi scan to get a list of available networks
    available_networks = {network[0].decode(): network[3] for network in wlan.scan()}  # SSID and RSSI
    print(f"Available networks: {available_networks}")

    # Filter Wi-Fi credentials based on available networks
    filtered_credentials = sorted(
        [(ssid, password, available_networks[ssid]) for ssid, password in WIFI_CREDENTIALS if ssid in available_networks],
        key=lambda x: x[2],  # Sort by RSSI (signal strength)
        reverse=True         # Higher RSSI (stronger signal) first
    )

    if not filtered_credentials:
        print("No known networks available. Retrying in 5 seconds...")
        GRBled.fill(red)
        GRBled.write()
        time.sleep(5)
        GRBled.fill(led_off)
        GRBled.write()
        connect_to_wifi()  # Retry after a delay
        return

    # Attempt to connect to each filtered network
    for ssid, password, rssi in filtered_credentials:
        for attempt in range(2):  # Retry twice per SSID
            print(f"Attempt {attempt + 1} to connect to WiFi SSID: {ssid} (RSSI: {rssi})...")
            wlan.connect(ssid, password)
            timeout = 15  # Timeout for each attempt
            while not wlan.isconnected() and timeout > 0:
                time.sleep(1)
                timeout -= 1
            if wlan.isconnected():
                print(f"Connected to WiFi SSID: {ssid}!")
                GRBled.fill(green)
                GRBled.write()
                time.sleep(0.2)
                GRBled.fill(led_off)
                GRBled.write()
                time.sleep(0.2)
                GRBled.fill(green)
                GRBled.write()
                time.sleep(0.2)
                GRBled.fill(led_off)
                GRBled.write()
                time.sleep(0.2)
                GRBled.fill(green)
                GRBled.write()
                time.sleep(0.2)
                GRBled.fill(led_off)
                GRBled.write()
                time.sleep(0.2)
                connected = True
                break
            else:
                print(f"Connection attempt {attempt + 1} to SSID: {ssid} failed. Retrying...")
                time.sleep(2)  # Delay before retrying the same SSID
        if connected:
            break

    if not connected:
        print("Failed to connect to any available WiFi. Retrying in 5 seconds...")
        time.sleep(5)
        connect_to_wifi()  # Retry the entire process

    # Print network configuration once connected
    print("Network Config:", wlan.ifconfig())
    # Send initial update to API
    send_update(device_name, "NULL")

# Send Update to API
def send_update(device_id, state):
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": API_KEY  # Adding the API key in the headers
    }
    try:
        response = urequests.post(API_URL, json={"device_id": device_id, "state": state}, headers=headers)
        print(f"Response: {response.status_code}, {response.text}")
        response.close()
    except Exception as e:
        print(f"Failed to send update: {e}")

# Send heartbeat to API
def send_heartbeat(device_id):
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": API_KEY  # Adding the API key in the headers
    }
    try:
        response = urequests.post(API_URL, json={"device_id": device_id, "heartbeat": "alive"}, headers=headers)
        print(f"Response: {response.status_code}, {response.text}")
        response.close()
    except Exception as e:
        print(f"Failed to send update: {e}")

# Timer callback for periodic updates
def periodic_update(timer):
    global last_state
    send_heartbeat(device_name)

# Main
print("Starting main.py...")
time.sleep(1)  # Allow time for initialization
connect_to_wifi()

# Set up a timer to call periodic_update every 2 minutes (120000 ms)
update_timer = Timer(-1)
update_timer.init(period=120000, mode=Timer.PERIODIC, callback=periodic_update)

# Main loop
while True:
    time.sleep(0.2)

    if button1.value() == 1:  # Button 1 pressed
        print("Button 1 pressed")
        GRBled.fill((blue))
        GRBled.write()
        last_state = "BLUE"
        send_update(device_name, "BLUE")

    if button3.value() == 1:  # Button 3 pressed
        print("Button 2 pressed")
        GRBled.fill((red))
        GRBled.write()
        last_state = "RED"
        send_update(device_name, "RED")

    if button2.value() == 1:  # Button 2 pressed
        print("Button 3 pressed")
        GRBled.fill((green))
        GRBled.write()
        last_state = "GREEN"
        send_update(device_name, "GREEN")



