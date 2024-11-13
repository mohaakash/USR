import tkinter as tk
from tkinter import ttk
import serial
import time

# Configure the serial connection
serial_port = 'COM9'  # Replace with your COM port
baud_rate = 115200    # Match the baud rate set in the Arduino code

# Establish serial communication
try:
    ser = serial.Serial(serial_port, baud_rate)
    time.sleep(2)  # Wait for the connection to initialize
except serial.SerialException:
    print(f"Failed to connect to {serial_port}. Make sure the ESP8266 is connected.")
    ser = None

def send_servo_angles(angle1, angle2):
    """
    Sends the servo angles to the ESP8266.
    :param angle1: Angle for servo 1 (0-180 degrees)
    :param angle2: Angle for servo 2 (0-180 degrees)
    """
    if ser and ser.is_open:
        # Create the command string in the format "angle1,angle2\n"
        command = f"{angle1},{angle2}\n"
        ser.write(command.encode())  # Send the command over the serial connection
        print(f"Sent: {command.strip()}")

def on_servo1_change(val):
    """
    Callback function for servo 1 slider change.
    """
    angle1 = int(servo1_slider.get())
    angle2 = int(servo2_slider.get())
    send_servo_angles(angle1, angle2)

def on_servo2_change(val):
    """
    Callback function for servo 2 slider change.
    """
    angle1 = int(servo1_slider.get())
    angle2 = int(servo2_slider.get())
    send_servo_angles(angle1, angle2)

# Create the main application window
root = tk.Tk()
root.title("Servo Control")

# Configure the grid layout
root.columnconfigure(0, weight=1)
root.rowconfigure([0, 1], weight=1)

# Create a label and slider for Servo 1
servo1_label = ttk.Label(root, text="Servo 1 Angle")
servo1_label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

servo1_slider = ttk.Scale(root, from_=0, to=180, orient="horizontal", command=on_servo1_change)
servo1_slider.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

# Create a label and slider for Servo 2
servo2_label = ttk.Label(root, text="Servo 2 Angle")
servo2_label.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

servo2_slider = ttk.Scale(root, from_=0, to=180, orient="horizontal", command=on_servo2_change)
servo2_slider.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

# Set initial positions of sliders to 90 degrees (middle)
servo1_slider.set(90)
servo2_slider.set(90)

# Start the main loop
try:
    root.mainloop()
finally:
    if ser and ser.is_open:
        ser.close()  # Close the serial connection when the program ends
