import pygame
import numpy as np

class AvatarRenderer:
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        
        # Colors
        self.P1_COLOR = (0, 255, 255) # Cyan
        self.P2_COLOR = (255, 0, 0)   # Red
        self.BONE_COLOR = (255, 255, 255)
        
        # Connections to draw (MediaPipe indices)
        self.CONNECTIONS = [
            (11, 13), (13, 15), # Left Arm
            (12, 14), (14, 16), # Right Arm
            (11, 12),           # Shoulders
            (11, 23), (12, 24), # Torso
            (23, 24),           # Hips
            (23, 25), (25, 27), # Left Leg
            (24, 26), (26, 28)  # Right Leg
        ]

    def draw_avatar(self, surface, landmarks, player_id=1, offset_x=0):
        """
        Draws a stickman from landmarks.
        landmarks: MediaPipe normalized landmarks (0.0-1.0)
        offset_x: Pixel shift to place P1 left/P2 right
        """
        if not landmarks:
            return

        points = {}
        
        # 1. Convert normalized landmarks to screen coordinates
        for idx, lm in enumerate(landmarks.landmark):
            # We focus on the upper body/main joints (0-32)
            # x is 0-1, y is 0-1
            
            # Flip X for mirroring effect if needed
            x = lm.x
            y = lm.y
            
            # Simple projection
            px = int(x * 300) + offset_x # Scale width to 300px avatar space
            py = int(y * 400) + 100      # Scale height
            
            points[idx] = (px, py)
            
        color = self.P1_COLOR if player_id == 1 else self.P2_COLOR
        
        # 2. Draw Bones
        for start, end in self.CONNECTIONS:
            if start in points and end in points:
                pygame.draw.line(surface, color, points[start], points[end], 3)
                
        # 3. Draw Head (Approximate from nose/ears)
        if 0 in points: # Nose
            pygame.draw.circle(surface, self.BONE_COLOR, points[0], 10)
            
        # 4. Draw Hands (fists)
        if 15 in points: # L Wrist
             pygame.draw.circle(surface, (255, 255, 0), points[15], 8)
        if 16 in points: # R Wrist
             pygame.draw.circle(surface, (255, 255, 0), points[16], 8)
