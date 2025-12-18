class TuringMachine:
    def __init__(self):
        self.transitions = {}
        self.start_state = None
        self.accept_states = set()
