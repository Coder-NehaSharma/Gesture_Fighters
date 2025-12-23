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
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.DOUBLEBUF)
        pygame.display.set_caption("Gesture Fighter - SERVER HOST")
        self.clock = pygame.time.Clock()
        
        # Networking
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
        
        # State: LOBBY, FIGHT, GAMEOVER
        self.state = "LOBBY"
        self.winner = None
        
        self.reset_game()

    def reset_game(self):
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
                if event.key == pygame.K_r:
                    if self.state == "GAMEOVER":
                        self.state = "LOBBY"
                        self.reset_game()

    def update(self):
        # 1. Network Data
        raw_p1, raw_p2 = self.server.get_landmarks()
        
        # Smooth and Store
        from src.network.utils import MockLandmarksResult
        current_time = pygame.time.get_ticks() / 1000.0
        
        if raw_p1:
             self.landmarks_p1 = MockLandmarksResult(self.smoother_p1.smooth(raw_p1, current_time))
        else:
             self.landmarks_p1 = None
             
        if raw_p2:
             self.landmarks_p2 = MockLandmarksResult(self.smoother_p2.smooth(raw_p2, current_time))
        else:
             self.landmarks_p2 = None

        # State Machine Logic
        if self.state == "LOBBY":
            # If both players present, auto start? Or just wait for visual confirmation.
            # Let's say if both are present for > 1 second, we start.
            if self.landmarks_p1 and self.landmarks_p2:
                # In a real game we'd have a countdown
                self.state = "FIGHT"
                self.reset_game()

        elif self.state == "FIGHT":
            # Action Detect
            self.p1_action = self.detector_p1.detect(self.landmarks_p1)
            self.p2_action = self.detector_p2.detect(self.landmarks_p2)
            
            # Hit Detect
            if "PUNCH" in self.p1_action and self.landmarks_p2:
                self.p2_health = max(0, self.p2_health - 1.5) # 1.5 dmg per frame
            
            if "PUNCH" in self.p2_action and self.landmarks_p1:
                self.p1_health = max(0, self.p1_health - 1.5)
                
            # Win Check
            if self.p1_health <= 0:
                self.state = "GAMEOVER"
                self.winner = 2
            elif self.p2_health <= 0:
                self.state = "GAMEOVER"
                self.winner = 1

    def render(self):
        # LOBBY
        if self.state == "LOBBY":
            p1_r = self.landmarks_p1 is not None
            p2_r = self.landmarks_p2 is not None
            self.renderer.draw_lobby(self.screen, p1_r, p2_r)
            pygame.display.flip()
            return

        # FIGHT or GAMEOVER (Draw game under overlay)
        self.renderer.draw_bg(self.screen)
        
        # Avatars
        self.renderer.draw_avatar(self.screen, self.landmarks_p1, 1, 200)
        self.renderer.draw_avatar(self.screen, self.landmarks_p2, 2, 800)
        
        # HUD
        self.renderer.draw_health_bar(self.screen, 50, 50, 400, 30, self.p1_health/100.0)
        self.renderer.draw_health_bar(self.screen, self.WIDTH-450, 50, 400, 30, self.p2_health/100.0)
        
        # Hit Text
        font = pygame.font.SysFont("Verdana", 48, bold=True)
        if "PUNCH" in self.p1_action:
             self.screen.blit(font.render("HIT!", True, (255, 255, 0)), (200, 200))
        if "PUNCH" in self.p2_action:
             self.screen.blit(font.render("HIT!", True, (255, 255, 0)), (self.WIDTH-300, 200))

        # GAMEOVER Overlay
        if self.state == "GAMEOVER":
            self.renderer.draw_game_over(self.screen, self.winner)
            
        pygame.display.flip()

if __name__ == "__main__":
    game = GameEngine()
    game.run()
