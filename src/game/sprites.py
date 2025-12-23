import pygame

class SpriteManager:
    def __init__(self):
        self.p1_parts = {}
        self.p2_parts = {}
        
    def load_sprites(self):
        # Load P1 (Red)
        try:
            sheet_p1 = pygame.image.load("assets/p1_spritesheet.png").convert_alpha()
            self.p1_parts = self.slice_sheet(sheet_p1)
        except Exception as e:
            print(f"Error loading P1 sprites: {e}")
            
        # Load P2 (Blue)
        try:
            sheet_p2 = pygame.image.load("assets/p2_spritesheet.png").convert_alpha()
            self.p2_parts = self.slice_sheet(sheet_p2)
        except Exception as e:
            print(f"Error loading P2 sprites: {e}")

    def slice_sheet(self, sheet):
        """
        Heuristic Slicing:
        Assumes the AI generated a roughly grid-like or separable layout.
        We blindly cut it into 4 key regions for now. 
        Top-Left: Head
        Bottom-Left: Torso
        Top-Right: Arms
        Bottom-Right: Legs
        """
        w, h = sheet.get_size()
        mid_x = w // 2
        mid_y = h // 2
        
        parts = {
            "head": sheet.subsurface((0, 0, mid_x, mid_y)),
            "torso": sheet.subsurface((0, mid_y, mid_x, mid_y)),
            "arm": sheet.subsurface((mid_x, 0, mid_x, mid_y)),
            "leg": sheet.subsurface((mid_x, mid_y, mid_x, mid_y))
        }
        return parts

    def get_rotated_part(self, player_id, part_name, angle):
        parts = self.p1_parts if player_id == 1 else self.p2_parts
        if part_name not in parts:
            return None
            
        orig_image = parts[part_name]
        # Rotate around center
        rotated_image = pygame.transform.rotate(orig_image, -angle) # Negative for pygame coord system
        return rotated_image
