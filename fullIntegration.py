import socket
import pickle
import struct
import numpy as np
import cv2 as cv
from ultralytics import YOLO

host='127.0.0.1'
port=65432

light_positions = [
    (500, 200, (0, 255, 0))     # Green 1
    (500, 250, (0, 255, 255))   # Yellow 1
    (500, 300, (0, 0, 255)),    # Red 1 

    (200, 250, (0, 255, 0))     # Green 2
    (250, 250, (0, 255, 255))   # Yellow 2
    (300, 250, (0, 0, 255)),    # Red 2 

    (500, 700, (0, 0, 255))     # Red 3
    (500, 750, (0, 255, 255))   # Yellow 3
    (500, 800, (0, 255, 0)),    # Green 3

    (700, 250, (0, 0, 255))     # Red 4
    (750, 250, (0, 255, 255))   # Yellow 4
    (800, 250, (255, 0, 0)),    # Green 4 
]

# Mapping: Which index in your array corresponds to which light?
# Index 0: Red 1, Index 1: Green 1, Index 2: Red 2, Index 3: Green 2
# Format: (x_coordinate, y_coordinate, color_bgr)

def draw_overlay(frame, pinValues):
    for i, is_on in enumerate(pinValues):
        pos, color = light_positions[i][0:2], light_positions[i][2]
        
        if is_on:
            # Draw a solid glowing circle
            cv.circle(frame, pos, 15, color, -1) 
            # Add a little white center for a "bulb" effect
            cv.circle(frame, pos, 5, (255, 255, 255), -1)
        else:
            # Draw just the outline (Light is OFF)
            cv.circle(frame, pos, 15, (50, 50, 50), 2)
            
    return frame

class Target:
    def __init__(self, x, y, type, ID):
        self.x = x
        self.y = y
        self.type = type
        self.ID = ID

model = YOLO("Custome3.pt")

cap = cv.VideoCapture(1)

cap.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)


pts1 = np.float32([[431,258],[1031,1],[996,1061],[1630,379]])
pts2 = np.float32([[0,0],[1000,0],[0,1000],[1000,1000]])

M = cv.getPerspectiveTransform(pts1,pts2)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, port))
    s.listen()
    print(f"Server listening on {host}:{port}...")
    conn, addr = s.accept()
    
    with conn:
        while True:
            # Capture frame-by-frame
            ret, img = cap.read()

            # cv.imwrite('warped_output.jpg', img)

            #Transform the perspective of the frame
            deWarp = cv.warpPerspective(img,M,(1000,1000))

            results = model.track(source=deWarp, conf=0.5, iou=0.7, show=False)

            for result in results:
                box = result.boxes.xyxy  # Bounding box coordinates
                confidence = result.boxes.conf   # Confidence scores
                classifier = result.boxes.cls    # Class labels

            list1 = []

            for i in range(len(box)):
                x1, y1, x2, y2 = box[i]
                ya= ((y2 - y1)/2)+y1
                xa= ((x2 - x1)/2)+x1
                conf = confidence[i]
                cls = classifier[i]
                x=Target(xa, ya, cls, i)
                list1.append(x)

            print("Targets:")
            for x in list1:
                print(f"Object {x.ID}: Class={x.type}, Center=({x.x}, {x.y})")

            current_logic_array = [True, False, False, True]

            #Add Overlay to the frame
            final = draw_overlay(results[0].plot(), current_logic_array)
            # Display the resulting frame


            cv.imshow('Webcam', final)

            # 1. Serialize the array
            data = pickle.dumps(list1)
            
            # 2. Pack the length of the data into 8 bytes (Q = unsigned long long)
            message_size = struct.pack("Q", len(data))
            
            # 3. Send length then data
            conn.sendall(message_size + data)

            # Check for the 'q' key to exit the loop
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

cap.release()
cv.destroyAllWindows()