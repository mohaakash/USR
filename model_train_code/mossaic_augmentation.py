import sys
import cv2
import os
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QWidget, QSlider, QFileDialog, QComboBox, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage

class MosaicApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mosaic Augmentation GUI")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize image list and transformations
        self.images = [None] * 4
        self.zoom_levels = [100] * 4
        self.rotations = [0] * 4
        self.x_translations = [0] * 4
        self.y_translations = [0] * 4
        self.export_folder = None

        # Main layout
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()

        # Image controls and preview
        self.image_controls = []
        self.image_labels = []
        for i in range(4):
            group_box = QGroupBox(f"Image {i + 1} Controls")
            group_layout = QHBoxLayout()

            slider_box = QGroupBox()
            slider_box.setFixedSize(350, 200)
            slier_layout = QVBoxLayout()

            # Image selection label
            label = QLabel("Select Image")
            label.setFixedSize(200, 200)
            label.setStyleSheet("border: 1px solid black;")
            self.image_labels.append(label)
            label.mousePressEvent = lambda _, idx=i: self.select_image(idx)
            slier_layout.addWidget(label)

            # Zoom slider
            zoom_slider = QSlider(Qt.Horizontal)
            zoom_slider.setRange(1, 200)
            zoom_slider.setValue(100)
            zoom_slider.valueChanged.connect(lambda _, idx=i: self.update_preview())
            slier_layout.addWidget(QLabel("Zoom"))
            slier_layout.addWidget(zoom_slider)

            # Rotation dropdown
            rotation_combo = QComboBox()
            rotation_combo.addItems(["0", "90", "180", "270"])
            rotation_combo.currentIndexChanged.connect(lambda _, idx=i: self.update_preview())
            slier_layout.addWidget(QLabel("Rotation"))
            slier_layout.addWidget(rotation_combo)

            # X Translation slider
            x_slider = QSlider(Qt.Horizontal)
            x_slider.setRange(-100, 100)
            x_slider.setValue(0)
            x_slider.valueChanged.connect(lambda _, idx=i: self.update_preview())
            slier_layout.addWidget(QLabel("X Translation"))
            slier_layout.addWidget(x_slider)

            # Y Translation slider
            y_slider = QSlider(Qt.Horizontal)
            y_slider.setRange(-100, 100)
            y_slider.setValue(0)
            y_slider.valueChanged.connect(lambda _, idx=i: self.update_preview())
            slier_layout.addWidget(QLabel("Y Translation"))
            slier_layout.addWidget(y_slider)

            # Store controls in a list for easy access
            self.image_controls.append({
                'zoom': zoom_slider,
                'rotation': rotation_combo,
                'x_trans': x_slider,
                'y_trans': y_slider
            })

            slider_box.setLayout(slier_layout)
            group_layout.addWidget(slider_box)
            group_box.setLayout(group_layout)
            left_layout.addWidget(group_box)

        main_layout.addLayout(left_layout)

        # Right Layout for Preview and Export Controls
        right_layout = QVBoxLayout()
        
        # Live Preview of Mosaic Image
        self.preview_label = QLabel("Live Mosaic Preview")
        self.preview_label.setFixedSize(640, 640)
        self.preview_label.setStyleSheet("border: 2px solid black;")
        right_layout.addWidget(self.preview_label)

        # Folder selection and export buttons
        button_layout = QHBoxLayout()
        folder_button = QPushButton("Select Export Folder")
        folder_button.clicked.connect(self.select_folder)
        button_layout.addWidget(folder_button)

        export_button = QPushButton("Export Mosaic Image")
        export_button.clicked.connect(self.export_image)
        button_layout.addWidget(export_button)

        right_layout.addLayout(button_layout)
        main_layout.addLayout(right_layout)

        # Set main layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def select_image(self, idx):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Image")
        
        if file_path:
            self.images[idx] = cv2.imread(file_path)
            self.set_preview_image(self.images[idx], idx)
            self.update_preview()

    def set_preview_image(self, img, idx):
        # Show the selected image in the corresponding label
        qimage = self.convert_cv_qt(img)
        self.image_labels[idx].setPixmap(qimage)

    def select_folder(self):
        self.export_folder = QFileDialog.getExistingDirectory(self, "Select Export Folder")
        if self.export_folder:
            print("Selected export folder:", self.export_folder)

    def update_preview(self):
        # Apply transformations to each image and create mosaic
        transformed_images = [self.apply_individual_transformations(img, i) for i, img in enumerate(self.images) if img is not None]
        if len(transformed_images) == 4:
            mosaic_image = self.create_mosaic(transformed_images, (640, 640))
            qimage = self.convert_cv_qt(mosaic_image)
            self.preview_label.setPixmap(qimage)

    def apply_individual_transformations(self, image, idx):
        # Retrieve transformations from sliders
        zoom = self.image_controls[idx]['zoom'].value() / 100
        rotation = int(self.image_controls[idx]['rotation'].currentText())
        x_trans = self.image_controls[idx]['x_trans'].value()
        y_trans = self.image_controls[idx]['y_trans'].value()
        
        # Set target size for each quadrant
        quadrant_size = 320  # since 640x640 mosaic, each quadrant is 320x320
        target_size = int(quadrant_size * zoom)

        # Resize the image to target size
        resized_image = cv2.resize(image, (target_size, target_size))

        # Initialize zoomed_image to avoid UnboundLocalError
        if target_size < quadrant_size:
            # Center the resized image in a blank canvas if smaller than quadrant size
            zoomed_image = np.zeros((quadrant_size, quadrant_size, 3), dtype=np.uint8)
            y_offset = (quadrant_size - target_size) // 2
            x_offset = (quadrant_size - target_size) // 2
            zoomed_image[y_offset:y_offset + target_size, x_offset:x_offset + target_size] = resized_image
        elif target_size > quadrant_size:
            # Crop if resized image is larger than quadrant size
            zoomed_image = resized_image[:quadrant_size, :quadrant_size]
        else:
            # Directly assign if target_size matches quadrant_size
            zoomed_image = resized_image

        # Apply rotation
        if rotation == 90:
            zoomed_image = cv2.rotate(zoomed_image, cv2.ROTATE_90_CLOCKWISE)
        elif rotation == 180:
            zoomed_image = cv2.rotate(zoomed_image, cv2.ROTATE_180)
        elif rotation == 270:
            zoomed_image = cv2.rotate(zoomed_image, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # Apply translation
        translation_matrix = np.float32([[1, 0, x_trans], [0, 1, y_trans]])
        transformed_image = cv2.warpAffine(zoomed_image, translation_matrix, (quadrant_size, quadrant_size))

        return transformed_image




    def export_image(self):
        if None in self.images:
            print("Please select all four images.")
            return

        if not self.export_folder:
            print("Please select an export folder.")
            return

        # Apply transformations and create mosaic
        transformed_images = [self.apply_individual_transformations(img, i) for i, img in enumerate(self.images) if img is not None]
        if len(transformed_images) == 4:
            mosaic_image = self.create_mosaic(transformed_images, (640, 640))
            save_path = os.path.join(self.export_folder, "mosaic_image.jpg")
            cv2.imwrite(save_path, mosaic_image)
            print("Image saved to", save_path)

    def create_mosaic(self, images, output_size=(640, 640)):
        half_w, half_h = output_size[0] // 2, output_size[1] // 2
        mosaic_img = np.zeros((output_size[1], output_size[0], 3), dtype=np.uint8)

        # Resize images and place them in quadrants
        resized_images = [cv2.resize(img, (half_w, half_h)) for img in images]
        mosaic_img[0:half_h, 0:half_w] = resized_images[0]  # Top-left
        mosaic_img[0:half_h, half_w:] = resized_images[1]   # Top-right
        mosaic_img[half_h:, 0:half_w] = resized_images[2]   # Bottom-left
        mosaic_img[half_h:, half_w:] = resized_images[3]    # Bottom-right

        return mosaic_img

    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(qt_image)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MosaicApp()
    window.show()
    sys.exit(app.exec_())  # This line is essential to keep the application running

   
