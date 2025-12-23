import pygame
import sys
from src.perception.camera import CameraManager
from src.perception.pose import PoseEngine
from src.logic.rules import ActionDetector
from src.game.renderer import AvatarRenderer

class GameEngine:
    def __init__(self):
        pygame.init()
        self.WIDTH = 1280
        self.HEIGHT = 720
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Gesture Fighter - SERVER HOST")
        self.clock = pygame.time.Clock()
        
        # Networking (Server)
        from src.network.server import MultiPlayerServer
        self.server = MultiPlayerServer(port=5000)
        
        # Logic
        from src.logic.smoothing import LandmarkSmoother
        self.smoother_p1 = LandmarkSmoother(min_cutoff=0.01, beta=0.5)
        self.smoother_p2 = LandmarkSmoother(min_cutoff=0.01, beta=0.5)
        
        self.detector_p1 = ActionDetector()
        self.detector_p2 = ActionDetector()
        
        self.renderer = AvatarRenderer(self.WIDTH, self.HEIGHT)
        
        self.running = True
        
        # Game State
        self.p1_health = 100
        self.p2_health = 100
        
        self.p1_action = "IDLE"
        self.p2_action = "IDLE"
        
        self.landmarks_p1 = None
        self.landmarks_p2 = None

    def run(self):
        print("Starting Game Server...")
        self.server.start()
        
        try:
            while self.running:
                self.handle_events()
                self.update()
                self.render()
                self.clock.tick(30)
        finally:
            self.server.stop()
            pygame.quit()
            sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_r: # Reset
                    self.p1_health = 100
                    self.p2_health = 100

    def update(self):
        # 1. Get Landmarks directly from Network Server
        raw_p1, raw_p2 = self.server.get_landmarks()
        
        current_time = pygame.time.get_ticks() / 1000.0
        
        # 1.5 Apply Smoothing
        # We need Mock Objects back because Receiver gives dicts, but Renderer/Detector expects objects or dicts (Detector handles object-like access specificly)
        # Actually our Detector/Renderer access .x .y properties if it's an object.
        # But our Smoother returns DICTS. 
        # Let's standardize everything to use helper class MockLandmarksResult from network.utils if needed,
        # OR just update Detector/Renderer to handle dicts. 
        # For speed: Let's assume Detector/Renderer logic was updated to use attributes. 
        # Let's wrap the Smoothed Dicts into MockLandmark Objects so existing code doesn't break.
        
        from src.network.utils import MockLandmarksResult
        
        if raw_p1:
             smoothed_p1_data = self.smoother_p1.smooth(raw_p1, current_time)
             self.landmarks_p1 = MockLandmarksResult(smoothed_p1_data)
        else:
             self.landmarks_p1 = None
             
        if raw_p2:
             smoothed_p2_data = self.smoother_p2.smooth(raw_p2, current_time)
             self.landmarks_p2 = MockLandmarksResult(smoothed_p2_data)
        else:
             self.landmarks_p2 = None
        
        # 2. Process Actions
        self.p1_action = self.detector_p1.detect(self.landmarks_p1)
        self.p2_action = self.detector_p2.detect(self.landmarks_p2)
        
        # 3. Hit Detection
        if "PUNCH" in self.p1_action and self.landmarks_p2:
                 self.p2_health = max(0, self.p2_health - 1)
                 
        if "PUNCH" in self.p2_action and self.landmarks_p1:
                self.p1_health = max(0, self.p1_health - 1)

    def render(self):
        self.screen.fill((20, 20, 40)) # Dark Blue
        
        # Floor
        pygame.draw.line(self.screen, (200, 200, 200), (0, 600), (self.WIDTH, 600), 2)
        
        # Draw P1 (Left side, cyan)
        self.renderer.draw_avatar(self.screen, self.landmarks_p1, player_id=1, offset_x=200)
        
        # Draw P2 (Right side, red). We might want to flip P2 visually?
        # For now, just rendering them.
        self.renderer.draw_avatar(self.screen, self.landmarks_p2, player_id=2, offset_x=800)
        
        # UI: Health Bars
        # P1
        pygame.draw.rect(self.screen, (255, 0, 0), (50, 50, 400, 30))
        pygame.draw.rect(self.screen, (0, 255, 0), (50, 50, 400 * (self.p1_health/100), 30))
        
        # P2
        pygame.draw.rect(self.screen, (255, 0, 0), (self.WIDTH - 450, 50, 400, 30))
        pygame.draw.rect(self.screen, (0, 255, 0), (self.WIDTH - 450, 50, 400 * (self.p2_health/100), 30))
        
        # Action Text
        font = pygame.font.SysFont("Arial", 36, bold=True)
        if "PUNCH" in self.p1_action:
            self.screen.blit(font.render("P1 HIT!", True, (255, 255, 0)), (200, 200))
        if "PUNCH" in self.p2_action:
            self.screen.blit(font.render("P2 HIT!", True, (255, 255, 0)), (self.WIDTH - 300, 200))
            
        # Game Over
        if self.p1_health <= 0:
            over_text = font.render("PLAYER 2 WINS!", True, (255, 255, 255))
            self.screen.blit(over_text, (self.WIDTH//2 - 150, self.HEIGHT//2))
        elif self.p2_health <= 0:
            over_text = font.render("PLAYER 1 WINS!", True, (255, 255, 255))
            self.screen.blit(over_text, (self.WIDTH//2 - 150, self.HEIGHT//2))

        pygame.display.flip()

if __name__ == "__main__":
    game = GameEngine()
    game.run()
