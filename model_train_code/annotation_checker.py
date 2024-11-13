import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QLabel, QVBoxLayout, QPushButton,
    QHBoxLayout, QWidget, QListWidget, QMessageBox
)
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QRectF


class AnnotationViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Annotation Viewer and Editor")
        self.setGeometry(100, 100, 1000, 800)

        # Variables
        self.image_dir = None
        self.label_dir = None
        self.image_files = []
        self.current_index = 0
        self.annotations = []
        self.current_boxes = []

        # Main layout
        main_layout = QVBoxLayout()
        
        # Image display
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.image_label)

        # Navigation and control buttons
        controls_layout = QHBoxLayout()

        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.prev_image)
        controls_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_image)
        controls_layout.addWidget(self.next_button)

        self.load_button = QPushButton("Load Folder")
        self.load_button.clicked.connect(self.load_folder)
        controls_layout.addWidget(self.load_button)

        self.save_button = QPushButton("Save Annotation")
        self.save_button.clicked.connect(self.save_annotation)
        controls_layout.addWidget(self.save_button)

        main_layout.addLayout(controls_layout)

        # Container widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
    #load foler
    def load_folder(self):
        # Open folder dialog
        folder_path = QFileDialog.getExistingDirectory(self, "Select Dataset Folder")
        if not folder_path:
            return

        # Check for images and labels subfolders
        self.image_dir = os.path.join(folder_path, "images")
        self.label_dir = os.path.join(folder_path, "labels")

        if not os.path.exists(self.image_dir) or not os.path.exists(self.label_dir):
            QMessageBox.warning(self, "Error", "Selected folder must contain 'images' and 'labels' subfolders.")
            return

        # Load image files (supporting multiple formats)
        valid_extensions = (".jpg", ".jpeg", ".png")
        self.image_files = sorted([f for f in os.listdir(self.image_dir) if f.lower().endswith(valid_extensions)])

        if not self.image_files:
            QMessageBox.warning(self, "Error", "No valid image files found in the 'images' folder.")
            return

        self.current_index = 0
        print(f"[INFO] Found {len(self.image_files)} images in {self.image_dir}")
        self.load_image_and_annotation()


    def load_image_and_annotation(self):
        # Load image
        image_path = os.path.join(self.image_dir, self.image_files[self.current_index])
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # Load annotation
        label_path = os.path.join(self.label_dir, self.image_files[self.current_index].replace(".jpg", ".txt"))
        self.current_boxes = []

        if os.path.exists(label_path):
            with open(label_path, "r") as f:
                for line in f.readlines():
                    parts = list(map(float, line.strip().split()))
                    self.current_boxes.append(parts)

        self.update()

    def save_annotation(self):
        if not self.image_files:
            return

        label_path = os.path.join(self.label_dir, self.image_files[self.current_index].replace(".jpg", ".txt"))
        with open(label_path, "w") as f:
            for box in self.current_boxes:
                f.write(" ".join(map(str, box)) + "\n")
        QMessageBox.information(self, "Success", "Annotation saved successfully.")

    def next_image(self):
        if not self.image_files or self.current_index >= len(self.image_files) - 1:
            return
        self.current_index += 1
        self.load_image_and_annotation()

    def prev_image(self):
        if not self.image_files or self.current_index <= 0:
            return
        self.current_index -= 1
        self.load_image_and_annotation()
    #paint event
    def paintEvent(self, event):
        super().paintEvent(event)

        if not self.image_files or not self.current_boxes:
            return

        # Painter setup
        painter = QPainter(self.image_label)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor(0, 0, 0), 4))  # Red bounding boxes

        # Scale factors for QLabel
        if self.image_label.pixmap():
            label_size = self.image_label.size()
            pixmap_size = self.image_label.pixmap().size()
            scale_w = label_size.width() / pixmap_size.width()
            scale_h = label_size.height() / pixmap_size.height()

            # Draw bounding boxes
            for box in self.current_boxes:
                label, x_center, y_center, width, height = box

                # Convert YOLO format to rectangle (x_min, y_min, width, height)
                x_min = (x_center - width / 2) * pixmap_size.width() * scale_w
                y_min = (y_center - height / 2) * pixmap_size.height() * scale_h
                box_width = width * pixmap_size.width() * scale_w
                box_height = height * pixmap_size.height() * scale_h

                # Draw the rectangle
                painter.drawRect(QRectF(x_min, y_min, box_width, box_height))

        painter.end()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnnotationViewer()
    window.show()
    sys.exit(app.exec_())
