# Word Runner 🎮

A Raspberry Pi-powered arcade word game built with Pygame and a custom GPIO controller. Dodge incoming letters, shoot them to build words, and cash them in for points!

---

## Overview

Word Runner is a physical arcade game where players control a character on screen using a joystick and buttons wired directly to a Raspberry Pi's GPIO pins. Letters fly across the screen — shoot them to collect characters, form valid words, and submit them for points. Colliding with a letter ends the game.

---

## Hardware Requirements

- Raspberry Pi (any model with GPIO and I2C support)
- Analog joystick module with I2C ADC (PCF8591 or ADS7830)
- 2 push buttons
- Jumper wires and breadboard
- Display connected to the Pi (HDMI or DSI)

### GPIO Pin Mapping

| Component      | BCM Pin |
|----------------|---------|
| Button 1 (Shoot) | GPIO 17 |
| Button 2 (Cash Word) | GPIO 27 |
| Joystick Click (Z) | GPIO 18 |
| Joystick X/Y   | I2C ADC (channels 1 and 0) |

The joystick's analog axes are read via I2C. The code auto-detects either a **PCF8591** (address `0x48`) or **ADS7830** (address `0x4b`) ADC module.

---

## Software Requirements

- Python 3
- Pygame
- gpiozero
- ADCDevice library (for I2C joystick reading)
- A system dictionary at `/usr/share/dict/words` (standard on most Linux distros)

Install dependencies:

```bash
pip install pygame gpiozero
```

Make sure I2C is enabled on your Pi:

```bash
sudo raspi-config  # Interface Options → I2C → Enable
```

---

## Project Structure

```
WordRunner/
├── WordRunner.py     # Main game loop and rendering
├── Controller.py     # GPIO input handler (joystick + buttons)
└── ADCDevice.py      # ADC library for analog joystick reading
```

---

## How to Run

```bash
python3 WordRunner.py
```

> Run from a desktop environment or with a display connected. Pygame requires a graphical output.

---

## How to Play

### Controls

| Action        | Input         |
|---------------|---------------|
| Move           | Joystick      |
| Shoot          | Button 1      |
| Submit Word    | Button 2      |

### Gameplay

- Letters fly across the screen from right to left.
- **Shoot** a letter to collect it into your Word Bank.
- **Avoid** letters — touching one is an instant Game Over.
- Once you've collected enough letters, press **Button 2** to submit your word.
- Only valid dictionary words of 2+ letters will score points.

### Letter Types & Point Values

| Type        | Color  | Points |
|-------------|--------|--------|
| Vowel       | Blue   | 1 pt   |
| Consonant   | White  | 2 pts  |
| Rare Letter | Orange | 4 pts  |

### Word Length Multipliers

| Word Length | Multiplier |
|-------------|------------|
| 2–4 letters | 1×         |
| 5–6 letters | 2×         |
| 7–8 letters | 3×         |
| 9+ letters  | 4×         |

---

## Controller Module

`Controller.py` can be run standalone for hardware testing:

```bash
python3 Controller.py
```

This prints the live `input_state` dictionary to the terminal so you can verify joystick movement and button presses before launching the game.

### Input State Dictionary

```python
input_state = {
    "x": 128,       # Joystick X axis (0–255, 128 = center)
    "y": 128,       # Joystick Y axis (0–255, 128 = center)
    "shoot": False, # Button 1
    "special": False, # Button 2
    "click": False  # Joystick Z (click)
}
```

A deadzone of ±80 and a change threshold of 20 are applied to reduce joystick noise.

---

## Credits

Developed by **Nicholas Jean** — February 2026.
