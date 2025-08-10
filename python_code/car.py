import sys
import serial
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QSlider, QPushButton, QLabel, QWidget
)
from PyQt5.QtCore import Qt


class MotorControlGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # Serial port configuration
        self.serial_port = "COM9"  # Replace with the actual COM port of your ESP8266
        self.baud_rate = 9600
        try:
            self.serial = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            self.serial = None

        # GUI setup
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Motor Control")
        self.setGeometry(100, 100, 300, 200)

        # Layout
        layout = QVBoxLayout()

        # Speed Slider
        self.speed_label = QLabel("Speed: 0", self)
        self.speed_slider = QSlider(Qt.Horizontal, self)
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(255)  # PWM range for speed control
        self.speed_slider.setValue(0)
        self.speed_slider.valueChanged.connect(self.set_speed)

        # Direction Buttons
        self.forward_button = QPushButton("Forward", self)
        self.forward_button.clicked.connect(self.set_forward)

        self.backward_button = QPushButton("Backward", self)
        self.backward_button.clicked.connect(self.set_backward)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.set_stop)

        # Add widgets to layout
        layout.addWidget(self.speed_label)
        layout.addWidget(self.speed_slider)
        layout.addWidget(self.forward_button)
        layout.addWidget(self.backward_button)
        layout.addWidget(self.stop_button)

        # Central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def set_speed(self, value):
        self.speed_label.setText(f"Speed: {value}")
        self.send_command(f"SPEED:{value}")

    def set_forward(self):
        self.send_command("DIR:FORWARD")

    def set_backward(self):
        self.send_command("DIR:BACKWARD")

    def set_stop(self):
        self.send_command("DIR:STOP")

    def send_command(self, command):
        if self.serial and self.serial.is_open:
            self.serial.write(f"{command}\n".encode())
            self.serial.flush()
            print(f"Command sent: {command}")
        else:
            print("Serial port not open!")

    def closeEvent(self, event):
        if self.serial and self.serial.is_open:
            self.serial.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = MotorControlGUI()
    gui.show()
    sys.exit(app.exec_())
