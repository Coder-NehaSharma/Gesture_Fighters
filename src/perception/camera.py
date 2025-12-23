import cv2
import threading
import time

class CameraThread:
    """
    Dedicated thread for grabbing frames from a camera.
    This prevents the main game loop from blocking on cv2.read().
    """
    def __init__(self, camera_id=0, width=640, height=480):
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.frame = None
        self.running = False
        self.lock = threading.Lock()
        self.cap = None

    def start(self):
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            print(f"Error: Could not open camera {self.camera_id}")
            return False
        
        # Optimize camera settings for speed
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        self.running = True
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()
        print(f"Camera {self.camera_id} started.")
        return True

    def _update(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame
            else:
                print(f"Warning: Camera {self.camera_id} failed to read frame.")
                time.sleep(0.1)

    def get_frame(self):
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        if self.cap:
            self.cap.release()
        print(f"Camera {self.camera_id} stopped.")

class CameraManager:
    """
    Manages multiple camera threads.
    """
    def __init__(self, camera_ids=[0]):
        self.cameras = [CameraThread(cid) for cid in camera_ids]

    def start_all(self):
        for cam in self.cameras:
            cam.start()

    def get_frames(self):
        return [cam.get_frame() for cam in self.cameras]

    def stop_all(self):
        for cam in self.cameras:
            cam.stop()
