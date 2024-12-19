from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

from CameraApp import CameraApp
from RegisterScreen import RegisterScreen


class StartScreen(QWidget):
    '''This class is responsible for displaying the start screen'''

    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()

    def init_ui(self):
        '''This method initializes the UI'''
        layout = QVBoxLayout()

        self.label = QLabel("Welcome to our Face Recognition App", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

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

        self.register_button = QPushButton("Register", self)
        self.register_button.setStyleSheet(button_styles)
        self.register_button.clicked.connect(self.show_register)
        layout.addWidget(self.register_button, alignment=Qt.AlignCenter)

        self.authorize_button = QPushButton("Authorize", self)
        self.authorize_button.setStyleSheet(button_styles)
        self.authorize_button.clicked.connect(self.show_authorize)
        layout.addWidget(self.authorize_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def show_register(self):
        '''This method switches to the registration screen'''
        if not hasattr(self.stacked_widget, 'register_window'):
            self.stacked_widget.register_window = RegisterScreen(self.stacked_widget)
            self.stacked_widget.addWidget(self.stacked_widget.register_window)
        self.stacked_widget.setCurrentWidget(self.stacked_widget.register_window)

    def show_authorize(self):
        '''This method switches to the authorization screen'''
        if not hasattr(self.stacked_widget, 'camera_app'):
            self.stacked_widget.camera_app = CameraApp(self.stacked_widget)
            self.stacked_widget.addWidget(self.stacked_widget.camera_app)
        self.stacked_widget.setCurrentWidget(self.stacked_widget.camera_app)
