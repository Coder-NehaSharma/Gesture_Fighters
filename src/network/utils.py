import json
import struct

def serialize_landmarks(landmarks):
    """
    Converts MediaPipe landmarks object to JSON bytes.
    Handles both MediaPipe objects and dict inputs.
    """
    if not landmarks:
        return json.dumps([]).encode('utf-8')
        
    data = []
    # If it's a MediaPipe object, it has a 'landmark' field which is a list
    if hasattr(landmarks, 'landmark'):
        source = landmarks.landmark
    # If it's the raw list itself (wrapper)
    else:
        source = landmarks 
        
    for lm in source:
        # Handle both object (lm.x) and dict access ({'x':...})
        if isinstance(lm, dict):
             data.append(lm)
        else:
            data.append({
                'x': lm.x,
                'y': lm.y,
                'z': lm.z,
                'v': lm.visibility
            })
    return json.dumps(data).encode('utf-8')

class MockLandmark:
    def __init__(self, x, y, z, v):
        self.x = x
        self.y = y
        self.z = z
        self.visibility = v

class MockLandmarksResult:
    def __init__(self, data_list):
        self.landmark = []
        for d in data_list:
            self.landmark.append(MockLandmark(d['x'], d['y'], d['z'], d['v']))

def deserialize_landmarks(json_bytes):
    try:
        data_list = json.loads(json_bytes.decode('utf-8'))
        if not data_list:
            return None
        return MockLandmarksResult(data_list)
    except Exception as e:
        print(f"Deserialization error: {e}")
        return None

def recvall(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data
