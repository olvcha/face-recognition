from PyQt5.QtCore import QThread, pyqtSignal

from DatabaseManager import DatabaseManager


class FeatureExtractionThread(QThread):
    extraction_complete = pyqtSignal(str)

    def __init__(self, name, password, captured_frame, user_identification, overwrite):
        super().__init__()
        self.name = name
        self.password = password
        self.captured_frame = captured_frame
        self.user_identification = user_identification
        self.db_manager = DatabaseManager()
        self.overwrite= overwrite

    def run(self):
        '''Extract feature vector and save to database'''
        try:
            feature_vector = self.user_identification.extract_feature_vector(self.captured_frame)
            if not feature_vector:
                self.extraction_complete.emit("Error: Unable to detect face or extract features.")
                return

            feature_vector_str = ",".join(map(str, feature_vector))
            result = self.db_manager.register_user(self.name, self.password, feature_vector_str, self.overwrite)

            if result:
                self.extraction_complete.emit(f"User {self.name} registered successfully!")
            else:
                self.extraction_complete.emit("Error: Failed to save user data to database.")

        except Exception as e:
            self.extraction_complete.emit(f"Error during feature extraction or database save: {e}")
