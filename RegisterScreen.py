import sys
import cv2
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox, QHBoxLayout, QStyle
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt

from DatabaseManager import DatabaseManager
from FaceExceptions import NoFaceDetectedException, MultipleFacesDetectedException
from FeatureExtractionThread import FeatureExtractionThread
from UserIdentification import UserIdentification
from CameraApp import CameraApp





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
        self.feature_extraction_thread = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Input fields in one horizontal row, placed above the camera feed
        input_layout = QHBoxLayout()

        # Input field for name
        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Enter Name")
        input_layout.addWidget(self.name_input)

        # Password input with toggle visibility button
        password_layout = QHBoxLayout()
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Enter Safety Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.password_input)

        # Eye button to toggle visibility
        self.show_password_button = QPushButton(self)
        self.show_password_button.setCheckable(True)
        self.update_eye_icon()
        self.show_password_button.setFixedSize(30, 30)
        self.show_password_button.setToolTip("Show/Hide Password")
        self.show_password_button.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.show_password_button)

        input_layout.addLayout(password_layout)

        # Add the input fields row to the main layout
        main_layout.addLayout(input_layout)

        # Add spacing to move the camera feed a little higher
        main_layout.addSpacing(-25)  # Adds a small gap to adjust visual position

        # Camera feed moved a little higher without resizing
        self.camera_view_label = QLabel(self)
        self.camera_view_label.setFixedSize(640, 400)  # Maintain the original size
        self.camera_view_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.camera_view_label)

        # Common button styles with gray theme and hover effect
        button_styles = """
            QPushButton {
                font-size: 18px;
                background-color: #D3D3D3; /* Light Gray */
                color: black;
                border: 1px solid #A9A9A9; /* Dark Gray border */
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #A9A9A9; /* Darker Gray */
                color: white;
            }
            QPushButton:pressed {
                background-color: #808080; /* Even Darker Gray */
                color: white;
            }
        """

        # Buttons in a single horizontal row
        button_layout = QHBoxLayout()

        # Start Camera button
        self.capture_button = QPushButton("Start Camera", self)
        self.capture_button.setStyleSheet(button_styles)
        self.capture_button.clicked.connect(self.toggle_camera_and_capture)
        button_layout.addWidget(self.capture_button)

        # Submit button
        self.submit_button = QPushButton("Submit", self)
        self.submit_button.setStyleSheet(button_styles)
        self.submit_button.clicked.connect(self.submit_data)
        button_layout.addWidget(self.submit_button)

        # Back to Main Screen button
        self.back_button = QPushButton("Back to Main Screen", self)
        self.back_button.setStyleSheet(button_styles)
        self.back_button.clicked.connect(self.go_back)
        button_layout.addWidget(self.back_button)

        # Add all buttons to a horizontal layout
        main_layout.addLayout(button_layout)

        # Set main layout and window title
        self.setLayout(main_layout)
        self.setWindowTitle("Registration Screen")

        # Set up a QTimer to update the camera feed
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera_feed)

    def toggle_password_visibility(self):
        '''Toggle the visibility of the password'''
        if self.show_password_button.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)  # Show password
        else:
            self.password_input.setEchoMode(QLineEdit.Password)  # Hide password
        self.update_eye_icon()  # Update icon based on visibility state

    def update_eye_icon(self):
        '''Updates the eye icon based on password visibility'''
        if self.show_password_button.isChecked():
            icon = self.style().standardIcon(QStyle.SP_ComputerIcon)  # "Visible" icon
        else:
            icon = self.style().standardIcon(QStyle.SP_DialogCloseButton)  # "Hidden" icon
        self.show_password_button.setIcon(icon)

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
        try:
            # Attempt to draw landmarks on the captured frame
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

        except NoFaceDetectedException as e:
            self.captured_frame = None
            QMessageBox.warning(self, "Face Not Found", str(e))
        except MultipleFacesDetectedException as e:
            self.captured_frame = None
            QMessageBox.warning(self, "Multiple Faces Detected", str(e))



    def submit_data(self):
        '''Start the feature extraction in a separate thread or prompt if user exists'''
        name = self.name_input.text()
        password = self.password_input.text()

        if not name or not password:
            QMessageBox.warning(self, "Input Error", "Please fill in both the name and password fields.")
        else:
            # Check if user with this name exists
            existing_user = self.database_manager.user_exists(name)

            if self.captured_frame is None:
                QMessageBox.warning(self, "Error", "No valid face captured. Please capture a photo with a single face.")
                return

            if existing_user:
                # If user exists, verify password
                stored_password, _ = existing_user
                if self.database_manager.verify_password(stored_password, password):
                    # Ask if they want to overwrite data
                    reply = QMessageBox.question(
                        self, 'User Exists',
                        "A user with this name already exists. Do you want to overwrite the data?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply == QMessageBox.Yes:
                        # Overwrite existing user data
                        self.register_user_with_overwrite(name, password)
                    else:
                        QMessageBox.information(self, "Cancelled", "User data was not overwritten.")
                else:
                    # Password mismatch
                    QMessageBox.warning(self, "Error", "Password does not match to the existing user of this name. Please enter correct one to overwrite face data.")
            else:
                # New user, proceed with registration
                self.register_user_without_overwrite(name, password)

    def register_user_with_overwrite(self, name, password):
        '''Register user and overwrite existing data'''
        # Start feature extraction and overwrite data in a separate thread
        self.start_feature_extraction_thread(name, password, overwrite=True)

    def register_user_without_overwrite(self, name, password):
        '''Register user without overwriting'''
        # Start feature extraction without overwrite
        self.start_feature_extraction_thread(name, password, overwrite=False)

    def start_feature_extraction_thread(self, name, password, overwrite):
        '''Initialize and start feature extraction with registration in a thread'''
        if self.captured_frame is not None:
            # Initialize and start the feature extraction thread
            self.feature_extraction_thread = FeatureExtractionThread(
                name, password, self.captured_frame, self.user_identification, overwrite
            )
            self.feature_extraction_thread.extraction_complete.connect(self.on_extraction_complete)
            self.feature_extraction_thread.start()
        else:
            QMessageBox.warning(self, "Error", "No captured photo available. Please capture a photo first.")

    def on_extraction_complete(self, result):
        '''Handle the completion of feature extraction and registration'''
        QMessageBox.information(self, "Registration", result)
        self.feature_extraction_thread = None  # Clean up the thread
        self.captured_frame = None  # Reset the captured frame after submission
        self.go_back()  # Return to the main screen after submission

    def showEvent(self, event):
        '''Start the camera when the screen is shown'''
        self.start_camera()
        self.name_input.clear()
        self.password_input.clear()
        super().showEvent(event)

    def hideEvent(self, event):
        '''Stop the camera when the screen is hidden'''
        self.stop_camera()
        super().hideEvent(event)

    def go_back(self):
        '''This method goes back to the start screen'''
        self.stacked_widget.setCurrentIndex(0)
