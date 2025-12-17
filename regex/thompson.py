from core.state import State
from automata.nfa import NFA

class Fragment:
    def __init__(self, start, accepts):
        self.start = start
        self.accepts = accepts

def regex_to_nfa(postfix):
    stack = []
    nfa = NFA()

    for char in postfix:
        if char.isalnum():
            s0 = State()
            s1 = State()
            nfa.states.update([s0, s1])
            nfa.alphabet.add(char)
            nfa.add_transition(s0, char, s1)
            stack.append(Fragment(s0, {s1}))

        elif char == ".":
            f2 = stack.pop()
            f1 = stack.pop()
            for a in f1.accepts:
                nfa.add_transition(a, None, f2.start)
            stack.append(Fragment(f1.start, f2.accepts))

        elif char == "|":
            f2 = stack.pop()
            f1 = stack.pop()
            start = State()
            end = State()
            nfa.states.update([start, end])
            nfa.add_transition(start, None, f1.start)
            nfa.add_transition(start, None, f2.start)
            for a in f1.accepts:
                nfa.add_transition(a, None, end)
            for a in f2.accepts:
                nfa.add_transition(a, None, end)
            stack.append(Fragment(start, {end}))

        elif char == "*":
            f = stack.pop()
            start = State()
            end = State()
            nfa.states.update([start, end])
            nfa.add_transition(start, None, f.start)
            nfa.add_transition(start, None, end)
            for a in f.accepts:
                nfa.add_transition(a, None, f.start)
                nfa.add_transition(a, None, end)
            stack.append(Fragment(start, {end}))

    final = stack.pop()
    nfa.start_state = final.start
    nfa.accept_states = final.accepts
    return nfa
