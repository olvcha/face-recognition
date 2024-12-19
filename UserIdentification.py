from itertools import combinations

import cv2
import dlib
import numpy as np

from DatabaseManager import DatabaseManager
from RegisterScreen import NoFaceDetectedException, MultipleFacesDetectedException


class UserIdentification:
    '''Handles facial recognition and identification using Dlib landmarks'''

    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        self.db_manager = DatabaseManager()

    def preprocess_image(self, image):
        '''Preprocesses the image for landmark detection'''
        height, width = image.shape[:2]
        max_dimension = 800
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            image = cv2.resize(image, (int(width * scale), int(height * scale)))

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return gray

    def extract_feature_vector(self, image):
        '''Extracts an extended facial feature vector based on normalized landmark distances and angles'''
        gray = self.preprocess_image(image)

        faces = self.detector(gray)
        if len(faces) == 0:
            raise NoFaceDetectedException("No faces detected.")
        elif len(faces) > 1:
            raise MultipleFacesDetectedException("Multiple faces detected.")

        face = faces[0]
        landmarks = self.predictor(gray, face)

        def euclidean_distance(point1, point2):
            return np.linalg.norm(np.array(point1) - np.array(point2))

        def calculate_angle(pointA, pointB, pointC):
            BA = np.array(pointA) - np.array(pointB)
            BC = np.array(pointC) - np.array(pointB)
            cosine_angle = np.dot(BA, BC) / (np.linalg.norm(BA) * np.linalg.norm(BC))
            angle = np.arccos(cosine_angle)
            return np.degrees(angle)

        feature_vector = []

        selected_points = [
            1, 2, 3, 4, 5,  # Jawline points
            36, 39,  # Left eye corners
            42, 45,  # Right eye corners
            31, 35,  # Nose width
            48, 54,  # Mouth corners
            57, 8,  # Bottom of lower lip and chin
            17, 26,  # Left and right eyebrows
            19, 24  # Center points of left and right eyebrows
        ]

        left_eye_point = (landmarks.part(36).x, landmarks.part(36).y)
        right_eye_point = (landmarks.part(45).x, landmarks.part(45).y)
        reference_distance = euclidean_distance(left_eye_point, right_eye_point)

        for i, j in combinations(selected_points, 2):
            point1 = (landmarks.part(i).x, landmarks.part(i).y)
            point2 = (landmarks.part(j).x, landmarks.part(j).y)
            distance = euclidean_distance(point1, point2)
            normalized_distance = distance / reference_distance
            feature_vector.append(normalized_distance)

        angle_triplets = [
            (36, 39, 42),  # Left eye region
            (42, 45, 36),  # Right eye region
            (31, 30, 35),  # Nose region
            (48, 51, 54),  # Mouth region
            (0, 8, 16)  # Chin-jawline region
        ]

        for (a, b, c) in angle_triplets:
            pointA = (landmarks.part(a).x, landmarks.part(a).y)
            pointB = (landmarks.part(b).x, landmarks.part(b).y)
            pointC = (landmarks.part(c).x, landmarks.part(c).y)
            angle = calculate_angle(pointA, pointB, pointC)
            feature_vector.append(angle)

        return feature_vector

    def draw_landmarks(self, frame):
        '''Detects landmarks on a single frame and returns the frame with landmarks'''
        gray = self.preprocess_image(frame)
        faces = self.detector(gray)

        if len(faces) == 0:
            raise NoFaceDetectedException("No faces detected.")
        elif len(faces) > 1:
            raise MultipleFacesDetectedException("Multiple faces detected.")

        landmarks = self.predictor(gray, faces[0])
        for n in range(68):
            x = landmarks.part(n).x
            y = landmarks.part(n).y
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
        return frame
