import cv2
import mediapipe as mp
import socket
import struct
import json
import argparse
import sys
import time

"""
GESTURE FIGHTER - CLIENT CAPTURE SCRIPT
Runs on Windows Laptop to capture Camera and send Pose to Mac Host.
"""

# --- Protocol Utils (Inline copy to be standalone) ---
def serialize_landmarks(landmarks):
    if not landmarks:
        return json.dumps([]).encode('utf-8')
    data = []
    for lm in landmarks.landmark:
        data.append({
            'x': lm.x, 'y': lm.y, 'z': lm.z, 'v': lm.visibility
        })
    return json.dumps(data).encode('utf-8')

# --- Main Logic ---
def main():
    parser = argparse.ArgumentParser(description='Gesture Fighter Client')
    parser.add_argument('--host', type=str, required=True, help='IP Address of the Mac Host')
    parser.add_argument('--port', type=int, default=5000, help='Port to connect to')
    parser.add_argument('--camera', type=int, default=0, help='Camera ID')
    args = parser.parse_args()

    print(f"Connecting to Host {args.host}:{args.port}...")

    # 1. Setup Network
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((args.host, args.port))
        print("Successfully Connected!")
    except Exception as e:
        print(f"Connection Failed: {e}")
        return

    # 2. Setup Camera
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"Error: Cannot open camera {args.camera}")
        return

    # 3. Setup MediaPipe
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    mp_drawing = mp.solutions.drawing_utils

    print("Capture Started. Press 'q' to quit.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret: break

            # Process
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_rgb.flags.writeable = False
            results = pose.process(frame_rgb)
            
            # Send Data
            if results.pose_landmarks:
                try:
                    data = serialize_landmarks(results.pose_landmarks)
                    # Send Length + Data
                    msg = struct.pack('>I', len(data)) + data
                    sock.sendall(msg)
                except Exception as e:
                    print(f"Send Error: {e}")
                    break

            # Feedback UI
            frame.flags.writeable = True
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
            cv2.imshow('Gesture Fighter Client (Sending Data...)', frame)
            
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break
                
    finally:
        cap.release()
        sock.close()
        cv2.destroyAllWindows()
        print("Disconnected.")

if __name__ == "__main__":
    main()
