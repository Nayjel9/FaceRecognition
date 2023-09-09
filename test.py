import serial
import time

# Replace with the actual serial port name
arduino_port = '/dev/ttyACM0'  # Example: '/dev/ttyUSB0'
baud_rate = 9600

try:
    ser = serial.Serial(arduino_port, baud_rate, timeout=1)
    print("Connected to Arduino on port:", arduino_port)

    while True:
        command = input("Enter '1' to turn ON the relay, '0' to turn OFF, or 'q' to quit: ").strip()
        
        if command == 'q':
            break
        elif command in ('0', '1'):
            ser.write(command.encode())  # Send the command to Arduino
            response = ser.readline().decode('utf-8').strip()
            print("Arduino response:", response)
        else:
            print("Invalid command. Enter '0', '1', or 'q'.")
        
except serial.SerialException as e:
    print("Error:", e)

finally:
    if 'ser' in locals():
        ser.close()
