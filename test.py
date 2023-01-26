import sys

from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication


class Object1(QObject):
    signal = pyqtSignal(str)

    @pyqtSlot(str)
    def received(self, input_str):
        print(input_str)
        self.signal.emit("From Object 1")


class Object2(QObject):
    signal = pyqtSignal(str)

    @pyqtSlot(str)
    def received(self, input_str):
        print(input_str)
        self.signal.emit("From Object 2")


class MainObject(QMainWindow):
    main_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.obj1 = Object1()
        self.thread1 = QThread()
        self.obj1.signal.connect(self.func1)
        self.main_signal.connect(self.obj1.received)
        self.obj1.moveToThread(self.thread1)
        self.thread1.start()

        # self.obj2 = Object2()
        # self.thread2 = QThread()
        # self.obj2.signal.connect(self.func2)
        # self.main_signal.connect(self.obj2.received)
        # self.obj2.moveToThread(self.thread2)
        # self.thread2.start()

        self.func1("First 1")
        # self.func2("First 2")

    def func1(self, input_str):
        print(input_str)
        self.main_signal.emit("Main --> 1")

    # def func2(self, input_str):
    #     print(input_str)
    #     self.main_signal.emit("Main --> 2")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainObject()
    sys.exit(app.exec())


