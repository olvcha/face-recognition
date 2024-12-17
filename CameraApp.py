import sys
import cv2
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QMessageBox, QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
from CameraView import CameraView

from UserSearch import UserSearch
from AfterAuthorizationScreen import AfterAuthorizationScreen

class CameraApp(QWidget):
    '''This class is responsible for displaying the camera window'''
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.camera_view = None

        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

    def init_ui(self):
        '''Initialize the UI with gray-styled buttons side by side.'''
        self.setFixedSize(680, 480)

        # Main layout
        self.layout = QVBoxLayout()

        # Label for displaying camera feed
        self.label = QLabel(self)
        self.label.setFixedSize(640, 400)  # Adjusted height to move it higher
        self.layout.addWidget(self.label, alignment=Qt.AlignCenter)

        # Horizontal layout for buttons
        button_layout = QHBoxLayout()

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

        # Back to Main Screen button
        self.back_button = QPushButton("Back to Main Screen", self)
        self.back_button.setStyleSheet(button_styles)
        self.back_button.clicked.connect(self.go_back)
        button_layout.addWidget(self.back_button)

        # Authorize button
        self.authorize_button = QPushButton("Authorize", self)
        self.authorize_button.setStyleSheet(button_styles)
        self.authorize_button.clicked.connect(self.authorize)
        button_layout.addWidget(self.authorize_button)

        # Add the button layout to the main layout
        self.layout.addLayout(button_layout)

        # Set the layout and window title
        self.setLayout(self.layout)
        self.setWindowTitle("Camera View")

    def start_camera(self):
        '''Initialize the camera after switching to this screen'''
        if self.camera_view is None:
            self.camera_view = CameraView()
            self.timer.start(30)

    def stop_camera(self):
        '''Stop the camera'''
        if self.camera_view is not None:
            self.camera_view.release()
            self.camera_view = None
            self.timer.stop()  # Stop the timer to stop updating frames

    def update_frame(self):
        '''Ensure that the camera is valid before trying to read a frame'''
        if self.camera_view is None:
            return

        frame = self.camera_view.get_frame()
        if frame is not None:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)

            pixmap = QPixmap.fromImage(q_image).scaled(
                self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )

            self.label.setPixmap(pixmap)

    def capture_frame(self):
        '''Capture and return the current frame'''
        if self.camera_view:
            return self.camera_view.get_frame()
        return None

    def go_back(self):
        '''Stop the camera and switch back to the main screen'''
        self.stop_camera()
        self.stacked_widget.setCurrentIndex(0)

    from PyQt5.QtWidgets import QMessageBox

    def authorize(self):
        try:
            image = self.capture_frame()
            if image is not None:
                user_search = UserSearch(image)
                user = user_search.get_nearest_user()
                if user:
                    print("jestes w bazie", user)
                    username = user[0][1]
                    # Switch to AuthorizationScreen
                    self.stacked_widget.authorization_screen = AfterAuthorizationScreen(self.stacked_widget, username)
                    self.stacked_widget.addWidget(self.stacked_widget.authorization_screen)
                    self.stacked_widget.setCurrentWidget(self.stacked_widget.authorization_screen)
                else:
                    print("nie ma cie xddd")
                    # Show a QMessageBox with "nie ma cie" text
                    QMessageBox.warning(self, "Authorization Failed", "Authorization denied. Please try again.")
        except Exception as e:
            print("Exception: ", e)
            # Show a QMessageBox with the exception text
            QMessageBox.critical(self, "Error", f"An error has occured: {e}")

    def showEvent(self, event):
        '''Called when the widget with camera is being shown, starts the camera'''
        self.start_camera()
        super().showEvent(event)

    def hideEvent(self, event):
        '''Called when the widget is hidden, stops the camera'''
        self.stop_camera()
        super().hideEvent(event)

    def closeEvent(self, event):
        '''Ensure the camera is released when the window is closed'''
        self.stop_camera()
        event.accept()
