import os
import sys
import cv2
from ultralytics import YOLO

sys.path.append(os.path.abspath(".."))

from supporting.camera_output import capture_one_frame

#model_path = os.path.join('.', 'runs', 'detect', 'train', 'weights', 'last.pt')
model = YOLO('june8.pt') 

threshold = 0
stackx = []
stacky = []

# Load an image
frame = capture_one_frame()

# Predict the image
results = model(frame)[0]
print("Is the stacks empty?", len(stackx) == 0 and len(stacky) == 0 )  # Output: True

for result in results.boxes.data.tolist():
    x1, y1, x2, y2, score, class_id = result
    detection_color= (0, 255, 0) if int(class_id)==0 else (0, 0, 255)
    if score > threshold:
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), detection_color, 4)
        cv2.putText(frame, results.names[int(class_id)].upper(), (int(x1), int(y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.3, detection_color, 3, cv2.LINE_AA)
        print('cordinates',x1,y1,x2,y2)

        #calculating the scaling constant
        x=int((x1+x2)//2)
        y=int((y1+y2)//2)
        # Push elements to the stack
        stackx.append(x)
        stacky.append(y)

# Display the image with predictions
# Print the entire stack
print("Stack contents X:", stackx)
print("Stack contents y:", stacky)

cv2.imshow('YOLOv8 Predictions', frame)
cv2.waitKey(0)
cv2.destroyAllWindows()
