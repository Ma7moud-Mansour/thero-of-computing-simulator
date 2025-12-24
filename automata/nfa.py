from core.automaton import Automaton

class NFA(Automaton):
    def __init__(self):
        super().__init__()
        self.transitions = {}

    def add_transition(self, from_state, symbol, to_state):
        key = (from_state, symbol)
        if key not in self.transitions:
            self.transitions[key] = set()
        self.transitions[key].add(to_state)
