#!/usr/bin/env python3
########################################################################
# Filename    : Controller.py
# Description : Nicholas Jean - Unified Button + Joystick Input
# modification: 2026/02/04
########################################################################

from gpiozero import Button
from signal import pause
import time
from ADCDevice import *
import threading

# ----------------------------
# GPIO PINS (BCM)
# ----------------------------
BUTTON1_PIN = 17
BUTTON2_PIN = 27
JOYSTICK_Z_PIN = 18

# ----------------------------
# Joystick tuning
# ----------------------------
POLL_RATE_HZ = 50
DEADZONE = 80          # ignore tiny movements
CHANGE_THRESHOLD = 20   # minimum delta to update input state

# ----------------------------
# Input state dictionary (import this in your game)
# ----------------------------
input_state = {
    "x": 128,      # Joystick X (0-255)
    "y": 128,      # Joystick Y (0-255)
    "shoot": False, # Button 1
    "special": False, # Button 2
    "click": False  # Joystick Z
}

# ----------------------------
# Button setup
# ----------------------------
button1 = Button(BUTTON1_PIN, pull_up=True, bounce_time=0.05)
button2 = Button(BUTTON2_PIN, pull_up=True, bounce_time=0.05)
joystick_z = Button(JOYSTICK_Z_PIN, pull_up=True, bounce_time=0.05)

# Update input_state on events
button1.when_pressed = lambda: input_state.update({"shoot": True})
button1.when_released = lambda: input_state.update({"shoot": False})

button2.when_pressed = lambda: input_state.update({"special": True})
button2.when_released = lambda: input_state.update({"special": False})

joystick_z.when_pressed = lambda: input_state.update({"click": True})
joystick_z.when_released = lambda: input_state.update({"click": False})

# ----------------------------
# ADC setup
# ----------------------------
adc = ADCDevice()

def setup_adc():
    global adc
    if adc.detectI2C(0x48):
        adc = PCF8591()
    elif adc.detectI2C(0x4b):
        adc = ADS7830()
    else:
        print("No ADC found. Check I2C wiring.")
        exit(1)

# ----------------------------
# Joystick polling (thread-safe)
# ----------------------------
def joystick_poll():
    last_x = 128
    last_y = 128
    while True:
        x = adc.analogRead(1)
        y = adc.analogRead(0)

        # Deadzone
        if abs(x - 128) < DEADZONE:
            x = 128
        if abs(y - 128) < DEADZONE:
            y = 128

        # Only update if movement is significant
        if abs(x - last_x) > CHANGE_THRESHOLD or abs(y - last_y) > CHANGE_THRESHOLD:
            input_state["x"] = x
            input_state["y"] = y
            last_x = x
            last_y = y

        time.sleep(1 / POLL_RATE_HZ)

# ----------------------------
# Start joystick thread
# ----------------------------
def start_input_thread():
    setup_adc()
    t = threading.Thread(target=joystick_poll, daemon=True)
    t.start()
    # gpiozero buttons work in background automatically

# ----------------------------
# Run standalone (for testing)
# ----------------------------
if __name__ == "__main__":
    print("Controller started. Updating input_state.")
    start_input_thread()
    try:
        while True:
            # Print input_state for debug
            print(input_state)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nExiting...")
        adc.close()
