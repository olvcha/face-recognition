import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget
from startScreen import StartScreen

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create the main stacked widget
    stacked_widget = QStackedWidget()

    # Create instance of MainWindow and set it in the stacked widget
    main_window = StartScreen(stacked_widget)
    stacked_widget.addWidget(main_window)  # Index 0 for main window

    # Set the initial screen to the main window
    stacked_widget.setCurrentIndex(0)
    stacked_widget.setFixedSize(640, 480)
    stacked_widget.setWindowTitle("Face Recognition App")
    stacked_widget.show()

    sys.exit(app.exec_())
