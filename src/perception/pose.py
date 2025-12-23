import mediapipe as mp
import cv2
import numpy as np

class PoseEngine:
    """
    Wrapper for MediaPipe Pose to extract body landmarks.
    """
    def __init__(self, static_image_mode=False, model_complexity=1, smooth_landmarks=True):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            smooth_landmarks=smooth_landmarks,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils

    def process_frame(self, frame):
        """
        Processes a BGR frame and returns landmarks.
        """
        if frame is None:
            return None

        # MediaPipe needs RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False # Performance trick
        
        results = self.pose.process(rgb_frame)
        
        return results.pose_landmarks

    def draw_landmarks(self, frame, landmarks):
        """
        Debug helper to draw the skeleton on the frame.
        """
        if landmarks:
            self.mp_drawing.draw_landmarks(
                frame,
                landmarks,
                self.mp_pose.POSE_CONNECTIONS
            )
        return frame
