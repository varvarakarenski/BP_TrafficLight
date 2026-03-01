import numpy as np
import cv2 as cv

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
    final = cv.warpPerspective(img,M,(1000,1000))

    # Display the resulting frame
    cv.imshow('Webcam', final)

    # Check for the 'q' key to exit the loop
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()