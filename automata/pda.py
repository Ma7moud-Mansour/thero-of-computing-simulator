class PDA:
    def __init__(self):
        self.states = set()
        self.input_alphabet = set()
        self.stack_alphabet = set()
        self.transitions = {}
        # (state, input, stack_top) -> set((next_state, push_symbols))

        self.start_state = None
        self.accept_states = set()
        self.start_stack_symbol = "$"

    def add_transition(self, state, inp, stack_top, next_state, push):
        key = (state, inp, stack_top)
        if key not in self.transitions:
            self.transitions[key] = set()
        self.transitions[key].add((next_state, push))
