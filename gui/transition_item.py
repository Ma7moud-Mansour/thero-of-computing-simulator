from PySide6.QtWidgets import QGraphicsLineItem, QGraphicsTextItem
from PySide6.QtGui import QPen
from PySide6.QtCore import Qt

class TransitionItem(QGraphicsLineItem):
    def __init__(self, x1, y1, x2, y2, label, epsilon=False):
        super().__init__(x1, y1, x2, y2)

        pen = QPen(Qt.black, 2)
        if epsilon:
            pen.setStyle(Qt.DashLine)

        self.setPen(pen)

        text = QGraphicsTextItem(label)
        text.setPos((x1 + x2) / 2, (y1 + y2) / 2)
        self.text = text
