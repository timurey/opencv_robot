import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np

gesture_recognizer_task = "models/gesture_recognizer.task"
hand_landmarker_task = "models/hand_landmarker.task"

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode


class MediapipeHandsModule:
    def __init__(self):
        self.mp_drawing = solutions.drawing_utils
        self.mp_pose = solutions.hands
        self.results = None
        self.timestamp = 0
        self.landmarkerOptions = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=hand_landmarker_task),
            running_mode=VisionRunningMode.LIVE_STREAM,
            num_hands=2,
            result_callback=self.print_handmarker_result)

    def draw_landmarks_on_image(self, rgb_image, detection_result):
        hands_landmarks_list = detection_result.hand_landmarks
        # pose_landmarks_list = detection_result
        annotated_image = np.copy(rgb_image)

        # Loop through the detected poses to visualize.
        for idx in range(len(hands_landmarks_list)):
            hand_landmarks = hands_landmarks_list[idx]

            # Draw the pose landmarks.
            hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            hand_landmarks_proto.landmark.extend([
                landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
            ])
            solutions.drawing_utils.draw_landmarks(
                annotated_image,
                hand_landmarks_proto,
                solutions.hands.HAND_CONNECTIONS,
                solutions.drawing_styles.get_default_hand_landmarks_style())
        return annotated_image

    def print_handmarker_result(self, result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        print('hands landmarker result: {}'.format(result))
        self.results = result
        # print(type(result))

    def getGestures(self, frame):
        results_ = None
        with HandLandmarker.create_from_options(self.landmarkerOptions) as landmarker:
            self.timestamp += 1
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            landmarker.detect_async(mp_image, self.timestamp)

            # print(type(self.results))

            if (bool(self.results.hand_landmarks)):
                annotated_image = self.draw_landmarks_on_image(mp_image.numpy_view(), self.results)
                # cv2.imshow('Show',cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
                print("showing detected image")
                results_ = self.results
                self.results = None
                return annotated_image, results_

        return frame, results_


# if __name__ == "__main__":
#     hands_module = MediapipeHandsModule()
    # body_module.main()
