import numpy as np
import cv2 as cv
from ultralytics import YOLO

model = YOLO("yolo26n.pt")

cap = cv.VideoCapture(1)

cap.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)

pts1 = np.float32([[950,497],[1066,507],[939,602],[1066,612]])
pts2 = np.float32([[400,400],[600,400],[400,600],[600,600]])

#pts2 = np.float32([[200,200],[300,200],[200,300],[300,300]])
M = cv.getPerspectiveTransform(pts1,pts2)

while True:
    # Capture frame-by-frame
    ret, img = cap.read()

    # cv.imwrite('warped_output.jpg', img)

    #Transform the perspective of the frame
    deWarp = cv.warpPerspective(img,M,(1000,1000))

    results = model.track(source=deWarp, conf=0.1, iou=0.7, show=True)

    # Display the resulting frame
    cv.imshow('Webcam', results[0].plot())

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

    # Check for the 'q' key to exit the loop
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()