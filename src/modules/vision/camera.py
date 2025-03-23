import cv2


class Camera:
    def __init__(self, stereo,left_camera,right_camera,camera, left_flip, right_flip, flip):
        self.isStereo = stereo
        self.leftFlip = False
        self.rightFlip = False
        self.flip = False

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
        if self.isStereo:
            return self.leftCamera
        else:
            return self.camera

    @property
    def RightCamera(self):
        if self.isStereo:
            return self.rightCamera
        else:
            return self.camera

    def ReadLeftCamera(self):
        if self.isStereo:
            success, frame_left = self.LeftCamera.read()
        else:
            success, frame_left = self.camera.read()
        if self.leftFlip:
            frame_left = cv2.flip(frame_left, 1)
        return success, frame_left

    def ReadRightCamera(self):
        if self.isStereo:
            success, frame_right = self.RightCamera.read()
        else:
            success, frame_right = self.camera.read()
        if self.rightFlip:
            frame_right = cv2.flip(frame_right, 1)
        return success, frame_right
