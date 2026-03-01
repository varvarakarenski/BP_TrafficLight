import cv2
import numpy as np
import socket
import json
import threading

# ── Config ────────────────────────────────────────────────────────────────────
LISTEN_HOST = '0.0.0.0'  # listen on all interfaces
LISTEN_PORT = 5006
# ─────────────────────────────────────────────────────────────────────────────

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((LISTEN_HOST, LISTEN_PORT))
print(f"[OK] Dashboard receiver listening on port {LISTEN_PORT}")
print(f"    Waiting for LED state from Communicator...\n")

# Group labels for pretty printing
GROUPS = {
    "GREEN" : ["G1","G2","G3","G4"],
    "YELLOW": ["Y1","Y2","Y3","Y4"],
    "RED"   : ["R1","R2","R3","R4"],
    "WALK"  : ["P1","P2","P3","P4"],
}

# shared state updated by listener thread
latest_leds = [0] * 20
latest_labels = {}
state_lock = threading.Lock()


def listener():
    """Background thread that receives UDP packets and updates shared state."""
    global latest_leds, latest_labels
    while True:
        data, addr = sock.recvfrom(65535)
        try:
            payload = json.loads(data.decode())
            with state_lock:
                latest_leds = payload.get("leds", latest_leds)
                latest_labels = payload.get("labels", latest_labels)

            # pretty-print the groups as before
            lines = []
            for group, keys in GROUPS.items():
                active = [k for k in keys if latest_labels.get(k)]
                lines.append(f"  {group:6s}: {', '.join(active) if active else '-'}")
            print('\n'.join(lines))
            print()

        except (json.JSONDecodeError, KeyError) as e:
            print(f"[!] Bad packet from {addr}: {e}")


# start listener thread
thread = threading.Thread(target=listener, daemon=True)
thread.start()

light_positions = [
    (500, 200, (0, 255, 0)),     # Red 1
    (500, 250, (0, 255, 255)),   # Yellow 1
    (500, 300, (0, 0, 255)),     # Green 1

    (200, 500, (0, 255, 0)),     # Red 2
    (250, 500, (0, 255, 255)),   # Yellow 2
    (300, 500, (0, 0, 255)),     # Green 2

    (500, 700, (0, 0, 255)),     # Red 3
    (500, 750, (0, 255, 255)),   # Yellow 3
    (500, 800, (0, 255, 0)),     # Green 3

    (700, 500, (0, 0, 255)),     # Red 4
    (750, 500, (0, 255, 255)),   # Yellow 4
    (800, 500, (255, 0, 0)),     # Green 4

    (740, 240, (255, 255, 255)), # White 1A
    (260, 240, (255, 255, 255)), # White 1B
    (240, 260, (255, 255, 255)), # White 2A
    (240, 740, (255, 255, 255)), # White 2B
    (260, 760, (255, 255, 255)), # White 3A
    (740, 760, (255, 255, 255)), # White 3B
    (760, 750, (255, 255, 255)), # White 4A
    (760, 260, (255, 255, 255))  # White 4B
]

# Format: (x_coordinate, y_coordinate, color_bgr)

def draw_overlay(frame, pinValues, base_w=1000, base_h=1000):
    h, w = frame.shape[:2]
    sx = w / float(base_w)
    sy = h / float(base_h)

    # radius relative to frame size
    radius = max(6, int(min(w, h) * 0.03))
    inner = max(2, int(radius * 0.33))

    for i, is_on in enumerate(pinValues):
        if i >= len(light_positions):
            break
        x, y, color = light_positions[i]

        # support both absolute (e.g. 500) and normalized (0.5) coords
        if x <= 1:
            xs = int(x * w)
        else:
            xs = int(x * sx)

        if y <= 1:
            ys = int(y * h)
        else:
            ys = int(y * sy)

        pos = (xs, ys)

        if is_on:
            cv2.circle(frame, pos, radius, color, -1)
            cv2.circle(frame, pos, inner, (255, 255, 255), -1)
        else:
            cv2.circle(frame, pos, radius, (50, 50, 50), 2)

        # small debug label to confirm point is drawn
        cv2.putText(frame, str(i), (xs + radius + 4, ys + radius + 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

    return frame

# --- Main Simulation Loop ---
cap = cv2.VideoCapture(0) # 0 is camera feed

while True:
    ret, frame = cap.read()
    if not ret: break

    with state_lock:
        current_logic_array = list(latest_leds)

    # Add the overlay (listener pads/truncates as needed)
    frame = draw_overlay(frame, current_logic_array)
    
    # Add a timestamp label
    cv2.putText(frame, "LIVE TRAFFIC LOGIC", (10, 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow('Traffic Camera Feed', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()