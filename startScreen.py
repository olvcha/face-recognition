from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from registerScreen import RegisterScreen
from cameraApp import CameraApp

class StartScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("Welcome to our Face Recognition App", self)
        layout.addWidget(self.label)

        self.register_button = QPushButton("Register", self)
        self.register_button.clicked.connect(self.show_register)
        layout.addWidget(self.register_button)

        self.authorize_button = QPushButton("Authorize", self)
        self.authorize_button.clicked.connect(self.show_authorize)
        layout.addWidget(self.authorize_button)

        self.setLayout(layout)

    def show_register(self):
        if not hasattr(self.stacked_widget, 'register_window'):
            self.stacked_widget.register_window = RegisterScreen(self.stacked_widget)
            self.stacked_widget.addWidget(self.stacked_widget.register_window)
        self.stacked_widget.setCurrentWidget(self.stacked_widget.register_window)

    def show_authorize(self):
        if not hasattr(self.stacked_widget, 'camera_app'):
            self.stacked_widget.camera_app = CameraApp(self.stacked_widget)
            self.stacked_widget.addWidget(self.stacked_widget.camera_app)
        self.stacked_widget.setCurrentWidget(self.stacked_widget.camera_app)