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

# order of LEDs used when we only receive label map
LED_ORDER = [
    "R1","Y1","G1",
    "R2","Y2","G2",
    "R3","Y3","G3",
    "R4","Y4","G4",
    "W1A","W1B","W2A","W2B","W3A","W3B","W4A","W4B",
]

# light_positions must be defined before we reference it
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

# shared state updated by listener thread
latest_leds = [0] * len(light_positions)
latest_labels = {}
state_lock = threading.Lock()


def normalize_led_array(arr):
    """Convert any incoming sequence to a list matching the number of light_positions.

    - if arr is shorter, pad with zeros.
    - if arr is longer, truncate.
    - convert truthy values (True, 1) to 1, else 0.
    """
    n = len(light_positions)
    result = [0] * n
    if not arr:
        return result
    for i, val in enumerate(arr):
        if i >= n:
            break
        result[i] = 1 if val else 0
    return result


def listener():
    """Background thread that receives UDP packets and updates shared state."""
    global latest_leds, latest_labels
    last_reported = None
    while True:
        data, addr = sock.recvfrom(65535)
        try:
            payload = json.loads(data.decode())
            with state_lock:
                if "leds" in payload:
                    latest_leds = normalize_led_array(payload.get("leds"))
                else:
                    # build from labels map if leds array not present
                    lbl = payload.get("labels", {})
                    arr = [1 if lbl.get(name) else 0 for name in LED_ORDER]
                    latest_leds = normalize_led_array(arr)

                latest_labels = payload.get("labels", latest_labels)

                # report when array actually changes
                if latest_leds != last_reported:
                    print(f"[->] LEDs updated: {latest_leds}")
                    last_reported = list(latest_leds)

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

# Format: (x_coordinate, y_coordinate, color_bgr)

def draw_overlay(frame, pinValues, base_w=1000, base_h=1000):
    h, w = frame.shape[:2]
    sx = w / float(base_w)
    sy = h / float(base_h)

    # radius relative to frame size
    radius = max(6, int(min(w, h) * 0.03))
    inner = max(2, int(radius * 0.33))

    vals = list(pinValues)
    if len(vals) < len(light_positions):
        vals.extend([0] * (len(light_positions) - len(vals)))
    elif len(vals) > len(light_positions):
        vals = vals[: len(light_positions)]

    for i, is_on in enumerate(vals):
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
    h, w = frame.shape[:2]

    with state_lock:
        current_logic_array = list(latest_leds)
    # if you're debugging and not sending UDP packets, you can override
    # current_logic_array here. for example, an "all green" signal would be:
    #   [0,0,1, 0,0,1, 0,0,1, 0,0,1] + [0]*8  # plus any white lights

    # Add the overlay (listener pads/truncates as needed)
    frame = draw_overlay(frame, current_logic_array)
    
    # overlay array text for debugging
    cv2.putText(frame, str(current_logic_array), (10, h-20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

    # Add a timestamp label
    cv2.putText(frame, "LIVE TRAFFIC LOGIC", (10, 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow('Traffic Camera Feed', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()