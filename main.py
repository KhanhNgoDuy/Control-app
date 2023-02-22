import cv2
import numpy as np
from PyQt5.QtCore import pyqtSignal, QThread, pyqtSlot, Qt
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QPen
from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication, QPushButton
from PyQt5.uic import loadUi
from click_label import ClickLabel

import serial

from camera_thread import CameraThread, FakeCamThread
from image_processing_thread import ImageProcessingThread


class MainWindow(QMainWindow):
    image_ready = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        # Set up connection with the serial port
        # self.ser = serial.Serial('COM8', 9600)

        # Set up UI
        self.ui = loadUi('untitled.ui', self)
        self.label = self.findChild(ClickLabel, "label")

        self.send_button = self.findChild(QPushButton, 'send_button')
        self.delete_button = self.findChild(QPushButton, 'delete_button')
        self.add_button = self.findChild(QPushButton, 'add_button')

        self.send_button.clicked.connect(self.send_data)
        self.delete_button.clicked.connect(self.delete_data)
        self.add_button.clicked.connect(self.add_data)

        # Create attributes
        self.image = None
        self.pixmap = None

        # Create threads
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

        pen = QPen(Qt.green)
        pen.setWidth(5)

        painter = QPainter(self.pixmap)
        # painter.setPen(QColor(255, 0, 0))
        painter.setPen(pen)

        for point in self.label.points:
            painter.drawPoint(point)
        painter.end()

        self.label.setPixmap(self.pixmap)

    # Set up connection with CameraThread
    def create_camera_thread(self):
        self.camera = CameraThread(1, self.label)
        # self.camera = FakeCamThread()
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
        print(self.label.points)
        # self.ser.write(b'Hello from Python')
        # self.ser.write(self.label.points)

    def delete_data(self):
        self.label.points.clear()

    def add_data(self):
        pass


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
