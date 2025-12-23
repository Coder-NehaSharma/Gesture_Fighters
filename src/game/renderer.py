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

    def draw_bg(self, surface):
        # Draw a retro grid floor
        surface.fill((20, 20, 35)) # Deep dark blue
        
        # Grid lines
        for x in range(0, self.width, 50):
            pygame.draw.line(surface, (30, 30, 50), (x, 0), (x, self.height), 1)
        for y in range(0, self.height, 50):
            pygame.draw.line(surface, (30, 30, 50), (0, y), (self.width, y), 1)
            
        # Floor horizon
        pygame.draw.line(surface, (0, 255, 255), (0, 600), (self.width, 600), 2)

    def draw_health_bar(self, surface, x, y, width, height, percent):
        # Background
        pygame.draw.rect(surface, (50, 0, 0), (x, y, width, height))
        pygame.draw.rect(surface, (255, 255, 255), (x-2, y-2, width+4, height+4), 2) # Border
        
        # Color Logic
        if percent > 0.6: color = (0, 255, 0) # Green
        elif percent > 0.3: color = (255, 255, 0) # Yellow
        else: color = (255, 0, 0) # Red
        
        fill_width = int(width * percent)
        if fill_width > 0:
             pygame.draw.rect(surface, color, (x, y, fill_width, height))

    def draw_lobby(self, surface, p1_ready, p2_ready):
        self.draw_bg(surface)
        
        font_big = pygame.font.SysFont("Verdana", 64, bold=True)
        font_small = pygame.font.SysFont("Verdana", 32)
        
        title = font_big.render("GESTURE FIGHTER", True, (0, 255, 255))
        surface.blit(title, (self.width//2 - title.get_width()//2, 100))
        
        # P1 Status
        offset_p1 = 200
        pygame.draw.circle(surface, (0, 255, 0) if p1_ready else (50, 50, 50), (300, 300), 50)
        p1_text = font_small.render("PLAYER 1", True, (255, 255, 255))
        p1_status = font_small.render("READY" if p1_ready else "WAITING...", True, (0, 255, 0) if p1_ready else (100, 100, 100))
        surface.blit(p1_text, (300 - p1_text.get_width()//2, 370))
        surface.blit(p1_status, (300 - p1_status.get_width()//2, 410))

        # P2 Status
        pygame.draw.circle(surface, (255, 0, 0) if p2_ready else (50, 50, 50), (980, 300), 50)
        p2_text = font_small.render("PLAYER 2", True, (255, 255, 255))
        p2_status = font_small.render("READY" if p2_ready else "WAITING...", True, (0, 255, 0) if p2_ready else (100, 100, 100))
        surface.blit(p2_text, (980 - p2_text.get_width()//2, 370))
        surface.blit(p2_status, (980 - p2_status.get_width()//2, 410))
        
        if p1_ready and p2_ready:
             msg = font_small.render("FIGHT STARTING...", True, (255, 255, 255))
             surface.blit(msg, (self.width//2 - msg.get_width()//2, 550))

    def draw_game_over(self, surface, winner_id):
        s = pygame.Surface((self.width, self.height))
        s.set_alpha(200)
        s.fill((0, 0, 0))
        surface.blit(s, (0,0))
        
        font = pygame.font.SysFont("Verdana", 96, bold=True)
        text = f"PLAYER {winner_id} WINS!"
        color = (0, 255, 255) if winner_id == 1 else (255, 0, 0)
        
        img = font.render(text, True, color)
        surface.blit(img, (self.width//2 - img.get_width()//2, self.height//2 - 100))
        
        font_small = pygame.font.SysFont("Verdana", 32)
        restart = font_small.render("Press 'R' to Restart", True, (255, 255, 255))
        surface.blit(restart, (self.width//2 - restart.get_width()//2, self.height//2 + 50))

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
