import serial
import keyboard

# Replace 'COM3' with the actual COM port your Arduino is connected to
ser = serial.Serial('COM5', 9600)

while True:
    # Check if the 'R' key is pressed
    if keyboard.is_pressed('a'):
        print("Turning relay ON")
        ser.write(b'1')  # Send '1' to Arduino to turn on the relay
    # Check if the 'S' key is pressed
    elif keyboard.is_pressed('b'):
        print("Turning relay OFF")
        ser.write(b'0')  # Send '0' to Arduino to turn off the relay
