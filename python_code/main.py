       
import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QPixmap, QPalette, QBrush,QIcon
from PyQt5.QtCore import Qt

from gui import USRControlSoftware
from car_control import RobotJoystick


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("USR Control software")
        self.setWindowIcon(QIcon("photos/robot.ico"))
        self.setGeometry(100, 100, 300, 400)
        self.setFixedSize(800, 500)

        # Set background image
        self.set_background_image("photos/USRlow.png")

        # Create layout for buttons
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addStretch()  # Push buttons to the bottom

        # Create buttons with custom sizes and colors
        button1 = QPushButton("Drive >")
        button1.setFixedSize(120, 40)
        button1.setStyleSheet("background-color: rgb(70, 130, 180); color: white;")
        button1.clicked.connect(self.open_car_control)

        button2 = QPushButton("Spray >")
        button2.setFixedSize(120, 40)
        button2.setStyleSheet("background-color: rgb(220, 20, 60); color: white;")
        button2.clicked.connect(self.open_usr_control_software)

        # Add buttons to layout
        layout.addWidget(button1, alignment=Qt.AlignCenter)
        layout.addWidget(button2, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def set_background_image(self, image_path):
        # Set the background image
        palette = QPalette()
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
        self.setPalette(palette)

    def open_usr_control_software(self):
        self.close()
        # Create and show the USRControlSoftware window
        self.usr_control_window = USRControlSoftware()
        self.usr_control_window.show()
        

    def open_car_control(self):
        self.close()
        self.open_car_control = RobotJoystick()
        self.open_car_control.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
