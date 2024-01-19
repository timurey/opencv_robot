import cv2


class Camera:
    def __init__(self, stereo,left_camera,right_camera,camera, left_flip, right_flip, flip):
        self.isStereo = stereo
        if self.isStereo:
            self.leftCamera = cv2.VideoCapture(int(left_camera))
            self.rightCamera = cv2.VideoCapture(int(right_camera))
            self.leftFlip = left_flip
            self.rightFlip = right_flip
        else:
            self.camera = cv2.VideoCapture(int(camera))
            self.flip = flip

    @property
    def LeftCamera(self):
        return self.leftCamera

    @property
    def RightCamera(self):
        return self.rightCamera

    def ReadLeftCamera(self):
        success, frame_left = self.LeftCamera.read()
        if self.leftFlip:
            frame_left = cv2.flip(frame_left, 1)
        return success, frame_left

    def ReadRightCamera(self):
        success, frame_right = self.RightCamera.read()
        if self.rightFlip:
            frame_right = cv2.flip(frame_right, 1)
        return success, frame_right
