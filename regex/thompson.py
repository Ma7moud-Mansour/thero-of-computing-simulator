from core.state import State
from automata.nfa import NFA

class Fragment:

    def __init__(self, start, accepts):
        self.start = start
        self.accepts = accepts # Set of states

def regex_to_nfa(postfix_tokens):
    stack = []
    
    nfa = NFA() 
    
    if not postfix_tokens:
        s0 = State()
        nfa.states.add(s0)
        nfa.start_state = s0
        nfa.accept_states.add(s0)
        return nfa

    for token in postfix_tokens:
        if token == ".":
            if len(stack) < 2: return None # Error
            f2 = stack.pop()
            f1 = stack.pop()
            
            for s in f1.accepts:
                nfa.add_transition(s, None, f2.start)
            
            stack.append(Fragment(f1.start, f2.accepts))
            
        elif token == "|":
            if len(stack) < 2: return None # Error
            f2 = stack.pop()
            f1 = stack.pop()
            
            # 1. New Start State s0
            s0 = State()
            nfa.states.add(s0)
            
            # 2. s0 -> epsilon -> A.start
            nfa.add_transition(s0, None, f1.start)
            
            # 3. s0 -> epsilon -> B.start
            nfa.add_transition(s0, None, f2.start)
            
            # 4. New Accept State f0
            f0 = State()
            nfa.states.add(f0)
            
            # 5. A.accepts -> epsilon -> f0
            for s in f1.accepts:
                nfa.add_transition(s, None, f0)
                
            # 6. B.accepts -> epsilon -> f0
            for s in f2.accepts:
                nfa.add_transition(s, None, f0)
                
            stack.append(Fragment(s0, {f0}))
            
        elif token == "*":
            if not stack: return None # Error
            f1 = stack.pop()
            
            # Kleene Star: A*
            # 1. New Start s0
            s0 = State()
            nfa.states.add(s0)
            
            # 2. New Accept f0
            f0 = State()
            nfa.states.add(f0)
            
            # 3. s0 -> epsilon -> A.start
            nfa.add_transition(s0, None, f1.start)
            
            # 4. s0 -> epsilon -> f0 (Empty string case)
            nfa.add_transition(s0, None, f0)
            
            # 5. A.accepts -> epsilon -> f0 (Exit)
            for s in f1.accepts:
                nfa.add_transition(s, None, f0)
                
            # 6. A.accepts -> epsilon -> A.start (Loop)
            for s in f1.accepts:
                nfa.add_transition(s, None, f1.start)
                
            stack.append(Fragment(s0, {f0}))
            
        else:
            # Literal Character
            s_start = State()
            s_end = State()
            nfa.states.add(s_start)
            nfa.states.add(s_end)
            
            nfa.add_transition(s_start, token, s_end)
            
            stack.append(Fragment(s_start, {s_end}))
            
    if not stack:
        return None
        
    final_fragment = stack.pop()
    nfa.start_state = final_fragment.start
    nfa.accept_states = final_fragment.accepts
    
    return nfa
