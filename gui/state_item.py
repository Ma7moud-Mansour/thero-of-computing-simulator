from PySide6.QtWidgets import QGraphicsEllipseItem
from PySide6.QtGui import QPen, QBrush, QColor
from PySide6.QtCore import QRectF, Qt


class StateItem(QGraphicsEllipseItem):
    def __init__(self, state, x, y, accept=False):
        super().__init__(QRectF(x, y, 60, 60))
        self.state = state
        self.accept = accept

        pen = QPen(Qt.black, 2)
        brush = QBrush(QColor("#ffffff"))
        self.setPen(pen)
        self.setBrush(brush)

        if accept:
            inner = QGraphicsEllipseItem(6, 6, 48, 48, self)
            inner.setPen(QPen(Qt.black, 2))
