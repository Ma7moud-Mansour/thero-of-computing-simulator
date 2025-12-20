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
            # Link all accept states of f1 to start of f2
            for a in f1.accepts:
                nfa.add_transition(a, None, f2.start)
            # Resulting fragment starts at f1.start and accepts at f2.accepts
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
            
            # Epsilon to start of fragment
            nfa.add_transition(start, None, f.start)
            # Epsilon to bypass fragment (0 occurrences)
            nfa.add_transition(start, None, end)
            
            for a in f.accepts:
                # Epsilon back to start (loop)
                nfa.add_transition(a, None, f.start)
                # Epsilon to end (break loop)
                nfa.add_transition(a, None, end)
            
            stack.append(Fragment(start, {end}))

    if not stack:
        return NFA() # Empty NFA if empty regex

    final = stack.pop()
    nfa.start_state = final.start
    nfa.accept_states = final.accepts
    return nfa
