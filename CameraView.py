import cv2


class CameraView:
    '''This class is responsible for camera stream'''
    def __init__(self, camera_index=1):
        self.camera_index = camera_index
        self.camera = cv2.VideoCapture(self.camera_index)
        if not self.camera.isOpened():
            raise Exception(f"Error: Could not open camera with index {camera_index}.")

    def get_frame(self):
        '''Get the camera frame and return it'''
        ret, frame = self.camera.read()
        if ret:
            return frame
        return None

    def release(self):
        '''Release the camera'''
        self.camera.release()
