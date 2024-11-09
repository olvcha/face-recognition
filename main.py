import sys

from PyQt5.QtWidgets import QApplication

from cameraApp import CameraApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraApp()
    window.show()
    sys.exit(app.exec_())