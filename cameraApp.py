import sys
import cv2
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
from cameraView import CameraView

class CameraApp(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.camera_view = None  # Initially, no camera is open

        # Set up the PyQt GUI components
        self.init_ui()

        # Set up a QTimer for updating the frame periodically, but don't start it yet
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

    def init_ui(self):
        self.setFixedSize(680, 480)

        # Create layout and widgets
        self.layout = QVBoxLayout()

        # QLabel to display the camera feed
        self.label = QLabel(self)
        self.label.setFixedSize(640, 480)
        self.layout.addWidget(self.label)

        # Back button
        self.back_button = QPushButton("Back to Main Screen", self)
        self.back_button.clicked.connect(self.go_back)
        self.layout.addWidget(self.back_button)

        # Set the layout on the main window
        self.setLayout(self.layout)
        self.setWindowTitle("Camera View")

    def start_camera(self):
        # Initialize the camera when switching to this screen
        if self.camera_view is None:
            self.camera_view = CameraView()
            self.timer.start(30)  # Start the timer to update frames every 30 ms

    def stop_camera(self):
        # Release the camera when leaving this screen
        if self.camera_view is not None:
            self.camera_view.release()
            self.camera_view = None
            self.timer.stop()  # Stop the timer to stop updating frames

    def update_frame(self):
        # Ensure that we have a valid camera before trying to read a frame
        if self.camera_view is None:
            return

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

    def go_back(self):
        # Stop the camera and switch back to the main screen
        self.stop_camera()
        self.stacked_widget.setCurrentIndex(0)

    def showEvent(self, event):
        # Called when the widget is shown, start the camera
        self.start_camera()
        super().showEvent(event)

    def hideEvent(self, event):
        # Called when the widget is hidden, stop the camera
        self.stop_camera()
        super().hideEvent(event)

    def closeEvent(self, event):
        # Ensure the camera is released when the window is closed
        self.stop_camera()
        event.accept()
