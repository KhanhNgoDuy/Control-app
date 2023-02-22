import numpy as np
import cv2
from PyQt5.QtCore import QThread, pyqtSignal, qDebug
from time import time

img_array = []
points = []
webcam = cv2.VideoCapture('images/rotate.mp4')
cnt = 0
total = 0
while True:
    cnt += 1
    start = time()
    gx = gy = rx = ry = None
    ret, imageFrame = webcam.read()

    if not ret:
        webcam.release()
        cv2.destroyAllWindows()
        break

    if cv2.waitKey(10) & 0xFF == ord('q'):
        webcam.release()
        cv2.destroyAllWindows()
        break

    hsvFrame = cv2.cvtColor(imageFrame, cv2.COLOR_BGR2HSV)

    # Set range for red color and
    # define mask
    red_lower = np.array([161, 155, 184], np.uint8)
    red_upper = np.array([179, 255, 255], np.uint8)
    red_mask = cv2.inRange(hsvFrame, red_lower, red_upper)

    # Set range for green color and
    # define mask
    green_lower = np.array([40, 100, 170], np.uint8)
    green_upper = np.array([80, 255, 255], np.uint8)
    green_mask = cv2.inRange(hsvFrame, green_lower, green_upper)

    kernal = np.ones((5, 5), "uint8")

    red_mask = cv2.dilate(red_mask, kernal)
    res_red = cv2.bitwise_and(imageFrame, imageFrame, mask=red_mask)
    green_mask = cv2.dilate(green_mask, kernal)
    res_green = cv2.bitwise_and(imageFrame, imageFrame, mask=green_mask)

    # Creating contour
    threshold = range(0, 200)
    contours, hierarchy = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        area = cv2.contourArea(contour)
        if area in threshold:
            x, y, w, h = cv2.boundingRect(contour)
            points.append((x, y))
            for _x, _y in points:
                imageFrame = cv2.circle(imageFrame, (_x, _y), radius=0, color=(0, 0, 255), thickness=3)
            imageFrame = cv2.rectangle(imageFrame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(imageFrame, "Red Colour", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255))
        M = cv2.moments(contour)
        rx = int(M["m10"] / M["m00"])
        ry = int(M["m01"] / M["m00"])
        # print(f"Red LED Coordinate: ({rx}, {ry})")

    contours, hierarchy = cv2.findContours(green_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        area = cv2.contourArea(contour)
        if area in threshold:
            x, y, w, h = cv2.boundingRect(contour)
            imageFrame = cv2.rectangle(imageFrame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(imageFrame, "Green Colour", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0))
        M = cv2.moments(contour)
        gx = int(M["m10"] / M["m00"])
        gy = int(M["m01"] / M["m00"])
        # print(f"Green LED Coordinate: ({gx}, {gy})")
    img_array.append(imageFrame)
    if None not in [gx, gy, rx, ry]:
        imageFrame = cv2.line(imageFrame, (gx, gy), (rx, ry), (0, 255, 0), thickness=1)
    total += (time() - start)
    cv2.imshow("Multiple Color Detection in Real-TIme", imageFrame)
print(total/cnt)
