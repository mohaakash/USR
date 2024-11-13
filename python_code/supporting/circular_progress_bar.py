from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QFont, QColor, QPen
from PyQt5.QtWidgets import QWidget, QVBoxLayout

class CircularProgressBar(QWidget):
    def __init__(self, max_value=100, label_text="Progress", progress_color=QColor(255, 80, 80)):
        super().__init__()
        self.value = 0  # Starting progress value
        self.max_value = max_value  # Max value for progress bar
        self.label_text = label_text  # Label text inside the progress bar
        self.progress_color = progress_color  # Progress color (default: red)
        self.initUI()

    def initUI(self):
        # Set default size for the widget
        self.setFixedSize(180, 180)

    def setValue(self, value):
        """Set the progress value and update the UI."""
        self.value = max(0, min(value, self.max_value))  # Clamp value between 0 and max_value
        self.update()

    def setProgressColor(self, color):
        """Set the color of the progress bar."""
        self.progress_color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect().adjusted(10, 10, -10, -10)  # Adjust the rect evenly from all sides

        # Set anti-aliasing for smoother drawing
        painter.setRenderHint(QPainter.Antialiasing)
        pen_width = 15  # Thickness of the progress arc
        
        # Draw background circle (hollow look)
        painter.setPen(QPen(QColor(50, 50, 50), pen_width, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(rect, 0, 360 * 16)

        # Draw progress arc with specified color
        painter.setPen(QPen(self.progress_color, pen_width, Qt.SolidLine, Qt.RoundCap))
        angle_span = int(360 * (self.value / self.max_value))  # Angle based on progress
        painter.drawArc(rect, 90 * 16, -angle_span * 16)

        # Draw progress text in the center with progress color
        painter.setPen(self.progress_color)
        painter.setFont(QFont("Arial", 15, QFont.Bold))
        painter.drawText(rect, Qt.AlignCenter, f"{int(self.value)}%")

        # Draw label text below progress text with the same color
        label_rect = rect.adjusted(0, 40, 0, 0)  # Adjust to position label text slightly below the percentage
        painter.setFont(QFont("Arial", 8))
        painter.drawText(label_rect, Qt.AlignCenter, self.label_text)

    def setLabelText(self, text):
        """Set the label text inside the progress bar."""
        self.label_text = text
        self.update()

    def setMaxValue(self, max_value):
        """Set the maximum value for the progress bar."""
        self.max_value = max_value
