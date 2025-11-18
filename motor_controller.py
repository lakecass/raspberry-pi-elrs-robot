# motor_controller.py
import RPi.GPIO as GPIO
import time
from config import *

class MotorController:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Setup Left Motor
        GPIO.setup(MOTOR_LEFT_IN1, GPIO.OUT)
        GPIO.setup(MOTOR_LEFT_IN2, GPIO.OUT)
        GPIO.setup(MOTOR_LEFT_ENA, GPIO.OUT)
        self.pwm_left = GPIO.PWM(MOTOR_LEFT_ENA, 1000)
        self.pwm_left.start(0)

        # Setup Right Motor
        GPIO.setup(MOTOR_RIGHT_IN3, GPIO.OUT)
        GPIO.setup(MOTOR_RIGHT_IN4, GPIO.OUT)
        GPIO.setup(MOTOR_RIGHT_ENB, GPIO.OUT)
        self.pwm_right = GPIO.PWM(MOTOR_RIGHT_ENB, 1000)
        self.pwm_right.start(0)

    def stop(self):
        """Stops both motors."""
        self.pwm_left.ChangeDutyCycle(0)
        self.pwm_right.ChangeDutyCycle(0)

    def move(self, speed, direction):
        """
        Controls the robot's movement.
        - speed: -100 to 100. Negative for backward, positive for forward.
        - direction: -100 to 100. Negative for left, positive for right.
        """
        
        # Invert if configured
        if INVERT_THROTTLE:
            speed = -speed
        if INVERT_STEERING:
            direction = -direction

        # Calculate motor speeds
        left_speed = speed
        right_speed = speed

        if direction > 0: # Turn Right
            left_speed = speed
            right_speed = speed * (1 - (direction / 100.0))
        elif direction < 0: # Turn Left
            right_speed = speed
            left_speed = speed * (1 - (abs(direction) / 100.0))

        # Clamp speeds to -100, 100
        left_speed = max(min(left_speed, 100), -100)
        right_speed = max(min(right_speed, 100), -100)
        
        self._set_motor_speed('left', left_speed)
        self._set_motor_speed('right', right_speed)

    def _set_motor_speed(self, motor, speed):
        """Sets the speed and direction for a single motor."""
        pwm = self.pwm_left if motor == 'left' else self.pwm_right
        in1 = MOTOR_LEFT_IN1 if motor == 'left' else MOTOR_RIGHT_IN3
        in2 = MOTOR_LEFT_IN2 if motor == 'left' else MOTOR_RIGHT_IN4
        
        if speed > 0:
            GPIO.output(in1, GPIO.HIGH)
            GPIO.output(in2, GPIO.LOW)
            pwm.ChangeDutyCycle(speed)
        elif speed < 0:
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.HIGH)
            pwm.ChangeDutyCycle(abs(speed))
        else:
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.LOW)
            pwm.ChangeDutyCycle(0)

    def cleanup(self):
        """Cleans up GPIO resources."""
        self.stop()
        GPIO.cleanup()

if __name__ == '__main__':
    # Example Usage:
    print("Motor Controller Test")
    controller = MotorController()
    try:
        print("Moving forward")
        controller.move(50, 0)
        time.sleep(2)

        print("Turning left")
        controller.move(50, -50)
        time.sleep(2)
        
        print("Turning right")
        controller.move(50, 50)
        time.sleep(2)

        print("Moving backward")
        controller.move(-50, 0)
        time.sleep(2)

        print("Stopping")
        controller.stop()

    except KeyboardInterrupt:
        print("Test stopped by user.")
    finally:
        controller.cleanup()
