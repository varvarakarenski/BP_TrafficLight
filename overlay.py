import cv2
import numpy as np

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

    (500, 350, (255, 255, 255)), # White 1A + 1B
    (350, 500, (255, 255, 255)), # White 2A + 2B
    (500, 650, (255, 255, 255)), # White 3A + 3B
    (650, 500, (255, 255, 255))  # White 4A + 4B
]

# Mapping: Which index in your array corresponds to which light?
# Index 0: Red 1, Index 1: Green 1, Index 2: Red 2, Index 3: Green 2
# Format: (x_coordinate, y_coordinate, color_bgr)

def draw_overlay(frame, pinValues):
    for i, is_on in enumerate(pinValues):
        if i >= len(light_positions):
            break
        x, y, color = light_positions[i]
        pos = (x, y)
        
        if is_on:
            # Draw a solid glowing circle
            cv2.circle(frame, pos, 15, color, -1) 
            # Add a little white center for a "bulb" effect
            cv2.circle(frame, pos, 5, (255, 255, 255), -1)
        else:
            # Draw just the outline (Light is OFF)
            cv2.circle(frame, pos, 15, (50, 50, 50), 2)
            
    return frame

# --- Main Simulation Loop ---
cap = cv2.VideoCapture(0) # 0 is your camera feed

while True:
    ret, frame = cap.read()
    if not ret: break

    # EXAMPLE: This is where you'd get your array from your logic
    # [R1, Y1, G1, R2, Y2, G2, R3, Y3, G3, R4, Y4, G4, W1A+W1B, W2A+W2B, W3A+W3B, W4A+W4B]
    current_logic_array = [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] 

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