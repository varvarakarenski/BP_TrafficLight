import cv2
import numpy as np
import socket
import json
import threading

# ── Config ────────────────────────────────────────────────────────────────────
LISTEN_HOST = '0.0.0.0'
LISTEN_PORT = 5006

# BGR COLORS
RED, YELLOW, GREEN, WHITE = (0,0,255), (0,255,255), (0,255,0), (255,255,255)

# ── The Coordinate Map ────────────────────────────────────────────────────────
# We map the labels DIRECTLY to coordinates. This fixes the pipeline.
LIGHT_MAP = {
    # Segment 1
    "R1": {"pos": (500, 200), "color": RED},
    "Y1": {"pos": (500, 250), "color": YELLOW},
    "G1": {"pos": (500, 300), "color": GREEN},
    # Segment 2
    "R2": {"pos": (200, 500), "color": RED},
    "Y2": {"pos": (250, 500), "color": YELLOW},
    "G2": {"pos": (300, 500), "color": GREEN},
    # Segment 3
    "R3": {"pos": (500, 700), "color": RED},
    "Y3": {"pos": (500, 750), "color": YELLOW},
    "G3": {"pos": (500, 800), "color": GREEN},
    # Segment 4
    "R4": {"pos": (700, 500), "color": RED},
    "Y4": {"pos": (750, 500), "color": YELLOW},
    "G4": {"pos": (800, 500), "color": GREEN},
    # White Lights
    "W1A": {"pos": (740, 240), "color": WHITE}, "W1B": {"pos": (260, 240), "color": WHITE},
    "W2A": {"pos": (240, 260), "color": WHITE}, "W2B": {"pos": (240, 740), "color": WHITE},
    "W3A": {"pos": (260, 760), "color": WHITE}, "W3B": {"pos": (740, 760), "color": WHITE},
    "W4A": {"pos": (760, 750), "color": WHITE}, "W4B": {"pos": (760, 260), "color": WHITE},
}

# Shared state
latest_labels = {} 
state_lock = threading.Lock()

# ── Network Listener ──────────────────────────────────────────────────────────
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((LISTEN_HOST, LISTEN_PORT))

def listener():
    global latest_labels
    while True:
        try:
            data, _ = sock.recvfrom(65535)
            payload = json.loads(data.decode())
            # We prioritize the "labels" dictionary from your JSON
            # Example payload: {"labels": {"G1": True, "G2": True ...}}
            with state_lock:
                latest_labels = payload.get("labels", {})
        except Exception as e:
            print(f"UDP Error: {e}")

threading.Thread(target=listener, daemon=True).start()

# ── Drawing Logic ─────────────────────────────────────────────────────────────
def draw_overlay(frame, current_labels):
    h, w = frame.shape[:2]
    sx, sy = w / 1000.0, h / 1000.0
    
    # Iterate through our LIGHT_MAP instead of an index array
    for label, info in LIGHT_MAP.items():
        pos = (int(info["pos"][0] * sx), int(info["pos"][1] * sy))
        color = info["color"]
        
        # Check if this specific label is True in the received data
        is_on = current_labels.get(label, False)
        
        if is_on:
            cv2.circle(frame, pos, 22, color, -1)
            cv2.circle(frame, pos, 8, (255, 255, 255), -1)
            # Add label text for 100% clarity
            cv2.putText(frame, label, (pos[0]-15, pos[1]+40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1)
        else:
            cv2.circle(frame, pos, 20, (40, 40, 40), 2)
            
    return frame

# ── Main Loop ─────────────────────────────────────────────────────────────────
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret: break

    with state_lock:
        current_state = latest_labels.copy()

    frame = draw_overlay(frame, current_state)
    
    cv2.putText(frame, "SYSTEM READY - LISTENING ON 5006", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow('Traffic Dashboard', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()