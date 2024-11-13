import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QSlider
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette

from main import MainWindow

class RobotJoystick(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Robot Joystick Control")
        self.setGeometry(100, 100, 400, 600)
        self.setFixedSize(400, 600)

        # Layout for the entire UI
        main_layout = QVBoxLayout()

        # Serial Port Selection and Connection Control
        connection_layout = QHBoxLayout()

        # Create buttons with custom sizes and colors
        back_button = QPushButton("<-Back")
        back_button.setFixedSize(120, 40)
        back_button.setStyleSheet("background-color: rgb(70, 130, 180); color: white;")
        back_button.clicked.connect(self.goto_main)
        
        # Serial port dropdown
        self.port_dropdown = QComboBox()
        self.port_dropdown.addItems(["COM1", "COM2", "COM3", "COM4"])  # Example ports; update as needed
        self.port_dropdown.setFixedWidth(100)
        
        # Connect/Disconnect button
        self.connect_button = QPushButton("Connect")
        self.connect_button.setFixedWidth(100)
        self.connect_button.clicked.connect(self.toggle_connection)
        
        # Connection status indicator
        self.connection_status = QLabel("Disconnected")
        self.connection_status.setFixedSize(100, 20)
        self.connection_status.setAlignment(Qt.AlignCenter)
        self.update_connection_indicator(False)

        # Add widgets to the connection layout
        connection_layout.addWidget(back_button,)
        connection_layout.addWidget(QLabel("Port:"))
        connection_layout.addWidget(self.port_dropdown)
        connection_layout.addWidget(self.connect_button)
        connection_layout.addWidget(self.connection_status)
        
        main_layout.addLayout(connection_layout)

        # Camera display and dropdown for camera selection
        camera_display = QLabel("Camera Feed")
        camera_display.setFixedSize(380, 200)
        camera_display.setStyleSheet("background-color: black; color: white; font-size: 18px;")
        camera_display.setAlignment(Qt.AlignCenter)

        camera_dropdown = QComboBox()
        camera_dropdown.addItems(["Camera 1", "Camera 2", "Camera 3"])  # Populate with camera options
        camera_dropdown.setFixedWidth(200)
        
        main_layout.addWidget(camera_display, alignment=Qt.AlignCenter)
        main_layout.addWidget(camera_dropdown, alignment=Qt.AlignCenter)
        
        # Speed control: Slider and Speed Display
        speed_label = QLabel("Speed Control")
        speed_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        speed_slider = QSlider(Qt.Horizontal)
        speed_slider.setMinimum(0)
        speed_slider.setMaximum(100)
        speed_slider.setValue(50)  # Default speed
        speed_slider.setFixedWidth(200)
        
        self.speed_display = QLabel("Speed: 50%")
        self.speed_display.setFont(QFont("Arial", 10))
        self.speed_display.setAlignment(Qt.AlignCenter)
        
        # Update speed display on slider change
        speed_slider.valueChanged.connect(self.update_speed_display)
        
        main_layout.addWidget(speed_label, alignment=Qt.AlignCenter)
        main_layout.addWidget(speed_slider, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.speed_display, alignment=Qt.AlignCenter)

        # Directional Buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)

        # Forward button (Green)
        forward_button = self.create_button("▲", "green")
        forward_button.clicked.connect(self.move_forward)

        # Left and Right buttons (Yellow and Blue)
        horizontal_layout = QHBoxLayout()
        left_button = self.create_button("◄", "yellow")
        left_button.clicked.connect(self.move_left)

        right_button = self.create_button("►", "blue")
        right_button.clicked.connect(self.move_right)

        horizontal_layout.addWidget(left_button)
        horizontal_layout.addWidget(right_button)

        # Backward button (Red)
        backward_button = self.create_button("▼", "red")
        backward_button.clicked.connect(self.move_backward)

        # Add directional buttons to the button layout
        button_layout.addWidget(forward_button, alignment=Qt.AlignCenter)
        button_layout.addLayout(horizontal_layout)
        button_layout.addWidget(backward_button, alignment=Qt.AlignCenter)

        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # Connection state
        self.is_connected = False
    def create_button(self, text, color):
        """Creates a circular, colored button with text and a specified color."""
        button = QPushButton(text)
        button.setFixedSize(60, 60)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-size: 20px;
                font-weight: bold;
                border-radius: 30px;
            }}
            QPushButton:pressed {{
                background-color: dark{color};  /* Darker color on press */
            }}
        """)
        return button

    def update_speed_display(self, value):
        """Updates the speed display label based on slider value."""
        self.speed_display.setText(f"Speed: {value}%")

    def update_connection_indicator(self, connected):
        """Updates the connection indicator's color and text."""
        if connected:
            self.connection_status.setText("Connected")
            self.connection_status.setStyleSheet("background-color: green; color: white;")
        else:
            self.connection_status.setText("Disconnected")
            self.connection_status.setStyleSheet("background-color: red; color: white;")

    def toggle_connection(self):
        """Toggles the connection state and updates the button text and indicator."""
        if self.is_connected:
            self.is_connected = False
            self.connect_button.setText("Connect")
        else:
            selected_port = self.port_dropdown.currentText()
            print(f"Connecting to {selected_port}...")  # Implement actual connection logic here
            self.is_connected = True
            self.connect_button.setText("Disconnect")
        
        # Update the connection indicator
        self.update_connection_indicator(self.is_connected)

    def move_forward(self):
        print("Moving forward")

    def move_backward(self):
        print("Moving backward")

    def move_left(self):
        print("Moving left")

    def move_right(self):
        print("Moving right")

    def got_main(self):
        self.close()
        self.goto_main = MainWindow()
        self.goto_main.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RobotJoystick()
    window.show()
    sys.exit(app.exec_())
