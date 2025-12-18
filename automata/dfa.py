from core.automaton import Automaton


class DFA(Automaton):
    def __init__(self):
        super().__init__()
        self.transitions = {}  # (state, symbol) -> state
