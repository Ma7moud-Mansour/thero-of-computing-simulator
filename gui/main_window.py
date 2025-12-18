from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QLineEdit, QLabel, QMessageBox
)
from PySide6.QtCore import QTimer

from gui.canvas import AutomatonCanvas
from gui.state_item import StateItem
from gui.transition_item import TransitionItem
from gui.animations import glow_state

from regex.regex_parser import insert_concatenation
from regex.postfix import to_postfix
from regex.thompson import regex_to_nfa

from simulation.nfa_simulator import simulate_nfa
from simulation.tm_simulator import simulate_tm

from conversions.nfa_to_dfa import nfa_to_dfa
from conversions.dfa_to_tm import dfa_to_tm


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Theory of Computing Visualizer")

        # === Widgets ===
        self.canvas = AutomatonCanvas()
        self.regex_input = QLineEdit()
        self.regex_input.setPlaceholderText("Enter Regex")

        self.input_string = QLineEdit()
        self.input_string.setPlaceholderText("Enter Input String")

        self.build_btn = QPushButton("Build NFA")
        self.sim_btn = QPushButton("Simulate")

        self.step_btn = QPushButton("Step")
        self.play_btn = QPushButton("Play")
        self.reset_btn = QPushButton("Reset")

        self.demo_btn = QPushButton("🚀 Full Demo")

        self.tape_label = QLabel()
        self.tape_label.setStyleSheet(
            "font-family: monospace; font-size: 18px;"
        )

        self.stack_label = QLabel()
        self.stack_label.setStyleSheet(
            "font-family: monospace; font-size: 16px;"
        )

        # === Layout ===
        layout = QVBoxLayout()
        layout.addWidget(self.regex_input)
        layout.addWidget(self.input_string)
        layout.addWidget(self.build_btn)
        layout.addWidget(self.sim_btn)
        layout.addWidget(self.step_btn)
        layout.addWidget(self.play_btn)
        layout.addWidget(self.reset_btn)
        layout.addWidget(self.demo_btn)
        layout.addWidget(self.canvas)
        layout.addWidget(self.tape_label)
        layout.addWidget(self.stack_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # === Signals ===
        self.build_btn.clicked.connect(self.build_nfa)
        self.sim_btn.clicked.connect(self.simulate)
        self.step_btn.clicked.connect(self.step)
        self.play_btn.clicked.connect(self.play)
        self.reset_btn.clicked.connect(self.reset)
        self.demo_btn.clicked.connect(self.run_demo)

    # ================= NFA =================

    def build_nfa(self):
        regex = self.regex_input.text().strip()
        regex = insert_concatenation(regex)
        postfix = to_postfix(regex)
        self.nfa = regex_to_nfa(postfix)
        self.draw_nfa()

    def draw_nfa(self):
        self.canvas.clear()
        positions = self.canvas.circular_layout(self.nfa.states)

        self.state_items = {}
        for state, (x, y) in positions.items():
            item = StateItem(
                state, x, y,
                accept=(state in self.nfa.accept_states)
            )
            self.canvas.scene.addItem(item)
            self.state_items[state] = item

        for (s, sym), targets in self.nfa.transitions.items():
            for t in targets:
                x1, y1 = positions[s]
                x2, y2 = positions[t]
                label = sym if sym else "ε"

                tr = TransitionItem(
                    x1 + 30, y1 + 30,
                    x2 + 30, y2 + 30,
                    label,
                    epsilon=(sym is None)
                )
                self.canvas.scene.addItem(tr)
                self.canvas.scene.addItem(tr.text)

    # ================= Simulation =================

    def simulate(self):
        if not hasattr(self, "nfa"):
            QMessageBox.warning(
                self,
                "Error",
                "Please build the NFA first."
            )
            return

        self.accepted, self.history = simulate_nfa(
            self.nfa,
            self.input_string.text().strip()
        )
        self.step_index = 0


    def step(self):
        if self.step_index >= len(self.history):
            return

        for item in self.state_items.values():
            item.setOpacity(0.3)

        for state in self.history[self.step_index]:
            glow_state(self.state_items[state])

        self.step_index += 1

    def play(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.step)
        self.timer.start(800)

    def reset(self):
        if hasattr(self, "timer"):
            self.timer.stop()
        for item in self.state_items.values():
            item.setOpacity(1.0)
        self.step_index = 0

    # ================= TM =================

    def draw_tape(self, tape, head):
        self.tape_label.setText(
            "".join(
                f"[{c}]" if i == head else f" {c} "
                for i, c in enumerate(tape)
            )
        )

    def simulate_tm_gui(self):
        self.tm_accepted, self.tm_history = simulate_tm(
            self.tm,
            self.input_string.text()
        )
        self.tm_step_index = 0

    # ================= Demo =================

    def run_demo(self):
        self.build_nfa()
        self.simulate()
        self.play()

        self.dfa = nfa_to_dfa(self.nfa)
        self.tm = dfa_to_tm(self.dfa)

        self.simulate_tm_gui()
