from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt

class AfterAuthorizationScreen(QWidget):
    '''This class represents the screen displayed upon successful authorization.'''
    def __init__(self, stacked_widget, username):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.username = username
        self.init_ui()

    def init_ui(self):
        '''Initialize the layout and widgets for the authorization screen.'''
        self.setFixedSize(680, 480)
        self.layout = QVBoxLayout()

        # Reduce spacing between widgets
        self.layout.setSpacing(10)  # Adjust spacing as needed

        # Authorization successful label
        self.message_label = QLabel("Authorization Successful!", self)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.layout.addWidget(self.message_label, alignment=Qt.AlignCenter)

        # Welcome label
        self.username_label = QLabel(f"Welcome, {self.username}", self)
        self.username_label.setAlignment(Qt.AlignCenter)
        self.username_label.setStyleSheet("font-size: 15px;")
        self.layout.addWidget(self.username_label, alignment=Qt.AlignCenter)

        # Back button
        self.back_button = QPushButton("Back to Main Screen", self)
        self.back_button.clicked.connect(self.go_back)
        self.layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

        # Set layout for the window
        self.setLayout(self.layout)
        self.setWindowTitle("Authorization Screen")

    def go_back(self):
        '''Switch back to the main screen.'''
        self.stacked_widget.setCurrentIndex(0)
