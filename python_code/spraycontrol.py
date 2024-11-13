import sys
import cv2
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QStatusBar
)
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import Qt, QTimer
from ultralytics import YOLO

from supporting.camera_output import capture_one_frame

class YOLOv8LiveGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set main window properties
        self.setWindowTitle("Robot control Software")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("background-color: #F0F8FF;")  # Light blue background

        # Status bar to show current operations
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # Create main layout
        main_layout = QVBoxLayout()

        # Label to display webcam feed
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setText("Click Start to begin webcam feed")
        self.video_label.setFont(QFont('Arial', 18))
        self.video_label.setStyleSheet("border: 3px solid #6495ED; background-color: #FFFFFF;")
        main_layout.addWidget(self.video_label)

        # Create a horizontal layout for buttons
        button_layout = QHBoxLayout()

        # Button to start webcam feed for crops
        self.start_button = QPushButton("Start Spraying Crops")
        self.start_button.setFont(QFont('Arial', 14))
        self.start_button.setStyleSheet("background-color: #32CD32; color: white; padding: 10px;")
        self.start_button.clicked.connect(self.start_webcam)
        button_layout.addWidget(self.start_button)
        # Button to start webcam feed for weeds
        self.start_button = QPushButton("Start Spraying Weeds")
        self.start_button.setFont(QFont('Arial', 14))
        self.start_button.setStyleSheet("background-color: #32CD32; color: white; padding: 10px;")
        self.start_button.clicked.connect(self.start_webcam)
        button_layout.addWidget(self.start_button)

        # Button to stop webcam feed
        self.stop_button = QPushButton("Stop Spraying")
        self.stop_button.setFont(QFont('Arial', 14))
        self.stop_button.setStyleSheet("background-color: #FF4500; color: white; padding: 10px;")
        self.stop_button.clicked.connect(self.stop_webcam)
        self.stop_button.setEnabled(False)  # Disabled until webcam is started
        button_layout.addWidget(self.stop_button)

        main_layout.addLayout(button_layout)

        # Set the central widget and layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Initialize variables for webcam and timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.cap = None

    def start_webcam(self):
        # Open webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.statusBar.showMessage("Error: Could not open webcam", 5000)
            return

        self.timer.start(20)  # Update every 20ms (50 FPS)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.statusBar.showMessage("Webcam started", 3000)

    def stop_webcam(self):
        # Stop the timer and release the webcam
        self.timer.stop()
        if self.cap:
            self.cap.release()
        self.video_label.setText("Webcam stopped")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.statusBar.showMessage("Webcam stopped", 3000)

    def update_frame(self):
        
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

        annotated_frame = results[0].plot()

        # Convert the annotated frame to QImage for display in QLabel
        height, width, channel = annotated_frame.shape
        bytes_per_line = 3 * width
        q_img = QImage(annotated_frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap(q_img)
        scaled_pixmap = pixmap.scaled(800, 800)



        # Display the image in the video label
        self.video_label.setPixmap(scaled_pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YOLOv8LiveGUI()
    window.show()
    sys.exit(app.exec_())
