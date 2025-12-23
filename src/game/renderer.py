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
