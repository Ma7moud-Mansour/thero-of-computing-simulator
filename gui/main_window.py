from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QLineEdit, QPushButton
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Theory of Computing Visualizer")

        central = QWidget()
        layout = QVBoxLayout()

        self.regex_input = QLineEdit()
        self.regex_input.setPlaceholderText("Enter Regex")

        self.build_btn = QPushButton("Build NFA")

        layout.addWidget(self.regex_input)
        layout.addWidget(self.build_btn)

        central.setLayout(layout)
        self.setCentralWidget(central)
