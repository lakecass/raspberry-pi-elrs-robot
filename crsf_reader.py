# crsf_reader.py
import serial
import time
from config import SERIAL_PORT

# CRSF Protocol constants
CRSF_SYNC_BYTE = 0xC8
CRSF_FRAME_RC_CHANNELS_PAYLOAD = 0x16
CRSF_PAYLOAD_SIZE = 22  # 16 channels * 11 bits = 176 bits = 22 bytes

# Precomputed CRC8 lookup table for DVB-S2
CRC8_DVB_S2_TABLE = [
    0x00, 0xD5, 0x7F, 0xAA, 0xFF, 0x2A, 0x80, 0x55, 0x3F, 0xEA, 0x40, 0x95, 0xC5, 0x10, 0xBA, 0x6F,
    0x1F, 0xCA, 0x60, 0xB5, 0xE5, 0x30, 0x9A, 0x4F, 0x25, 0xF0, 0x5A, 0x8F, 0xDF, 0x0A, 0xA0, 0x75,
    0xAF, 0x7A, 0xD0, 0x05, 0x55, 0x80, 0x2A, 0xFF, 0x95, 0x40, 0xEA, 0x3F, 0x6F, 0xBA, 0x10, 0xC5,
    0xB5, 0x60, 0xCA, 0x1F, 0x4F, 0x9A, 0x30, 0xE5, 0x8F, 0x5A, 0xF0, 0x25, 0x75, 0xA0, 0x0A, 0xDF,
    0x5F, 0x8A, 0x20, 0xF5, 0xA5, 0x70, 0xDA, 0x0F, 0x65, 0xB0, 0x1A, 0xCF, 0x9F, 0x4A, 0xE0, 0x35,
    0x45, 0x90, 0x3A, 0xEF, 0xBF, 0x6A, 0xC0, 0x15, 0x7F, 0xAA, 0x00, 0xD5, 0x85, 0x50, 0xFA, 0x2F,
    0xE5, 0x30, 0x9A, 0x4F, 0x1F, 0xCA, 0x60, 0xB5, 0xD5, 0x00, 0xAA, 0x7F, 0x2F, 0xFA, 0x50, 0x85,
    0xF5, 0x20, 0x8A, 0x5F, 0x0F, 0xDA, 0x70, 0xA5, _CF, 0x1A, 0xB0, 0x65, 0x35, 0xE0, 0x4A, 0x9F,
    0xBF, 0x6A, 0xC0, 0x15, 0x45, 0x90, 0x3A, 0xEF, 0x85, 0x50, 0xFA, 0x2F, 0x7F, 0xAA, 0x00, 0xD5,
    0xA5, 0x70, 0xDA, 0x0F, 0x5F, 0x8A, 0x20, 0xF5, 0x9F, 0x4A, 0xE0, 0x35, 0x65, 0xB0, 0x1A, 0xCF,
    0x0F, 0xDA, 0x70, 0xA5, 0xF5, 0x20, 0x8A, 0x5F, 0x35, 0xE0, 0x4A, 0x9F, 0xCF, 0x1A, 0xB0, 0x65,
    0x15, 0xC0, 0x6A, 0xBF, 0xEF, 0x3A, 0x90, 0x45, 0x2F, 0xFA, 0x50, 0x85, 0xD5, 0x00, 0xAA, 0x7F,
    0x9F, 0x4A, 0xE0, 0x35, 0x65, 0xB0, 0x1A, 0xCF, 0xAF, 0x7A, 0xD0, 0x05, 0x55, 0x80, 0x2A, 0xFF,
    0xCF, 0x1A, 0xB0, 0x65, 0x35, 0xE0, 0x4A, 0x9F, 0xFF, 0x2A, 0x80, 0x55, 0x05, 0xD0, 0x7A, 0xAF,
    0x65, 0xB0, 0x1A, 0xCF, 0x9F, 0x4A, 0xE0, 0x35, 0x5F, 0x8A, 0x20, 0xF5, 0xA5, 0x70, 0xDA, 0x0F,
    0x75, 0xA0, 0x0A, 0xDF, 0x8F, 0x5A, 0xF0, 0x25, 0x4F, 0x9A, 0x30, 0xE5, 0xB5, 0x60, 0xCA, 0x1F,
]

def crc8_dvb_s2(data):
    crc = 0
    for byte in data:
        crc = CRC8_DVB_S2_TABLE[crc ^ byte]
    return crc

class CRSFReader:
    def __init__(self, port=SERIAL_PORT):
        self.port = port
        self.ser = serial.Serial(
            port=self.port,
            baudrate=420000,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0.05
        )
        self.channels = [0] * 16
        self.is_connected = True

    def _parse_channels(self, payload):
        """Unpacks the 11-bit channel data from the 22-byte payload."""
        # This is a bitwise operation to extract 16 channels, 11 bits each
        ch0 = (payload[0] | payload[1] << 8) & 0x07FF
        ch1 = (payload[1] >> 3 | payload[2] << 5) & 0x07FF
        ch2 = (payload[2] >> 6 | payload[3] << 2 | payload[4] << 10) & 0x07FF
        ch3 = (payload[4] >> 1 | payload[5] << 7) & 0x07FF
        ch4 = (payload[5] >> 4 | payload[6] << 4) & 0x07FF
        ch5 = (payload[6] >> 7 | payload[7] << 1 | payload[8] << 9) & 0x07FF
        ch6 = (payload[8] >> 2 | payload[9] << 6) & 0x07FF
        ch7 = (payload[9] >> 5 | payload[10] << 3) & 0x07FF
        ch8 = (payload[11] | payload[12] << 8) & 0x07FF
        ch9 = (payload[12] >> 3 | payload[13] << 5) & 0x07FF
        ch10 = (payload[13] >> 6 | payload[14] << 2 | payload[15] << 10) & 0x07FF
        ch11 = (payload[15] >> 1 | payload[16] << 7) & 0x07FF
        ch12 = (payload[16] >> 4 | payload[17] << 4) & 0x07FF
        ch13 = (payload[17] >> 7 | payload[18] << 1 | payload[19] << 9) & 0x07FF
        ch14 = (payload[19] >> 2 | payload[20] << 6) & 0x07FF
        ch15 = (payload[20] >> 5 | payload[21] << 3) & 0x07FF

        self.channels = [ch0, ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8, ch9, ch10, ch11, ch12, ch13, ch14, ch15]
        return True

    def read(self):
        """Reads and processes one CRSF frame."""
        # Find sync byte
        byte = self.ser.read(1)
        if not byte or ord(byte) != CRSF_SYNC_BYTE:
            return False

        # Read the rest of the header
        header = self.ser.read(2)
        if len(header) < 2:
            return False
        
        length = header[0]
        frame_type = header[1]
        
        # Check if it's a channels frame
        if frame_type == CRSF_FRAME_RC_CHANNELS_PAYLOAD:
            if length != CRSF_PAYLOAD_SIZE + 2: # payload + type + crc
                 return False

            frame_data = bytes([frame_type]) + self.ser.read(length-1)
            if len(frame_data) < length-1:
                return False

            payload = frame_data[1:-1] #
            crc_received = frame_data[-1]
            
            crc_calculated = crc8_dvb_s2(frame_data[:-1])

            if crc_calculated == crc_received:
                 return self._parse_channels(payload)
        else:
            # Skip other frame types
            self.ser.read(length - 1)
        
        return False

    def get_channels(self):
        """Returns the last known channel values."""
        return self.channels

    def close(self):
        self.ser.close()

if __name__ == '__main__':
    # Example Usage:
    print("Starting CRSF Reader Test. Make sure your receiver is connected.")
    try:
        reader = CRSFReader()
        start_time = time.time()
        packet_count = 0
        while True:
            if reader.read():
                packet_count += 1
                channels = reader.get_channels()
                # Print channels in a readable format
                print(f"Channels: {', '.join(f'{ch:4d}' for ch in channels)}", end='\r')
            
            # Calculate and print packet rate
            if time.time() - start_time > 1:
                print(f"\nPacket Rate: {packet_count} Hz")
                packet_count = 0
                start_time = time.time()
                
    except serial.SerialException as e:
        print(f"Serial Error: {e}. Is the receiver connected to {SERIAL_PORT}?")
    except KeyboardInterrupt:
        print("\nStopping test.")
    finally:
        if 'reader' in locals():
            reader.close()
