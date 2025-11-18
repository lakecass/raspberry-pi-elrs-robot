# config.py

# GPIO Pin definitions using BCM numbering
MOTOR_LEFT_IN1 = 24
MOTOR_LEFT_IN2 = 23
MOTOR_LEFT_ENA = 25

MOTOR_RIGHT_IN3 = 22
MOTOR_RIGHT_IN4 = 27
MOTOR_RIGHT_ENB = 17

# Serial port for ELRS Receiver
SERIAL_PORT = '/dev/ttyS0'  # For Raspberry Pi 3/4/Zero W with console disabled
#SERIAL_PORT = '/dev/ttyAMA0' # For older Raspberry Pi models

# CRSF RC Channel mapping
# Adjust these values based on your transmitter's channel configuration
THROTTLE_CHANNEL = 2  # Typically Channel 3 (index 2)
STEERING_CHANNEL = 0  # Typically Channel 1 (index 0)

# Deadzone for joystick to prevent movement when centered
DEADZONE = 50

# Invert steering or throttle if necessary
INVERT_STEERING = False
INVERT_THROTTLE = False
