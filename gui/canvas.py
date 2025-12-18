from PySide6.QtWidgets import QGraphicsScene, QGraphicsView
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
import math


class AutomatonCanvas(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # ✅ السطر الصح
        self.setRenderHint(QPainter.Antialiasing)

        self.setAlignment(Qt.AlignCenter)

    def clear(self):
        self.scene.clear()

    def circular_layout(self, states, center_x=400, center_y=300, radius=200):
        positions = {}
        states = list(states)
        n = len(states)

        for i, state in enumerate(states):
            angle = 2 * math.pi * i / n
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            positions[state] = (x, y)

        return positions
