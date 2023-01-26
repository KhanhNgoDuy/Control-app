import cv2
import numpy as np
from PyQt5.QtCore import pyqtSignal, QThread, pyqtSlot, Qt
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor
from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication, QPushButton
from PyQt5.uic import loadUi

import serial

from camera_thread import CameraThread, FakeCamThread
from image_processing_thread import ImageProcessingThread


class MainWindow(QMainWindow):
    image_ready = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        # Set up connection with the serial port
        self.ser = serial.Serial('COM3', 9600)

        # Set up UI
        self.ui = loadUi('untitled.ui', self)
        self.label = self.findChild(QLabel, "label")
        self.send_button = self.findChild(QPushButton, 'send_button')
        self.delete_button = self.findChild(QPushButton, 'delete_button')
        self.add_button = self.findChild(QPushButton, 'add_button')

        self.send_button.clicked.connect(self.send_position)
        self.delete_button.clicked.connect(self.delete_data)
        self.add_button.clicked.connect(self.add_data)

        # Create attributes
        self.image = None
        self.pixmap = None
        self.points = []

        #Create threads
        self.create_camera_thread()
        self.create_image_processing_thread()
        self.camera_thread.start()
        self.processing_thread.start()

    @pyqtSlot(dict)
    def print_position(self, position_dict):
        for key in position_dict.keys():
            print(position_dict[key], end='\t')
        print()

    @pyqtSlot(np.ndarray)
    def get_image(self, rgb_image):
        self.image = rgb_image
        self.image_ready.emit(self.image)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.pixmap = QPixmap.fromImage(qt_image)

        painter = QPainter(self.pixmap)
        painter.setPen(QColor(255, 0, 0))

        for point in self.points:
            painter.drawPoint(point)
        painter.end()

        self.label.setPixmap(self.pixmap)
        self.label.setAlignment(Qt.AlignRight)
        self.label.setScaledContents(True)

    def mousePressEvent(self, event):
        w, h = self.width(), self.height()
        wl, hl = self.label.width(), self.label.height()

        # scale = [0.887, 0.841]
        scale = [1, 1]

        pos = event.pos()
        pos.setX(int(np.round(pos.x() * scale[0] * w/wl)))
        pos.setY(int(np.round(pos.y() * scale[1] * h/hl)))
        self.points.append(pos)

    def mouseMoveEvent(self, event):
        w, h = self.width(), self.height()
        wl, hl = self.label.width(), self.label.height()

        # scale = [0.887, 0.841]
        scale = [1, 1]

        pos = event.pos()
        pos.setX(int(np.round(pos.x() * scale[0] * w/wl)))
        pos.setY(int(np.round(pos.y() * scale[1] * h/hl)))
        self.points.append(pos)

    # Set up connection with CameraThread
    def create_camera_thread(self):
        # self.camera = CameraThread()
        self.camera = FakeCamThread()
        self.camera.image_signal.connect(self.get_image)

        self.camera_thread = QThread()
        self.camera.moveToThread(self.camera_thread)
        self.camera_thread.started.connect(self.camera.run)

    # Set up connection with ImageProcessingThread
    def create_image_processing_thread(self):
        self.position_extractor = ImageProcessingThread()
        self.image_ready.connect(self.position_extractor.extract_position)
        self.position_extractor.position_signal.connect(self.print_position)  # --> TEST THE POSITION FEEDBACK

        self.processing_thread = QThread()
        self.position_extractor.moveToThread(self.processing_thread)

    def send_data(self):
        self.ser.write(self.points)

    def delete_data(self):
        self.points.clear()

    def add_data(self):
        pass


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
