import cv2
from src.perception.camera import CameraManager
from src.perception.pose import PoseEngine

def main():
    # Initialize Camera (Try just 1 for now to test)
    cam_manager = CameraManager(camera_ids=[0])
    cam_manager.start_all()
    
    # Initialize Pose
    pose_engine = PoseEngine()
    
    print("Press 'q' to quit.")
    
    try:
        while True:
            frames = cam_manager.get_frames()
            frame = frames[0]
            
            if frame is not None:
                # Detect Pose
                landmarks = pose_engine.process_frame(frame)
                
                # Draw Pose
                debug_frame = pose_engine.draw_landmarks(frame, landmarks)
                
                cv2.imshow('Camera 0', debug_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cam_manager.stop_all()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
