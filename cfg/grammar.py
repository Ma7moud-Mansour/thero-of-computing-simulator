class Grammar:
    def __init__(self, start):
        self.start = start
        self.productions = {}  # A -> list of RHS

    def add_production(self, lhs, rhs):
        if lhs not in self.productions:
            self.productions[lhs] = []
        self.productions[lhs].append(rhs)
