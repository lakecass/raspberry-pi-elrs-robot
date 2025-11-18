# Raspberry Pi ELRS Robot Controller

This project turns a Raspberry Pi into a controller for a simple robot using an ExpressLRS (ELRS) RC receiver and an L298N motor driver.

## Features

-   Receives RC signals via an ELRS receiver using the CRSF protocol.
-   Controls a 2-motor robot chassis with an L298N driver.
-   Configurable GPIO pins and RC channels.
-   Built-in failsafe to stop motors if the signal is lost.
-   Lightweight with minimal Python dependencies.

## Hardware Required

1.  **Raspberry Pi**: Any model with GPIO pins (e.g., 3B+, 4, Zero W).
2.  **ELRS Receiver**: Must support CRSF serial output.
3.  **L298N Motor Driver Module**.
4.  **DC Motors**: Two motors for a differential drive robot.
5.  **Robot Chassis**.
6.  **Separate Power Supply for Motors**: A battery pack (e.g., 7.4V - 12V LiPo or Li-Ion) is essential. **Do not power the motors from the Raspberry Pi's 5V pin.**
7.  **Jumper Wires**.

## Hardware Setup

### 1. ELRS Receiver to Raspberry Pi

Connect the receiver's CRSF output to the Pi's hardware serial pins.

| Receiver Pin | Raspberry Pi Pin | GPIO (BCM) |
| :----------- | :--------------- | :----------- |
| GND          | GND (Pin 6)      | -            |
| 5V           | 5V (Pin 2)       | -            |
| TX           | GPIO 15 (Pin 10) | RXD0         |

**Note**: The receiver's TX (Transmit) pin must connect to the Pi's RX (Receive) pin.

### 2. L298N Motor Driver

-   **Connect Motors**: Connect your left motor to `OUT1`/`OUT2` and your right motor to `OUT3`/`OUT4` on the L298N.
-   **Connect Motor Power**: Connect your separate battery pack to the `+12V` (or `VCC`) and `GND` terminals on the L298N.
-   **Connect L298N to Raspberry Pi**: Use the default pin configuration in `config.py` or modify it to your needs.

| L298N Pin | Raspberry Pi Pin | GPIO (BCM) | Purpose                  |
| :-------- | :--------------- | :----------- | :----------------------- |
| IN1       | GPIO 24 (Pin 18) | 24           | Left Motor Direction 1   |
| IN2       | GPIO 23 (Pin 16) | 23           | Left Motor Direction 2   |
| ENA       | GPIO 25 (Pin 22) | 25           | Left Motor Speed (PWM)   |
| IN3       | GPIO 22 (Pin 15) | 22           | Right Motor Direction 1  |
| IN4       | GPIO 27 (Pin 13) | 27           | Right Motor Direction 2  |
| ENB       | GPIO 17 (Pin 11) | 17           | Right Motor Speed (PWM)  |
| GND       | GND (e.g., Pin 9)| -            | **Critical: Common Ground** |

**IMPORTANT**: Ensure the `GND` of the L298N's motor power supply is connected to one of the Raspberry Pi's `GND` pins. This is required for the logic signals to work correctly.

## Software Setup

### 1. Configure Raspberry Pi Serial Port

You must enable the hardware serial port and disable the serial console.

1.  Open a terminal on your Pi.
2.  Run `sudo raspi-config`.
3.  Navigate to `3 Interface Options`.
4.  Select `I6 Serial Port`.
5.  Answer **NO** to "Would you like a login shell to be accessible over serial?".
6.  Answer **YES** to "Would you like the serial port hardware to be enabled?".
7.  Finish and reboot the Raspberry Pi.

### 2. Install Dependencies

Clone or download this project, navigate to the project directory, and install the required Python libraries.

```bash
cd raspberry-pi-elrs-robot
pip install -r requirements.txt
```

### 3. Configure the Controller

Open the `config.py` file to adjust settings:
-   Verify that the GPIO pin numbers match your wiring.
-   Check which channels your transmitter uses for throttle and steering (`THROTTLE_CHANNEL`, `STEERING_CHANNEL`). The indices are zero-based (Channel 1 = index 0).
-   If your robot moves in the wrong direction, you can flip `INVERT_THROTTLE` or `INVERT_STEERING` from `False` to `True`.

## Running the Robot

With all hardware connected and software installed, simply run the main script:

```bash
python main.py
```

The script will start, and if it receives a signal from your ELRS transmitter, your robot should now be controllable!

To stop the program, press `Ctrl+C`. The script will automatically stop the motors and clean up the GPIO resources.
