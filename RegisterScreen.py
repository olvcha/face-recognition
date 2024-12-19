import cv2
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox, QHBoxLayout, QStyle

from CameraApp import CameraApp
from DatabaseManager import DatabaseManager
from FaceExceptions import NoFaceDetectedException, MultipleFacesDetectedException
from FeatureExtractionThread import FeatureExtractionThread
from UserIdentification import UserIdentification


class RegisterScreen(QWidget):
    '''This class is responsible for displaying the registration screen'''

    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.camera_app = CameraApp(self.stacked_widget)
        self.user_identification = UserIdentification()
        self.is_camera_running = False
        self.database_manager = DatabaseManager()
        self.captured_frame = None
        self.feature_extraction_thread = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        input_layout = QHBoxLayout()

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Enter Name")
        input_layout.addWidget(self.name_input)

        password_layout = QHBoxLayout()
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Enter Safety Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.password_input)

        self.show_password_button = QPushButton(self)
        self.show_password_button.setCheckable(True)
        self.update_eye_icon()
        self.show_password_button.setFixedSize(30, 30)
        self.show_password_button.setToolTip("Show/Hide Password")
        self.show_password_button.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.show_password_button)

        input_layout.addLayout(password_layout)

        main_layout.addLayout(input_layout)

        self.camera_view_label = QLabel(self)
        self.camera_view_label.setFixedSize(640, 400)
        self.camera_view_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.camera_view_label)

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

        button_layout = QHBoxLayout()

        self.capture_button = QPushButton("Start Camera", self)
        self.capture_button.setStyleSheet(button_styles)
        self.capture_button.clicked.connect(self.toggle_camera_and_capture)
        button_layout.addWidget(self.capture_button)

        self.submit_button = QPushButton("Submit", self)
        self.submit_button.setStyleSheet(button_styles)
        self.submit_button.clicked.connect(self.submit_data)
        button_layout.addWidget(self.submit_button)

        self.back_button = QPushButton("Back to Main Screen", self)
        self.back_button.setStyleSheet(button_styles)
        self.back_button.clicked.connect(self.go_back)
        button_layout.addWidget(self.back_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.setWindowTitle("Registration Screen")

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera_feed)

    def toggle_password_visibility(self):
        '''Toggle the visibility of the password'''
        if self.show_password_button.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
        self.update_eye_icon()

    def update_eye_icon(self):
        '''Updates the eye icon based on password visibility'''
        if self.show_password_button.isChecked():
            icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
        else:
            icon = self.style().standardIcon(QStyle.SP_DialogCloseButton)
        self.show_password_button.setIcon(icon)

    def start_camera(self):
        '''Start the camera feed and timer'''
        self.camera_app.start_camera()
        self.timer.start(30)
        self.is_camera_running = True
        self.capture_button.setText("Capture Photo")

    def stop_camera(self):
        '''Stop the camera feed and timer completely'''
        self.timer.stop()
        if self.timer.isActive():
            self.timer.timeout.disconnect(self.update_camera_feed)
        self.camera_app.stop_camera()
        self.is_camera_running = False
        self.capture_button.setText("Start Camera")

    def update_camera_feed(self):
        '''Continuously update the camera feed in the QLabel if the camera is running'''
        if not self.is_camera_running:
            return

        frame = self.camera_app.capture_frame()
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
            self.start_camera()
        else:
            frame = self.camera_app.capture_frame()
            if frame is not None:
                self.stop_camera()
                self.process_captured_frame(frame)
                QMessageBox.information(self, "Success", "Photo captured successfully!")

    def process_captured_frame(self, frame):
        '''Processes the captured frame to display landmarks and store for further processing'''
        try:
            image_with_landmarks = self.user_identification.draw_landmarks(frame)

            height, width, channel = image_with_landmarks.shape
            bytes_per_line = channel * width
            q_img = QImage(image_with_landmarks.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            self.camera_view_label.setPixmap(pixmap.scaled(
                self.camera_view_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))

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
            existing_user = self.database_manager.user_exists(name)

            if self.captured_frame is None:
                QMessageBox.warning(self, "Error", "No valid face captured. Please capture a photo with a single face.")
                return

            if existing_user:
                stored_password, _ = existing_user
                if self.database_manager.verify_password(stored_password, password):
                    reply = QMessageBox.question(
                        self, 'User Exists',
                        "A user with this name already exists. Do you want to overwrite the data?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply == QMessageBox.Yes:
                        self.register_user_with_overwrite(name, password)
                    else:
                        QMessageBox.information(self, "Cancelled", "User data was not overwritten.")
                else:
                    QMessageBox.warning(self, "Error",
                                        "Password does not match to the existing user of this name. Please enter correct one to overwrite face data.")
            else:
                self.register_user_without_overwrite(name, password)

    def register_user_with_overwrite(self, name, password):
        '''Register user and overwrite existing data'''
        self.start_feature_extraction_thread(name, password, overwrite=True)

    def register_user_without_overwrite(self, name, password):
        '''Register user without overwriting'''
        self.start_feature_extraction_thread(name, password, overwrite=False)

    def start_feature_extraction_thread(self, name, password, overwrite):
        '''Initialize and start feature extraction with registration in a thread'''
        if self.captured_frame is not None:
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
        self.feature_extraction_thread = None
        self.captured_frame = None
        self.go_back()

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
