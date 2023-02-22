import numpy as np
import cv2
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication


DISTANCE_ON_SCREEN = 0
DISTANCE_REAL = 0


class ImageProcessingThread(QObject):
    position_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

    @pyqtSlot(np.ndarray)
    def extract_position(self, imageFrame):
        rx = ry = gx = gy = None
        led_position_dict = {
            'red': (rx, ry),
            'green': (gx, gy)
        }

        hsvFrame = cv2.cvtColor(imageFrame, cv2.COLOR_RGB2HSV)

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
            # print("red area", area)
            if area in threshold:
                x, y, w, h = cv2.boundingRect(contour)
                imageFrame = cv2.rectangle(imageFrame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(imageFrame, "Red Colour", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0))
            M = cv2.moments(contour)
            rx = int(M["m10"] / M["m00"])
            ry = int(M["m01"] / M["m00"])
            led_position_dict['red'] = (rx, ry)
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
            led_position_dict['green'] = (gx, gy)
            # print(f"Green LED Coordinate: ({gx}, {gy})")

        # print(rx, ry, gx, gy)
        if None not in (rx, ry, gx, gy):
            position = self.led_to_global(led_position_dict)
            self.position_signal.emit(position)

    @staticmethod
    def led_to_global(led_position_dict):
        rx, ry = led_position_dict['red']
        gx, gy = led_position_dict['green']

        num = gy - ry
        deno = gx - rx

        if deno == 0:
            deno = 0.000001
        angle = np.arctan(num/deno)
        angle = angle * 180 / np.pi
        global_position = {
            'x': rx,
            'y': ry,
            'phi': angle
        }
        return global_position

