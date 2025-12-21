from core.state import State
from automata.nfa import NFA

class Fragment:
    """
    Represents a partial NFA with a single start state and a set of accept states.
    For strict Thompson, usually there is exactly one accept state, but we support a set 
    just in case, which is then connected to the next state via integers.
    """
    def __init__(self, start, accepts):
        self.start = start
        self.accepts = accepts # Set of states

def regex_to_nfa(postfix_tokens):
    """
    Converts a postfix regex token list to an NFA using Strict Thompson's Construction.
    """
    stack = []
    
    # Create a blank NFA object just to hold the transitions/states as we build
    # But wait, our NFA class is built node-by-node. We typically just build the graph 
    # and wrap it in NFA at the end.
    
    # We need a container for the transitions if we want to use NFA.add_transition helper,
    # or we can just manipulate states directly since State objects hold their own data 
    # (assuming the existing backend uses State objects).
    # Let's check `core/state.py`.
    # Based on previous file reads, `NFA` class holds `transitions` dictionary.
    # So we should create a global `nfa` instance to store transitions? 
    # OR, we create the states and transitions, and at the end populate a new NFA object.
    
    # Better approach: Create a temporary NFA tracker.
    nfa = NFA() 
    # NFA init creates start_state. We might overwrite it.
    
    if not postfix_tokens:
        # Empty Regex -> Accepts Empty String
        # q0 (Start, Accept)
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
            
            # Concatenation: A . B
            # Link all f1.accepts -> f2.start with Epsilon
            for s in f1.accepts:
                nfa.add_transition(s, None, f2.start)
            
            # New Fragment: Start of A, Accept of B
            # (Strictly: A's accept states are no longer accepting)
            stack.append(Fragment(f1.start, f2.accepts))
            
        elif token == "|":
            if len(stack) < 2: return None # Error
            f2 = stack.pop()
            f1 = stack.pop()
            
            # Union: A | B
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
