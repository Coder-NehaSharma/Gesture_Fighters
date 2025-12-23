import numpy as np
from src.logic.geometry import calculate_angle
import time

class ActionDetector:
    """
    Stateful detector that looks at current and previous frames 
    to determine actions based on velocity and pose.
    """
    def __init__(self):
        self.prev_landmarks = None
        self.prev_time = time.time()
        
        # Velocity thresholds (pixels/sec or normalized units/sec)
        # These need tuning!
        self.PUNCH_VELOCITY_THRESHOLD = 0.5 
        self.KICK_VELOCITY_THRESHOLD = 0.5
        
        # Extension thresholds (degrees)
        self.ELBOW_EXTENSION_THRESHOLD = 150
        self.KNEE_EXTENSION_THRESHOLD = 150
        
        self.last_action = "IDLE"
        self.cooldown = 0

    def detect(self, landmarks):
        """
        Returns 'IDLE', 'PUNCH_LEFT', 'PUNCH_RIGHT', 'KICK_LEFT', 'KICK_RIGHT'
        """
        if landmarks is None:
            return "IDLE"

        current_time = time.time()
        dt = current_time - self.prev_time
        if dt == 0: dt = 0.001
        
        # Extract useful joints (MediaPipe indices)
        # 11=L_Shoulder, 13=L_Elbow, 15=L_Wrist
        # 12=R_Shoulder, 14=R_Elbow, 16=R_Wrist
        # 23=L_Hip, 25=L_Knee, 27=L_Ankle
        # 24=R_Hip, 26=R_Knee, 28=R_Ankle
        
        l_shoulder = [landmarks.landmark[11].x, landmarks.landmark[11].y]
        l_elbow = [landmarks.landmark[13].x, landmarks.landmark[13].y]
        l_wrist = [landmarks.landmark[15].x, landmarks.landmark[15].y]
        
        r_shoulder = [landmarks.landmark[12].x, landmarks.landmark[12].y]
        r_elbow = [landmarks.landmark[14].x, landmarks.landmark[14].y]
        r_wrist = [landmarks.landmark[16].x, landmarks.landmark[16].y]
        
        # Calculate Angles
        l_elbow_angle = calculate_angle(l_shoulder, l_elbow, l_wrist)
        r_elbow_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)
        
        # Calculate Velocities if we have history
        l_wrist_vel = 0
        r_wrist_vel = 0
        
        if self.prev_landmarks:
            prev_l_wrist = [self.prev_landmarks.landmark[15].x, self.prev_landmarks.landmark[15].y]
            prev_r_wrist = [self.prev_landmarks.landmark[16].x, self.prev_landmarks.landmark[16].y]
            
            # Simple Euclidean distance change
            l_wrist_dist = np.linalg.norm(np.array(l_wrist) - np.array(prev_l_wrist))
            r_wrist_dist = np.linalg.norm(np.array(r_wrist) - np.array(prev_r_wrist))
            
            l_wrist_vel = l_wrist_dist / dt
            r_wrist_vel = r_wrist_dist / dt

        # Update State
        self.prev_landmarks = landmarks
        self.prev_time = current_time
        
        # Cooldown prevents spamming (1 action per 0.5s approx)
        if self.cooldown > 0:
            self.cooldown -= dt
            return "IDLE"

        
        # Detection Logic
        action = "IDLE"
        
        # Print debug info occasionally
        # print(f"L_Vel: {l_wrist_vel:.2f}, L_Ang: {l_elbow_angle:.0f}")

        # Check Punches
        if l_elbow_angle > self.ELBOW_EXTENSION_THRESHOLD and l_wrist_vel > self.PUNCH_VELOCITY_THRESHOLD:
            action = "PUNCH_LEFT"
        elif r_elbow_angle > self.ELBOW_EXTENSION_THRESHOLD and r_wrist_vel > self.PUNCH_VELOCITY_THRESHOLD:
            action = "PUNCH_RIGHT"
            
        # (Kicks logic would be similar, checking knees and foot velocity)
        # TODO: Implement Kicks
        
        if action != "IDLE":
            self.cooldown = 0.4 # 400ms cooldown
            
        return action
