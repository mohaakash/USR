import sys
import cv2
import serial
import psutil
from ultralytics import YOLO
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSlider,
    QComboBox, QPushButton, QCheckBox, QLineEdit, QGroupBox, QMessageBox
)
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from supporting.camera_output import capture_one_frame
from supporting.circular_progress_bar import CircularProgressBar
import serial.tools.list_ports
import os


# Function to get available serial ports
def get_available_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]


# FrameProcessor Thread Class
class FrameProcessor(QThread):
    frame_processed = pyqtSignal(QImage)  # Signal for processed frame
    coordinates_processed = pyqtSignal(list)  # Signal for detected coordinates

    def __init__(self, model, parent=None):
        super(FrameProcessor, self).__init__(parent)
        self.model = model
        self.running = True

    def run(self):
        while self.running:
            frame = capture_one_frame()
            if frame is not None and frame.size != 0:
                coordinates, annotated_frame = self.process_image_with_yolo(frame)

                # Convert processed frame to QImage for display
                rgb_image = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                height, width, channel = rgb_image.shape
                bytes_per_line = channel * width
                qimage = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)

                # Emit the processed frame and coordinates
                self.frame_processed.emit(qimage)
                self.coordinates_processed.emit(coordinates)

    def stop(self):
        self.running = False

    def process_image_with_yolo(self, image):
        results = self.model(image)[0]
        coordinates = []
        annotated_frame = image.copy()

        for obj in results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = obj
            x = int((x1 + x2) // 2)
            y = int((y1 + y2) // 2)
            coordinates.append((x, y))

            # Draw bounding box and label
            label = f"{self.model.names[int(class_id)]}: {score:.2f}"
            cv2.rectangle(annotated_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(
                annotated_frame, label, (int(x1), int(y1) - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
            )
        return coordinates, annotated_frame


# Main GUI Class
class USRControlSoftware(QWidget):
    def __init__(self):
        super().__init__()
        self.stackx = []
        self.stacky = []
        self.esp = None

        # Load YOLO model
        try:
            self.model = YOLO('june8.pt')
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load YOLO model: {e}")
            sys.exit(1)

        self.initUI()
        self.initSerial()

        # Create FrameProcessor Thread
        self.processor = FrameProcessor(self.model)
        self.processor.frame_processed.connect(self.update_frame_display)
        self.processor.coordinates_processed.connect(self.update_coordinates)
        self.processor.start()

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

        # GUI Timer for CPU/RAM Updates
        self.gui_timer = QTimer(self)
        self.gui_timer.timeout.connect(self.update_system_metrics)
        self.gui_timer.start(1000)

    def initSerial(self):
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
        self.left_panel = QVBoxLayout()

        # Camera Settings
        self.camera_group = QGroupBox("Camera Setting")
        self.camera_layout = QVBoxLayout()
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(1, 5)
        self.zoom_slider.valueChanged.connect(self.update_zoom_label)
        self.camera_layout.addWidget(QLabel("Zoom"))
        self.camera_layout.addWidget(self.zoom_slider)
        self.camera_group.setLayout(self.camera_layout)
        self.left_panel.addWidget(self.camera_group)

        self.leftpanel_box.setLayout(self.left_panel)

    def initRightPanel(self):
        self.right_panel = QVBoxLayout()
        self.image_container = QLabel("Camera")
        self.image_container.setFixedSize(640, 480)
        self.right_panel.addWidget(self.image_container)

    def connect_serial(self):
        port = self.usb_combo.currentText()
        try:
            self.esp = serial.Serial(port, 9600, timeout=1)
        except serial.SerialException as e:
            QMessageBox.warning(self, "Error", f"Could not connect to {port}: {e}")
            self.esp = None

    def update_zoom_label(self):
        zoom_value = self.zoom_slider.value()
        print(f"Zoom: {zoom_value}x")

    def update_frame_display(self, frame: QImage):
        self.image_container.setPixmap(QPixmap.fromImage(frame))

    def update_coordinates(self, coordinates):
        for x, y in coordinates:
            self.stackx.append(x)
            self.stacky.append(y)

    def update_system_metrics(self):
        self.cpu_value.setText(f"{psutil.cpu_percent()} %")
        self.ram_value.setText(f"{psutil.virtual_memory().percent} %")

    def closeEvent(self, event):
        self.processor.stop()
        self.processor.wait()
        if self.esp and self.esp.is_open:
            self.esp.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = USRControlSoftware()
    window.show()
    sys.exit(app.exec_())
