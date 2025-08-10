import sys
import cv2
import time
import serial
from ultralytics import YOLO
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSlider, 
    QComboBox, QPushButton, QCheckBox, QLineEdit, QGroupBox
)
from PyQt5.QtGui import QPixmap, QColor,QIcon,QImage
from PyQt5.QtCore import Qt,QTimer
from supporting.camera_output import capture_one_frame
from supporting.circular_progress_bar import CircularProgressBar

#Initialize stacks and YOLO model
stackx = []
stacky = []
model = YOLO('june8.pt')
esp = serial.Serial('COM11', 9600, timeout=1)  # Replace 'COM_PORT' with the actual ESP8266 port

def process_image_with_yolo(image):
    results = model(image)[0]
    coordinates = []
    annotated_frame = image.copy()

    for obj in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = obj
        x = int((x1 + x2) // 2)
        y = int((y1 + y2) // 2)
        coordinates.append((x, y))

        # Draw bounding box and label
        label = f"{model.names[int(class_id)]}: {score:.2f}"
        cv2.rectangle(annotated_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.putText(
            annotated_frame, label, (int(x1), int(y1) - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
        )
    return coordinates, annotated_frame

class USRControlSoftware(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("USR Control Software")
        self.setWindowIcon(QIcon("photos/robot.ico"))
        
        # Set fixed size for main window
        self.setFixedSize(1300, 950)
        
        # Main container layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(10, 0, 10, 0)  # Remove top and bottom margins
        self.main_layout.setSpacing(5)  # Minimal spacing between sections
        
        # Header section
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)  # No margins
        header_layout.setSpacing(10)  # Control spacing between header widgets
        
        # USB section
        usb_layout = QHBoxLayout()
        usb_layout.setSpacing(5)
        usb_label = QLabel("USB")
        usb_combo = QComboBox()
        usb_combo.addItem("COM7")
        usb_combo.setFixedSize(80, 25)
        
        start_button = QPushButton("Start")
        start_button.setFixedSize(80, 35)
        stop_button = QPushButton("Stop")
        stop_button.setFixedSize(80, 35)
        close_button = QPushButton("Close")
        close_button.setFixedSize(80, 35)
        
        usb_layout.addWidget(usb_label)
        usb_layout.addWidget(usb_combo)
        usb_layout.addWidget(start_button)
        usb_layout.addWidget(stop_button)
        usb_layout.addWidget(close_button)
        
        # Status section
        status_layout = QHBoxLayout()
        status_layout.setSpacing(5)
        
        cpu_label = QLabel("CPU Usage")
        cpu_value = QLabel("93.2 %")
        cpu_value.setStyleSheet("color: red; font-size: 25px; font-weight: bold;")
        
        ram_label = QLabel("Ram Usage")
        ram_value = QLabel("56.2 %")
        ram_value.setStyleSheet("color: green; font-size: 25px; font-weight: bold;")
        
        status_layout.addWidget(cpu_label)
        status_layout.addWidget(cpu_value)
        status_layout.addWidget(ram_label)
        status_layout.addWidget(ram_value)
        
        header_layout.addLayout(usb_layout)
        header_layout.addStretch()
        header_layout.addLayout(status_layout)
        
        # Left panel
        self.leftpanel_box = QGroupBox()
        self.leftpanel_box.setFixedSize(320,820 )
        self.leftpanel_box.setStyleSheet("QGroupBox { background-color: rgb(220, 255, 229); }")
        self.left_panel = QVBoxLayout()
        self.left_panel.setSpacing(10)
             
        # camera Setting
        self.camera_group = QGroupBox("Camera Setting")
        self.camera_group.setFixedSize(300, 150)
        self.camera_layout = QVBoxLayout()
        self.camera_layout.setContentsMargins(10, 10, 10, 10)
        self.camera_layout.setSpacing(5)
        
        self.zoom_slider = QSlider(Qt.Horizontal,self)
        self.zoom_slider.setFixedSize(180, 20)
        self.zoom_slider.setRange(1, 5)
        self.zoom_slider.setValue(1)
        self.zoom_slider_label = QLabel("Zoom: 1x", self)

        self.brightness_slider = QSlider(Qt.Horizontal, self)
        self.brightness_slider.setFixedSize(180, 20)
        self.brightness_slider.setRange(0, 100)
        self.brightness_slider.setValue(50)
        self.brightness_slider_label = QLabel("Brightness: 50", self)

        self.saturation_slider = QSlider(Qt.Horizontal, self)
        self.saturation_slider.setFixedSize(180, 20)
        self.saturation_slider.setRange(0, 100)
        self.saturation_slider.setValue(50)
        self.saturation_slider_label = QLabel("Saturation: 50", self)
        
        self.camera_layout.addWidget(self.zoom_slider_label)
        self.camera_layout.addWidget(self.zoom_slider)
        self.camera_layout.addWidget(self.brightness_slider_label)
        self.camera_layout.addWidget(self.brightness_slider)
        self.camera_layout.addWidget(self.saturation_slider_label)
        self.camera_layout.addWidget(self.saturation_slider)
        self.camera_group.setLayout(self.camera_layout)
        
        # Set Area
        set_area_group = QGroupBox("Set Area")
        set_area_group.setFixedSize(300, 150)
        set_area_layout = QHBoxLayout()
        set_area_layout.setSpacing(10)
        
        height_label = QLabel("Height")
        height_input = QLineEdit("0")
        height_input.setFixedSize(60, 20)
        height_button = QPushButton("OK")
        height_button.setFixedSize(50, 25)
        height_button.setStyleSheet("background-color: green; color: white;")
        
        width_label = QLabel("Width")
        width_input = QLineEdit("0")
        width_input.setFixedSize(60, 20)
        width_button = QPushButton("Close")
        width_button.setFixedSize(50, 25)
        width_button.setStyleSheet("background-color: orange; color: white;")
        
        height_layout = QVBoxLayout()
        height_layout.setSpacing(5)
        height_layout.addWidget(height_label)
        height_layout.addWidget(height_input)
        height_layout.addWidget(height_button)
        
        width_layout = QVBoxLayout()
        width_layout.setSpacing(5)
        width_layout.addWidget(width_label)
        width_layout.addWidget(width_input)
        width_layout.addWidget(width_button)
        
        set_area_layout.addLayout(height_layout)
        set_area_layout.addLayout(width_layout)
        set_area_group.setLayout(set_area_layout)
        
        # Target Class to Spray
        target_group = QGroupBox("Set Target Class to Spray")
        target_group.setFixedSize(300, 100)
        target_layout = QVBoxLayout()
        target_layout.setContentsMargins(10, 10, 10, 10)
        target_layout.setSpacing(5)
        
        crop_layout = QHBoxLayout()
        crop_checkbox = QCheckBox("Crop")
        crop_button = QPushButton("SET")
        crop_button.setFixedSize(50, 25)
        crop_layout.addWidget(crop_checkbox)
        crop_layout.addWidget(crop_button)
        
        weed_layout = QHBoxLayout()
        weed_checkbox = QCheckBox("Weed")
        weed_button = QPushButton("SET")
        weed_button.setFixedSize(50, 25)
        weed_layout.addWidget(weed_checkbox)
        weed_layout.addWidget(weed_button)
        
        target_layout.addLayout(crop_layout)
        target_layout.addLayout(weed_layout)
        
        
        target_group.setLayout(target_layout)
        
        # Add sections to the left panel
        self.left_panel.addWidget(self.camera_group)
        self.left_panel.addWidget(set_area_group)
        self.left_panel.addWidget(target_group)
        self.leftpanel_box.setLayout(self.left_panel)
        
        # Right panel
        self.right_panel = QVBoxLayout()
        self.right_panel.setSpacing(10)
        
        # Image container
        self.image_container = QLabel("Camera")
        self.image_container.setFixedSize(640, 480)
        self.image_container.setStyleSheet("border: 3px solid #6495ED; background-color: #FFFFFF;")

        # Counter
        self.counter_box = QGroupBox("Counter")
        self.counter_box.setFixedSize(640, 220)
        self.counter_layout = QHBoxLayout()
        self.counter_layout.setSpacing(10)
        self.counter_layout.setContentsMargins(10, 10, 10, 10)
        
        self.progress_bar_counter = CircularProgressBar(max_value=100, label_text="Total Target")
        self.progress_bar_remaining = CircularProgressBar(max_value=100, label_text="Completion")
        self.progress_bar_counter.setValue(0)
        self.progress_bar_remaining.setValue(0)
        self.progress_bar_remaining.setProgressColor(QColor(0, 204, 0))
        
        self.counter_layout.addWidget(self.progress_bar_counter)
        self.counter_layout.addWidget(self.progress_bar_remaining)
        self.counter_box.setLayout(self.counter_layout)
        

        # Status section
        status_box = QLabel("0: 480x640 48 weeds, 2 crops, 46.5ms\n"
                            "Speed: 1.0ms preprocess, 46.5ms inference, 1.0ms postprocess per image at shape (1, 3, 480, 640)")
        status_box.setFixedSize(640, 150)
        status_box.setStyleSheet("background-color: #e0e0e0; border: 1px solid #ccc; ")


        self.right_panel.addWidget(self.image_container)
        self.right_panel.addStretch()
        self.right_panel.addWidget(self.counter_box)
        self.right_panel.addWidget(status_box)

        # Combine left and right panel
        self.main_panel_layout = QHBoxLayout()
        self.main_panel_layout.addWidget(self.leftpanel_box)
        self.main_panel_layout.addLayout(self.right_panel)
        
        # Add all sections to main layout
        self.main_layout.addLayout(header_layout)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.main_panel_layout)
        
        self.setLayout(self.main_layout)

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
        coordinates, annotated_frame = process_image_with_yolo(frame)
        if not stackx and not stacky:
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
        self.progress_bar_counter.setValue(f"{len(stackx)}")

        # Convert annotated frame for processed display
        rgb_annotated = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        height, width, channel = rgb_annotated.shape
        bytes_per_line = channel * width
        annotated_qimage = QImage(rgb_annotated.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.image_container.setPixmap(QPixmap.fromImage(annotated_qimage))
    

        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = USRControlSoftware()
    window.show()
    sys.exit(app.exec_())
