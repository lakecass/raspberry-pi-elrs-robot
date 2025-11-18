# main.py
import time
from crsf_reader import CRSFReader
from motor_controller import MotorController
from config import *

def map_channel_value(value, min_in=172, max_in=1811, min_out=-100, max_out=100):
    """Maps a CRSF channel value (172-1811) to an output range (-100 to 100)."""
    # Clamp the value to the input range
    value = max(min(value, max_in), min_in)
    # Perform the linear mapping
    return (value - min_in) * (max_out - min_out) / (max_in - min_in) + min_out

def main():
    print("Starting ELRS Robot Controller...")
    
    try:
        reader = CRSFReader(SERIAL_PORT)
        motors = MotorController()
        
        print("Controller initialized. Waiting for signal...")

        last_packet_time = time.time()

        while True:
            if reader.read():
                last_packet_time = time.time()
                channels = reader.get_channels()
                
                # Extract throttle and steering values
                throttle_raw = channels[THROTTLE_CHANNEL]
                steering_raw = channels[STEERING_CHANNEL]
                
                # Map raw values to -100 to 100 range
                throttle = map_channel_value(throttle_raw)
                steering = map_channel_value(steering_raw)

                # Apply deadzone
                if abs(throttle) < DEADZONE:
                    throttle = 0
                if abs(steering) < DEADZONE:
                    steering = 0
                
                # Control the motors
                motors.move(throttle, steering)

                # Optional: Print status for debugging
                # print(f"Throttle: {throttle: 3.0f}, Steering: {steering: 3.0f}", end='\r')

            # Failsafe: if no packet is received for 0.5 seconds, stop the motors
            if time.time() - last_packet_time > 0.5:
                print("\nFailsafe triggered: No signal from receiver. Stopping motors.")
                motors.stop()
                # You might want to try to reconnect or simply wait
                time.sleep(0.1)


    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        print("\nCleaning up and shutting down.")
        if 'motors' in locals():
            motors.cleanup()
        if 'reader' in locals():
            reader.close()

if __name__ == '__main__':
    main()
