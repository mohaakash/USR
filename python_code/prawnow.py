import cv2
import time
import serial
from ultralytics import YOLO

from supporting.camera_output import capture_one_frame

# Step 2: Initialize stacks and YOLO model
stackx = []
stacky = []
model = YOLO('june8.pt') 
esp = serial.Serial('COM10', 9600, timeout=1)  # Replace 'COM_PORT' with the actual ESP8266 port

def process_image_with_yolo(image):
    results = model(frame)[0]
    coordinates = []
    for obj in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = obj

        x=int((x1+x2)//2)
        y=int((y1+y2)//2)
        x3, y3 = x,y  # Replace 'x' and 'y' with actual result keys
        coordinates.append((x3, y3))
    return coordinates

while True:
    # Step 3: Check if stacks are empty
    if not stackx and not stacky:
        frame = capture_one_frame()
        coordinates = process_image_with_yolo(frame)
        for x, y in coordinates:
            stackx.append(x)
            stacky.append(y)

    else:
        # Step 5: Pop from stacks and send to ESP8266
        x = stackx.pop()
        y = stacky.pop()
        message = f"{x},{y}\n"
        esp.write(message.encode())
        print(f"Sent coordinates: {message.strip()}")

    # Step 6: Pause for 5 seconds to simulate a delay
    time.sleep(1)
