import cv2
import numpy as np
import socket
import pickle
import struct

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
cap = cv2.VideoCapture(0) # 0 is your camera feed

while True:
    ret, frame = cap.read()
    if not ret: break

    # EXAMPLE: This is where we'd get your array from your logic
    # [R1, Y1, G1, R2, Y2, G2, R3, Y3, G3, R4, Y4, G4, W1A+W1B, W2A+W2B, W3A+W3B, W4A+W4B]
    current_logic_array = [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0] 

    # Add the overlay
    frame = draw_overlay(frame, current_logic_array)
    
    # Add a timestamp label
    cv2.putText(frame, "LIVE TRAFFIC LOGIC", (10, 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow('Traffic Camera Feed', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()