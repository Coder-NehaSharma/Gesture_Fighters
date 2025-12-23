import numpy as np

def calculate_angle(a, b, c):
    """
    Calculates the angle at point b given points a, b, c.
    Points are (x, y) or (x, y, z).
    Returns angle in degrees (0-180).
    """
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle

def normalize_keypoint(point, hip_center, scale):
    """
    Translates point relative to hip_center and scales it.
    """
    return (point - hip_center) * scale
