import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
from cameraView import CameraView


class CameraApp(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the CameraView
        self.camera_view = CameraView()

        # Set up the PyQt GUI components
        self.init_ui()

        # Set up a QTimer to update the frame periodically
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30 ms for smooth video

    def init_ui(self):
        self.setFixedSize(680, 480)
        # Create a layout and add widgets
        self.layout = QVBoxLayout()

        # QLabel to display the camera feed
        self.label = QLabel(self)
        self.label.setFixedSize(640, 480)  # Set the QLabel size to match the window
        self.layout.addWidget(self.label)

        # Button to close the app
        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close_app)
        self.layout.addWidget(self.quit_button)

        # Set the layout on the main window
        self.setLayout(self.layout)
        self.setWindowTitle("Camera View")

    def update_frame(self):
        # Get the latest frame from the camera
        frame = self.camera_view.get_frame()

        if frame is not None:
            # Convert the frame to RGB format for QImage
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)

            # Create a QPixmap from QImage and scale it to fit QLabel
            pixmap = QPixmap.fromImage(q_image).scaled(
                self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )

            # Set the QPixmap on the QLabel
            self.label.setPixmap(pixmap)

    def close_app(self):
        # Stop the camera and release resources
        self.camera_view.release()
        self.close()

    def closeEvent(self, event):
        # Make sure to release the camera when the window is closed
        self.camera_view.release()
        event.accept()
