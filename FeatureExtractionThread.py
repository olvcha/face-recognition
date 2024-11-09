from PyQt5.QtCore import QThread, pyqtSignal

from DatabaseManager import DatabaseManager


class FeatureExtractionThread(QThread):
    extraction_complete = pyqtSignal(str)  # Signal to notify when extraction and saving are complete

    def __init__(self, name, surname, captured_frame, user_identification):
        super().__init__()
        self.name = name
        self.surname = surname
        self.captured_frame = captured_frame
        self.user_identification = user_identification
        self.db_manager = DatabaseManager()  # Initialize DatabaseManager here to ensure connection is fresh

    def run(self):
        '''Extract feature vector and save to database'''
        try:
            # Step 1: Extract feature vector from the captured frame
            feature_vector = self.user_identification.extract_feature_vector(self.captured_frame)
            if not feature_vector:
                self.extraction_complete.emit("Error: Unable to detect face or extract features.")
                return

            # Step 2: Save to database
            # Convert feature vector to a string format (or appropriate format for database storage)
            feature_vector_str = ",".join(map(str, feature_vector))
            result = self.db_manager.register_user(self.name, self.surname, feature_vector_str)

            # Emit success message if saved correctly
            if result:
                self.extraction_complete.emit(f"User {self.name} {self.surname} registered successfully!")
            else:
                self.extraction_complete.emit("Error: Failed to save user data to database.")

        except Exception as e:
            self.extraction_complete.emit(f"Error during feature extraction or database save: {e}")
