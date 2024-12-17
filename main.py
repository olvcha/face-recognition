import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget
from StartScreen import StartScreen

if __name__ == "__main__":
    app = QApplication(sys.argv)

    stacked_widget = QStackedWidget()

    main_window = StartScreen(stacked_widget)
    stacked_widget.addWidget(main_window)

    # Initial screen to the main window
    stacked_widget.setCurrentIndex(0)
    stacked_widget.setFixedSize(680, 480)
    stacked_widget.setWindowTitle("Face Recognition App")
    stacked_widget.show()

    sys.exit(app.exec_())
