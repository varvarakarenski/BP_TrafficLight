from ultralytics import YOLO
import cv2 as cv

# Configure the tracking parameters and run the tracker
model = YOLO("yolo26n.pt")
results = model.track(source="Cars2.png", conf=0.1, iou=0.7, show=True)

cv.imshow("Whatever", results[0].plot())

# Display the tracking results
for result in results:
    box = result.boxes.xyxy  # Bounding box coordinates
    confidence = result.boxes.conf   # Confidence scores
    classifier = result.boxes.cls    # Class labels

for i in range(len(box)):
    x1, y1, x2, y2 = box[i]
    ya= ((y2 - y1)/2)+y1
    xa= ((x2 - x1)/2)+x1
    conf = confidence[i]
    cls = classifier[i]
    print(f"Object {i}: Class={cls}, Confidence={conf}, Center=({xa}, {ya})")

cv.waitKey(0)