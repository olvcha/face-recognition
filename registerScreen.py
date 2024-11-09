from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton


class RegisterScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel("Registration Screen", self)
        layout.addWidget(self.label)

        self.back_button = QPushButton("Back to Main Screen", self)
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def go_back(self):
        # Switch back to the main window (index 0 in the stacked widget)
        self.stacked_widget.setCurrentIndex(0)