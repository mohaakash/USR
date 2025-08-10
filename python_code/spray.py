import sys
import cv2
import serial
import psutil

from ultralytics import YOLO
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSlider,
    QComboBox, QPushButton, QCheckBox, QLineEdit, QGroupBox, QMessageBox
)
from PyQt5.QtGui import QPixmap, QColor, QIcon, QImage
from PyQt5.QtCore import Qt, QTimer
from supporting.camera_output import capture_one_frame
from supporting.circular_progress_bar import CircularProgressBar
import serial.tools.list_ports


def get_available_ports():
    """
    Get a list of available serial ports.
    """
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]


class USRControlSoftware(QWidget):
    def __init__(self):
        super().__init__()
        self.stackx = []  # Stack for x-coordinates
        self.stacky = []  # Stack for y-coordinates
        self.esp = None

        # YOLO model initialization
        try:
            self.model = YOLO('novlast.pt')
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load YOLO model: {e}")
            sys.exit(1)

        self.initUI()
        #self.initSerial()

        # Timer for periodic frame processing and communication
        self.processing_timer = QTimer(self)
        self.processing_timer.timeout.connect(self.process_and_send_coordinates)
        self.processing_timer.start(5000)  # 5000ms = 5 seconds

    def initUI(self):
        self.setWindowTitle("USR Control Software")
        self.setWindowIcon(QIcon("photos/robot.ico"))
        self.setFixedSize(1300, 950)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(10, 0, 10, 0)
        self.main_layout.setSpacing(5)

        self.initHeader()
        self.initLeftPanel()
        self.initRightPanel()

        self.main_panel_layout = QHBoxLayout()
        self.main_panel_layout.addWidget(self.leftpanel_box)
        self.main_panel_layout.addLayout(self.right_panel)

        self.main_layout.addLayout(self.header_layout)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.main_panel_layout)
        self.setLayout(self.main_layout)

        # Timer for GUI updates
        self.gui_timer = QTimer(self)
        self.gui_timer.timeout.connect(self.update_frame)
        self.gui_timer.start(200)

        # Connect slider signals
        self.zoom_slider.valueChanged.connect(self.update_zoom_label)
        self.brightness_slider.valueChanged.connect(self.update_brightness_label)
        self.saturation_slider.valueChanged.connect(self.update_saturation_label)

    def initSerial(self):
        """
        Populate available serial ports in the dropdown.
        """
        available_ports = get_available_ports()
        if available_ports:
            self.usb_combo.addItems(available_ports)
        else:
            QMessageBox.warning(self, "No Ports Found", "No available serial ports detected.")

    def initHeader(self):
        self.header_layout = QHBoxLayout()
        self.header_layout.setSpacing(10)

        usb_layout = QHBoxLayout()
        usb_label = QLabel("USB")
        self.usb_combo = QComboBox()
        available_ports = get_available_ports()
        if available_ports:
            self.usb_combo.addItems(available_ports)
        else:
            QMessageBox.warning(self, "No Ports Found", "No available serial ports detected.")

        connect_button = QPushButton("Connect")
        connect_button.clicked.connect(self.connect_serial)

        usb_layout.addWidget(usb_label)
        usb_layout.addWidget(self.usb_combo)
        usb_layout.addWidget(connect_button)

        status_layout = QHBoxLayout()
        cpu_label = QLabel("CPU Usage")
        self.cpu_value = QLabel("0.0 %")
        ram_label = QLabel("RAM Usage")
        self.ram_value = QLabel("0.0 %")

        status_layout.addWidget(cpu_label)
        status_layout.addWidget(self.cpu_value)
        status_layout.addWidget(ram_label)
        status_layout.addWidget(self.ram_value)

        self.header_layout.addLayout(usb_layout)
        self.header_layout.addStretch()
        self.header_layout.addLayout(status_layout)

    def initLeftPanel(self):
        self.leftpanel_box = QGroupBox()
        self.leftpanel_box.setFixedSize(320, 820)
        self.leftpanel_box.setStyleSheet("QGroupBox { background-color: rgb(220, 255, 229); }")
        self.left_panel = QVBoxLayout()
        self.left_panel.setSpacing(10)

        self.initCameraSettings()
        self.initSetArea()
        self.initTargetClass()

        self.leftpanel_box.setLayout(self.left_panel)

    def initCameraSettings(self):
        self.camera_group = QGroupBox("Camera Setting")
        self.camera_group.setFixedSize(300, 250)
        self.camera_layout = QVBoxLayout()
        self.camera_layout.setContentsMargins(10, 10, 10, 10)
        self.camera_layout.setSpacing(5)

        self.zoom_slider = QSlider(Qt.Horizontal, self)
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
        self.left_panel.addWidget(self.camera_group)

    def initSetArea(self):
        set_area_group = QGroupBox("Set Area")
        set_area_group.setFixedSize(300, 150)
        set_area_layout = QHBoxLayout()

        height_label = QLabel("Height")
        self.height_input = QLineEdit("0")
        self.height_input.setFixedSize(60, 20)
        height_button = QPushButton("OK")

        width_label = QLabel("Width")
        self.width_input = QLineEdit("0")
        self.width_input.setFixedSize(60, 20)
        width_button = QPushButton("Close")

        height_layout = QVBoxLayout()
        height_layout.addWidget(height_label)
        height_layout.addWidget(self.height_input)
        height_layout.addWidget(height_button)

        width_layout = QVBoxLayout()
        width_layout.addWidget(width_label)
        width_layout.addWidget(self.width_input)
        width_layout.addWidget(width_button)

        set_area_layout.addLayout(height_layout)
        set_area_layout.addLayout(width_layout)
        set_area_group.setLayout(set_area_layout)

        self.left_panel.addWidget(set_area_group)

    def initTargetClass(self):
        target_group = QGroupBox("Set Target Class to Spray")
        target_group.setFixedSize(300, 200)
        target_layout = QVBoxLayout()

        crop_checkbox = QCheckBox("Crop")
        crop_button = QPushButton("SET")
        weed_checkbox = QCheckBox("Weed")
        weed_button = QPushButton("SET")

        target_layout.addWidget(crop_checkbox)
        target_layout.addWidget(crop_button)
        target_layout.addWidget(weed_checkbox)
        target_layout.addWidget(weed_button)
        target_group.setLayout(target_layout)

        self.left_panel.addWidget(target_group)

    def initRightPanel(self):
        self.right_panel = QVBoxLayout()

        self.image_container = QLabel("Camera")
        self.image_container.setFixedSize(640, 480)
        self.image_container.setStyleSheet("border: 3px solid #6495ED; background-color: #FFFFFF;")

        self.counter_box = QGroupBox("Counter")
        self.counter_box.setFixedSize(640, 220)
        self.counter_layout = QHBoxLayout()
        self.progress_bar_counter = CircularProgressBar(max_value=100, label_text="Total Target",progress_color=QColor(57, 153, 24))
        self.progress_bar_remaining = CircularProgressBar(max_value=100, label_text="Remaining")
        self.counter_layout.addWidget(self.progress_bar_counter)
        self.counter_layout.addWidget(self.progress_bar_remaining)
        self.counter_box.setLayout(self.counter_layout)

        self.status_box = QLabel("Status: Ready")
        self.status_box.setFixedSize(640, 150)
        self.status_box.setStyleSheet("background-color: #e0e0e0; border: 1px solid #ccc; ")

        self.right_panel.addWidget(self.image_container)
        self.right_panel.addWidget(self.counter_box)
        self.right_panel.addWidget(self.status_box)

    def connect_serial(self):
        port = self.usb_combo.currentText()
        try:
            self.esp = serial.Serial(port, 9600, timeout=1)
        except serial.SerialException as e:
            QMessageBox.warning(self, "Error", f"Could not connect to {port}: {e}")
            self.status_box.setText(f"Could not connect to {port}: {e}")
            self.esp = None

    def update_zoom_label(self):
        zoom_value = self.zoom_slider.value()
        self.zoom_slider_label.setText(f"Zoom: {zoom_value}x")

    def update_brightness_label(self):
        brightness_value = self.brightness_slider.value()
        self.brightness_slider_label.setText(f"Brightness: {brightness_value}")

    def update_saturation_label(self):
        saturation_value = self.saturation_slider.value()
        self.saturation_slider_label.setText(f"Saturation: {saturation_value}")
    
    def process_and_send_coordinates(self):
        """
        Process a frame and send coordinates to the ESP8266 via serial communication.
        """
        if not self.esp or not self.esp.is_open:
            print("ESP is not connected.")
            self.status_box.setText(f"ESP is not connected.")
            return

        # Step 3: Check if stacks are empty
        if not self.stackx and not self.stacky:
            
            message = f"runesp2\n"
            self.esp.write(message.encode())

            frame = capture_one_frame()
            if frame is None or frame.size == 0:
                print("Warning: Captured frame is empty.")
                self.status_box.setText(f"Warning: Captured frame is empty.")
                return

            coordinates,annotated_frame = self.process_image_with_yolo(frame)

            # Convert frame to RGB for displaying
            rgb_image = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            height, width, channel = rgb_image.shape
            bytes_per_line = channel * width
            qimage = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
            self.image_container.setPixmap(QPixmap.fromImage(qimage))

            for x, y in coordinates:
                self.stackx.append(x)
                self.stacky.append(y)
            self.progress_bar_counter.setValue(len(self.stackx))
        else:
            # Step 5: Pop from stacks and send to ESP8266
            self.progress_bar_remaining.setValue(len(self.stackx))
            x = self.stackx.pop()
            y = self.stacky.pop()
            message = f"{x},{y}\n"
            self.esp.write(message.encode())
            print(f"Sent coordinates: {message.strip()}")
            self.status_box.setText(f"Sent coordinates: {message.strip()}")

    def process_image_with_yolo(self, image):
        """
        Process the image using YOLO and return coordinates and annotated image.
        """
        results = self.model(image)[0]
        coordinates = []
        annotated_frame = image.copy()


        for obj in results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = obj
            x = int((x1 + x2) // 2)
            y = int((y1 + y2) // 2)
            coordinates.append((x, y))

            # Draw bounding box and label
            detection_color= (0, 0, 255) if int(class_id)==0 else (0, 240, 0)
            label = f"{self.model.names[int(class_id)]}: {score:.2f}"
            cv2.rectangle(annotated_frame, (int(x1), int(y1)), (int(x2), int(y2)), detection_color, 2)
            cv2.putText(
                annotated_frame, label, (int(x1), int(y1) - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, detection_color, 2
            )
        return coordinates, annotated_frame

    def update_frame(self):
        if self.esp is None or not self.esp.is_open:
            print("ESP is not connected.")
            self.status_box.setText(f"Warning: ESP is not connected..")
            return

        frame = capture_one_frame()
        if frame is None or frame.size == 0:
            print("Warning: Captured frame is empty.")
            self.status_box.setText(f"Warning: Captured frame is empty.")
            return

        # Update system metrics
        self.cpu_value.setText(f"{psutil.cpu_percent()} %")
        self.ram_value.setText(f"{psutil.virtual_memory().percent} %")


    def closeEvent(self, event):
        if self.esp and self.esp.is_open:
            self.esp.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = USRControlSoftware()
    window.show()
    sys.exit(app.exec_())
