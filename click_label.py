import numpy as np
from PyQt5.QtWidgets import QLabel


class ClickLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print('label', self.geometry())
        self.points = []

    def mousePressEvent(self, event):
        pos = event.pos()
        self.points.append(pos)

    def mouseMoveEvent(self, event):
        pos = event.pos()
        self.points.append(pos)

    def resizeEvent(self, a0) -> None:
        print(self.width())