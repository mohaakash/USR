import os

from ultralytics import YOLO
import cv2
import serial,time


cap = cv2.VideoCapture(0)
ret, frame = cap.read()
H, W, _ = frame.shape

#serial connection
ArduinoSerial=serial.Serial('COM7',9600,timeout=0.1)
time.sleep(1)

# Load a model
model = YOLO('last.pt')  # load a custom model

threshold = 0

while ret:

    results = model(frame)[0]

    for result in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = result
        detection_color= (0, 255, 0) if int(class_id)==0 else (0, 0, 255)
        if score > threshold:
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), detection_color, 4)
            cv2.putText(frame, results.names[int(class_id)].upper(), (int(x1), int(y1 - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.3, detection_color, 3, cv2.LINE_AA)
            print('cordinates',x1,y1,x2,y2)

            #calculating the scaling constant
            x=int(x1+x2//2)
            y=int(y1+y2//2)
            #sending coordinates to Arduino
            string='X{0:d}Y{1:d}'.format(x,y)
            print(string)
            ArduinoSerial.write(string.encode('utf-8'))
            # Display the frame
            
    cv2.imshow('YOLOv8 prediction', frame)
    # Press 'q' to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    ret, frame = cap.read()
    

cap.release()
cv2.destroyAllWindows()
