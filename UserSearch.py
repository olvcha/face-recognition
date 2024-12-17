import numpy as np
from scipy.spatial.distance import euclidean
from DatabaseManager import DatabaseManager
from UserIdentification import UserIdentification


class UserSearch:
    '''Handles user search operations and identification.'''

    def __init__(self, image):
        self.db_manager = DatabaseManager()
        self.user_identification = UserIdentification()
        user_vector = ",".join(map(str, self.user_identification.extract_feature_vector(image)))
        self.nearest_user = self.find_nearest_user(user_vector)

    def find_nearest_user(self, feature_vector):
        '''
            Finds the nearest user according to the feature vector.
            :param feature_vector: feature vector of the current user
            :return closest matched user and the distance between theirs feature vectors
        '''

        all_users = self.db_manager.get_all_users()
        min_distance = float(999999999)
        closest_user = None

        #print("twoj wektor", feature_vector)

        for user in all_users:
            user_feature_vector = user[2]
            print('to juser', user)
            distance = self.calculate_euclidean_distance(feature_vector, user_feature_vector)
            print('to dystans', distance)
            if distance < min_distance:
                min_distance = distance
                closest_user = user

        if min_distance < 11:
            print("najlepsze dopasowanie", closest_user)
            print("odleglosc", min_distance)
            return closest_user, min_distance
        else:
            return None

    def calculate_euclidean_distance(self, vector_str1, vector_str2):
        '''
            Calculates the Euclidean distance between two vectors represented as strings.
            :param vector_str1: first vector
            :param vector_str2: second vector
            :return: Euclidean distance between two vectors
        '''
        # Convert data
        vector1 = np.array([float(x) for x in vector_str1.split(",")])
        vector2 = np.array([float(x) for x in vector_str2.split(",")])

        # Check the vectors
        if vector1.shape != vector2.shape:
            raise ValueError("Vectors are not the same size.")

        # Calculate euclidean distance
        distance = np.sqrt(np.sum((vector1 - vector2) ** 2))

        return distance

    def get_nearest_user(self):
        return self.nearest_user


