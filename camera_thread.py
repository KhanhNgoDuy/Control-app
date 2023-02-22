import numpy as np
import cv2
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication

# import time


class CameraThread(QObject):
    image_signal = pyqtSignal(np.ndarray)
    finished = pyqtSignal()

    def __init__(self, _id, label):
        super().__init__()
        self.id = _id
        self.label = label
        self.stop_cmd = False

    def run(self):
        print('camera running')
        cap = cv2.VideoCapture(self.id)
        while True:
            ret, frame = cap.read()
            # print(ret)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.image_signal.emit(cv2.resize(frame, (self.label.width(), self.label.height())))

        cap.release()
        print("stopped")
        self.finished.emit()


class FakeCamThread(QObject):
    image_signal = pyqtSignal(np.ndarray)
    finished = pyqtSignal()

    def __init__(self, path='images/rotate.mp4'):
        super().__init__()
        self.stop_cmd = False
        self.path = path

    def run(self):
        # print('camera running')
        cap = cv2.VideoCapture(self.path)
        while True:
            ret, frame = cap.read()

            if not ret:
                break

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.image_signal.emit(frame)
        print("stopped")
        self.finished.emit()


class TestWindow(QMainWindow):
    stop_cmd = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

        self.camera = CameraThread()
        self.camera.image_signal.connect(self.show_image)
        self.camera.finished.connect(self.destroy_window)

        self.thread = QThread()
        self.camera.moveToThread(self.thread)
        self.thread.started.connect(self.camera.run)
        self.thread.start()

    def show_image(self, image):
        cv2.imshow("1", image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.camera.stop_cmd = True

    @staticmethod
    def destroy_window():
        print('released the camera')
        cv2.destroyAllWindows()


if __name__ == "__main__":
    app = QApplication([])
    window = TestWindow()
    app.exec_()
