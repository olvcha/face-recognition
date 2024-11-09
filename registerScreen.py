import cv2
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox

from DatabaseManager import DatabaseManager
from UserIdentification import UserIdentification
from cameraApp import CameraApp


class RegisterScreen(QWidget):
    '''This class is responsible for displaying the registration screen'''

    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.camera_app = CameraApp(self.stacked_widget)
        self.user_identification = UserIdentification()
        self.is_camera_running = False
        self.database_manager = DatabaseManager()
        self.captured_frame = None  # Store captured photo for further processing
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Input fields for name and surname
        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Enter Name")
        layout.addWidget(self.name_input)

        self.surname_input = QLineEdit(self)
        self.surname_input.setPlaceholderText("Enter Surname")
        layout.addWidget(self.surname_input)

        # Camera view for displaying live feed or captured photo
        self.camera_view_label = QLabel(self)
        self.camera_view_label.setFixedSize(640, 480)
        layout.addWidget(self.camera_view_label)

        # Capture button
        self.capture_button = QPushButton("Start Camera", self)
        self.capture_button.clicked.connect(self.toggle_camera_and_capture)
        layout.addWidget(self.capture_button)

        # Submit button
        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(self.submit_data)
        layout.addWidget(self.submit_button)

        # Back to Main Screen button
        self.back_button = QPushButton("Back to Main Screen", self)
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

        # Set up a QTimer to update the camera feed
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera_feed)  # Connect the timer to update the camera feed

    def start_camera(self):
        '''Start the camera feed and timer'''
        self.camera_app.start_camera()
        self.timer.start(30)  # Update the feed every 30ms for smooth streaming
        self.is_camera_running = True
        self.capture_button.setText("Capture Photo")

    def stop_camera(self):
        '''Stop the camera feed and timer completely'''
        self.timer.stop()
        if self.timer.isActive():
            self.timer.timeout.disconnect(self.update_camera_feed)  # Disconnect the camera feed update
        self.camera_app.stop_camera()
        self.is_camera_running = False
        self.capture_button.setText("Start Camera")

    def update_camera_feed(self):
        '''Continuously update the camera feed in the QLabel if the camera is running'''
        if not self.is_camera_running:
            return  # Only update if the camera is running

        frame = self.camera_app.capture_frame()  # Capture current frame for live feed
        if frame is not None:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.camera_view_label.setPixmap(pixmap.scaled(
                self.camera_view_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))

    def toggle_camera_and_capture(self):
        '''Toggles the camera feed on/off and captures a photo if the camera is running'''
        if not self.is_camera_running:
            # Start the camera if it is not running
            self.start_camera()
        else:
            # Stop the camera, capture the photo, and display landmarks
            frame = self.camera_app.capture_frame()
            if frame is not None:
                self.stop_camera()  # Stop camera and timer
                self.process_captured_frame(frame)
                QMessageBox.information(self, "Success", "Photo captured successfully!")

    def process_captured_frame(self, frame):
        '''Processes the captured frame to display landmarks and store for further processing'''
        # Draw landmarks on the captured frame
        image_with_landmarks = self.user_identification.draw_landmarks(frame)

        # Display the image with landmarks in the QLabel
        height, width, channel = image_with_landmarks.shape
        bytes_per_line = channel * width
        q_img = QImage(image_with_landmarks.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        self.camera_view_label.setPixmap(pixmap.scaled(
            self.camera_view_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))

        # Store the captured frame for further processing
        self.captured_frame = frame

    def submit_data(self):
        '''Processes the last captured photo, calculates feature vector, and saves to database'''
        name = self.name_input.text()
        surname = self.surname_input.text()

        # Check if there is a captured frame
        if self.captured_frame is not None:
            # Extract the feature vector (distances and angles) from the captured frame
            feature_vector = self.user_identification.extract_feature_vector(self.captured_frame)

            if feature_vector:
                # Convert feature vector to a string for database storage
                feature_vector_str = ",".join(map(str, feature_vector))

                # Save to database
                result = self.database_manager.register_user(name, surname, feature_vector_str)
                success_msg = QMessageBox(self)
                success_msg.setIcon(QMessageBox.Information)
                success_msg.setWindowTitle("Registration")
                success_msg.setText(result)
                success_msg.setStandardButtons(QMessageBox.Ok)

                # Connect the OK button to go back to the main page
                success_msg.buttonClicked.connect(self.go_back)

                # Display the message box
                success_msg.exec_()

                # Clear captured frame after successful submission
                self.captured_frame = None
            else:
                QMessageBox.warning(self, "Error", "Unable to detect face or calculate feature vector.")
        else:
            QMessageBox.warning(self, "Error", "No captured photo available. Please capture a photo first.")

    def showEvent(self, event):
        '''Start the camera when the screen is shown'''
        self.start_camera()
        super().showEvent(event)

    def hideEvent(self, event):
        '''Stop the camera when the screen is hidden'''
        self.stop_camera()
        super().hideEvent(event)

    def go_back(self):
        '''This method goes back to the start screen'''
        self.stacked_widget.setCurrentIndex(0)
