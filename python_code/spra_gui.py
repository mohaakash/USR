import sys
import cv2
import time
import serial
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QSlider, QWidget, QHBoxLayout
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from ultralytics import YOLO

from supporting.camera_output import capture_one_frame

# Step 2: Initialize stacks and YOLO model
stackx = []
stacky = []
model = YOLO('june8.pt')
esp = serial.Serial('COM11', 9600, timeout=1)  # Replace 'COM_PORT' with the actual ESP8266 port


def process_image_with_yolo(image):
    results = model(image)[0]
    coordinates = []
    for obj in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = obj
        x = int((x1 + x2) // 2)
        y = int((y1 + y2) // 2)
        coordinates.append((x, y))
    return coordinates


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YOLO Object Tracker with GUI")
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Video display
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.video_label)

        # Stack counter
        self.stack_label = QLabel("Stack Length: 0", self)
        self.layout.addWidget(self.stack_label)

        # Sliders
        slider_layout = QHBoxLayout()
        self.zoom_slider = QSlider(Qt.Horizontal, self)
        self.zoom_slider.setRange(1, 5)
        self.zoom_slider.setValue(1)
        self.zoom_slider.setTickInterval(1)
        self.zoom_slider.setTickPosition(QSlider.TicksBelow)
        self.zoom_slider_label = QLabel("Zoom: 1x", self)

        self.brightness_slider = QSlider(Qt.Horizontal, self)
        self.brightness_slider.setRange(0, 100)
        self.brightness_slider.setValue(50)
        self.brightness_slider_label = QLabel("Brightness: 50", self)

        self.saturation_slider = QSlider(Qt.Horizontal, self)
        self.saturation_slider.setRange(0, 100)
        self.saturation_slider.setValue(50)
        self.saturation_slider_label = QLabel("Saturation: 50", self)

        slider_layout.addWidget(self.zoom_slider_label)
        slider_layout.addWidget(self.zoom_slider)
        slider_layout.addWidget(self.brightness_slider_label)
        slider_layout.addWidget(self.brightness_slider)
        slider_layout.addWidget(self.saturation_slider_label)
        slider_layout.addWidget(self.saturation_slider)
        self.layout.addLayout(slider_layout)

        # Timer for GUI updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(100)

        # Signals for sliders
        self.zoom_slider.valueChanged.connect(self.update_zoom_label)
        self.brightness_slider.valueChanged.connect(self.update_brightness_label)
        self.saturation_slider.valueChanged.connect(self.update_saturation_label)

    def update_zoom_label(self):
        zoom_value = self.zoom_slider.value()
        self.zoom_slider_label.setText(f"Zoom: {zoom_value}x")

    def update_brightness_label(self):
        brightness_value = self.brightness_slider.value()
        self.brightness_slider_label.setText(f"Brightness: {brightness_value}")

    def update_saturation_label(self):
        saturation_value = self.saturation_slider.value()
        self.saturation_slider_label.setText(f"Saturation: {saturation_value}")

    def update_frame(self):
        global stackx, stacky

        # Capture a frame
        frame = capture_one_frame()
        if frame is None or frame.size == 0:
            print("Warning: Captured frame is empty.")
            return

        # Apply brightness and saturation adjustments
        brightness = self.brightness_slider.value()
        saturation = self.saturation_slider.value()
        frame = cv2.convertScaleAbs(frame, alpha=saturation / 50, beta=brightness - 50)

        # Zoom effect
        zoom_factor = self.zoom_slider.value()
        if zoom_factor > 1:
            height, width, _ = frame.shape
            center_x, center_y = width // 2, height // 2
            radius_x, radius_y = width // (2 * zoom_factor), height // (2 * zoom_factor)
            frame = frame[center_y - radius_y:center_y + radius_y, center_x - radius_x:center_x + radius_x]
            frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)

        # YOLO Processing and stack update
        if not stackx and not stacky:
            coordinates = process_image_with_yolo(frame)
            for x, y in coordinates:
                stackx.append(x)
                stacky.append(y)

        # Pop from stacks and send to ESP8266
        if stackx and stacky:
            x = stackx.pop()
            y = stacky.pop()
            message = f"{x},{y}\n"
            esp.write(message.encode())
            print(f"Sent coordinates: {message.strip()}")

        # Update stack length display
        self.stack_label.setText(f"Stack Length: {len(stackx)}")

        # Convert frame for display
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = rgb_image.shape
        bytes_per_line = channel * width
        qimage = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qimage))



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
