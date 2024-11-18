import sys
import cv2
from ultralytics import YOLO
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSlider, 
    QComboBox, QPushButton, QCheckBox, QLineEdit, QGroupBox
)
from PyQt5.QtGui import QPixmap, QColor,QIcon,QImage
from PyQt5.QtCore import Qt,QTimer
from supporting.camera_output import capture_one_frame
from supporting.circular_progress_bar import CircularProgressBar

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
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 0, 10, 0)  # Remove top and bottom margins
        main_layout.setSpacing(5)  # Minimal spacing between sections
        
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
        leftpanel_box = QGroupBox()
        leftpanel_box.setFixedSize(320,820 )
        leftpanel_box.setStyleSheet("QGroupBox { background-color: rgb(220, 255, 229); }")
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)
        
        # Object Color Setting
        color_setting_group = QGroupBox("Camera Setting")
        color_setting_group.setFixedSize(300, 100)
        color_setting_layout = QVBoxLayout()
        color_setting_layout.setContentsMargins(10, 10, 10, 10)
        color_setting_layout.setSpacing(5)
        
        kernel_label = QLabel("Brightness")
        kernel_slider = QSlider(Qt.Horizontal)
        kernel_slider.setRange(0, 100)
        kernel_slider.setFixedSize(180, 20)
        
        color_setting_layout.addWidget(kernel_label)
        color_setting_layout.addWidget(kernel_slider)
        color_setting_group.setLayout(color_setting_layout)
        
        # HSV Setting
        hsv_group = QGroupBox("HSV Setting")
        hsv_group.setFixedSize(300, 150)
        hsv_layout = QVBoxLayout()
        hsv_layout.setContentsMargins(10, 10, 10, 10)
        hsv_layout.setSpacing(5)
        
        hsv_max_h = QSlider(Qt.Horizontal)
        hsv_max_h.setFixedSize(180, 20)
        hsv_max_s = QSlider(Qt.Horizontal)
        hsv_max_s.setFixedSize(180, 20)
        hsv_max_v = QSlider(Qt.Horizontal)
        hsv_max_v.setFixedSize(180, 20)
        hsv_max_h.setValue(180)
        hsv_max_s.setValue(255)
        hsv_max_v.setValue(255)
        
        hsv_layout.addWidget(hsv_max_h)
        hsv_layout.addWidget(hsv_max_s)
        hsv_layout.addWidget(hsv_max_v)
        hsv_group.setLayout(hsv_layout)
        
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
        left_panel.addWidget(color_setting_group)
        left_panel.addWidget(hsv_group)
        left_panel.addWidget(set_area_group)
        left_panel.addWidget(target_group)
        leftpanel_box.setLayout(left_panel)
        
        # Right panel
        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)
        
        # Image container
        image_container = QLabel("Camera")
        image_container.setFixedSize(640, 480)
        image_container.setStyleSheet("border: 3px solid #6495ED; background-color: #FFFFFF;")
        
        stackx = []
        stacky = []
        while(1):
            if(len(stackx) == 0 and len(stacky) == 0):
                image_container.setPixmap(update_frame(stackx,stacky))
            else:
                print("Stack:","X",stackx.pop(),"Y:",stacky.pop()) 
        # Counter
        counter_box = QGroupBox("Counter")
        counter_box.setFixedSize(640, 220)
        counter_layout = QHBoxLayout()
        counter_layout.setSpacing(10)
        counter_layout.setContentsMargins(10, 10, 10, 10)
        
        self.progress_bar_counter = CircularProgressBar(max_value=100, label_text="Total Target")
        self.progress_bar_remaining = CircularProgressBar(max_value=100, label_text="Completion")
        self.progress_bar_counter.setValue(28)
        self.progress_bar_remaining.setValue(75)
        self.progress_bar_remaining.setProgressColor(QColor(0, 204, 0))
        
        counter_layout.addWidget(self.progress_bar_counter)
        counter_layout.addWidget(self.progress_bar_remaining)
        counter_box.setLayout(counter_layout)
        

        # Status section
        status_box = QLabel("0: 480x640 48 weeds, 2 crops, 46.5ms\n"
                            "Speed: 1.0ms preprocess, 46.5ms inference, 1.0ms postprocess per image at shape (1, 3, 480, 640)")
        status_box.setFixedSize(640, 150)
        status_box.setStyleSheet("background-color: #e0e0e0; border: 1px solid #ccc; ")


        right_panel.addWidget(image_container)
        right_panel.addStretch()
        right_panel.addWidget(counter_box)
        right_panel.addWidget(status_box)

        # Combine left and right panel
        main_panel_layout = QHBoxLayout()
        main_panel_layout.addWidget(leftpanel_box)
        main_panel_layout.addLayout(right_panel)
        
        # Add all sections to main layout
        main_layout.addLayout(header_layout)
        main_layout.addStretch()
        main_layout.addLayout(main_panel_layout)
        
        self.setLayout(main_layout)

#function that detects crops and weed and returns annotated image
def update_frame(stack1,stack2):
        
    model = YOLO('june8.pt') 
    threshold = 0
    # Load an image
    frame = capture_one_frame()
    # Predict the image
    results = model(frame)[0]

    for result in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = result
        detection_color= (204, 0, 0) if int(class_id)==0 else (0, 0, 255)
        if score > threshold:
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), detection_color, 2)
            cv2.putText(frame, results.names[int(class_id)].upper(), (int(x1), int(y1 - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, .5, detection_color, 2, cv2.LINE_4)
            print('cordinates',x1,y1,x2,y2)

            #calculating the scaling constant
            x=int((x1+x2)//2)
            y=int((y1+y2)//2)
            print(results.names,'cordinates',x,y)
            # Push elements to the stack
            stack1.append(x)
            stack2.append(y)

    annotated_frame = frame

    # Convert the annotated frame to QImage for display in QLabel
    height, width, channel = annotated_frame.shape
    bytes_per_line = 3 * width
    q_img = QImage(annotated_frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
    pixmap = QPixmap(q_img)
    scaled_pixmap = pixmap.scaled(640, 480)

    return scaled_pixmap
    

        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = USRControlSoftware()
    window.show()
    sys.exit(app.exec_())
