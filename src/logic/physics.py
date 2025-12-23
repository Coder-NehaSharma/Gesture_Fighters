class PhysicsEngine:
    """
    Handles collisions between separate entity coordinates.
    Arguments are typically normalized game coordinates (0-1000 range).
    """
    def check_hit(self, attack_point, hitbox_rect):
        """
        attack_point: (x, y)
        hitbox_rect: (x, y, w, h)
        """
        px, py = attack_point
        rx, ry, rw, rh = hitbox_rect
        
        if rx <= px <= rx + rw and ry <= py <= ry + rh:
            return True
        return False

    def get_hitbox(self, pose_coords, type="BODY"):
        """
        Returns a bounding box valid for the current pose.
        Requires normalized pose coordinates.
        """
        # Placeholder: returning generic box
        # Real impl would calculate box around torso landmarks
        return (0, 0, 0, 0)
