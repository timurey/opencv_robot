import cv2
from .gesture_recognition import MediapipeHandsModule

# font
font = cv2.FONT_HERSHEY_SIMPLEX
# org
org = (450, 450)
# fontScale
fontScale = 1
# Blue color in BGR
color = (0, 255, 0)
# Line thickness of 2 px
thickness = 1
gestureRecognition = MediapipeHandsModule()
print(gestureRecognition)


def get_hands(frame):
    hands = {"left": "none", "right": "none"}
    results = {}
    # frame = cv2.resize(frame, (320, 240), interpolation=cv2.INTER_AREA)  # уменьшаем разрешение кадров (если видео тупит, можно уменьшить еще больше)

    frame, results = gestureRecognition.getGestures(frame)
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # перевод изображения в градации серого
    # frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)  # перевод изображения в цветное

    frame = cv2.putText(frame, str(hands), org, font, fontScale, color, thickness, cv2.LINE_AA)

    return frame, results
