from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox

from cameraApp import CameraApp


class RegisterScreen(QWidget):
    '''This class is responsible for displaying the registration screen'''
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.camera_app = CameraApp(stacked_widget)
        self.init_ui()

    def init_ui(self):
        '''Initializes the UI components'''
        layout = QVBoxLayout()

        # Input fields for name and surname
        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Enter Name")
        layout.addWidget(self.name_input)

        self.surname_input = QLineEdit(self)
        self.surname_input.setPlaceholderText("Enter Surname")
        layout.addWidget(self.surname_input)

        # Submit button
        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(self.submit_data)
        layout.addWidget(self.submit_button)

        # Back to Main Screen button
        self.back_button = QPushButton("Back to Main Screen", self)
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        # Camera view (using CameraApp instance)
        layout.addWidget(self.camera_app.label)  # Add the label from CameraApp for displaying the camera feed

        # Capture button
        self.capture_button = QPushButton("Capture Photo", self)
        self.capture_button.clicked.connect(self.capture_photo)
        layout.addWidget(self.capture_button)

        self.setLayout(layout)

    def start_camera(self):
        '''Initialize and start the camera view using CameraApp'''
        self.camera_app.start_camera()

    def stop_camera(self):
        '''Stop the camera'''
        self.camera_app.stop_camera()

    def capture_photo(self):
        '''Capture the current camera frame and show a popup with the result'''
        try:
            frame = self.camera_app.capture_frame()
            if frame is not None:
                # Display success message
                QMessageBox.information(self, "Success", "Photo captured successfully!")
                return frame
            else:
                # Display error message if no frame is captured
                QMessageBox.warning(self, "Error", "Failed to capture photo.")
        except Exception as e:
            # Display error message with exception details
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
        return None

    def submit_data(self):
        '''Collect and submit name, surname, and captured photo for further processing, then return to main screen'''
        name = self.name_input.text()
        surname = self.surname_input.text()
        photo = self.capture_photo()

        if photo is not None:
            # Here you can handle the collected data (e.g., save or send it somewhere)
            print(f"Name: {name}, Surname: {surname}")
            # Immediately go back to the main screen after successful submission
            self.go_back()

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