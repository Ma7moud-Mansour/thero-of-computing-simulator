from core.state import State

def epsilon_closure(nfa, states):
    """
    Computes the epsilon closure of a set of states.
    Returns: (closure_set, transitions_taken)
    """
    stack = list(states)
    closure = set(states)
    transitions = []

    while stack:
        s = stack.pop()
        # Check for epsilon transitions from s
        # Key in nfa.transitions is (state, symbol). Symbol is None for epsilon.
        if (s, None) in nfa.transitions:
            targets = nfa.transitions[(s, None)]
            for t in targets:
                if t not in closure:
                    closure.add(t)
                    stack.append(t)
                    transitions.append({
                        "from": s.name,
                        "to": t.name,
                        "symbol": "ε"
                    })
    
    return closure, transitions

def move(nfa, states, symbol):
    """
    Computes the set of states reachable from 'states' on input 'symbol'.
    Returns: (next_states, transitions_taken)
    """
    next_states = set()
    transitions = []

    for s in states:
        if (s, symbol) in nfa.transitions:
            targets = nfa.transitions[(s, symbol)]
            for t in targets:
                next_states.add(t)
                transitions.append({
                    "from": s.name,
                    "to": t.name,
                    "symbol": symbol
                })
    
    return next_states, transitions

def simulate_nfa(nfa, input_string):
    """
    Simulates the NFA on the input string using standard Epsilon-Closure method.
    Records every step for visualization.
    """
    history = []
    
    # 1. Initial State
    start_node = nfa.start_state
    
    # 2. Initial Epsilon Closure
    current_states, initial_epsilon_trans = epsilon_closure(nfa, {start_node})
    
    history.append({
        "step": "initial",
        "description": "Start & Initial ε-closure",
        "active": [s.name for s in current_states],
        "transitions": initial_epsilon_trans
    })

    # 3. Process Input
    for char in input_string:
        # A. Move (Consume Character)
        move_dest, move_trans = move(nfa, current_states, char)
        
        # Snapshot after Move (before epsilon closure) - Optional, but good for visualization
        # Ideally visualization shows the move happening.
        
        # B. Epsilon Closure on the destination states
        next_active, epsilon_trans = epsilon_closure(nfa, move_dest)
        
        # We combine Move + Epsilon for one logical "Step" in user's mind, 
        # or separate them. Let's separate for clarity if requested, 
        # but user wants "standard logic". standard is: next_state = epsilon_closure(move(current, c))
        
        # Let's record the "Consume" step which highlights the edge taken
        history.append({
            "step": "consume",
            "char": char,
            "description": f"Consume '{char}'",
            "active": [s.name for s in move_dest], # Transitional active states
            "transitions": move_trans
        })
        
        # Then record the results of epsilon closure (the set of states we imply we are in)
        if epsilon_trans or len(move_dest) > 0:
             # Only add epsilon step if there ARE epsilon moves or to update final active set
             history.append({
                "step": "epsilon",
                "description": f"ε-closure after '{char}'",
                "active": [s.name for s in next_active],
                "transitions": epsilon_trans
            })
        else:
             # If no epsilon transitions, the active set is just move_dest (which is next_active)
             # But we might want to update the 'active' list in the UI to be the Full Closure even if no edges added
             # Actually, move_dest might fail to include some states if we didn't run closure.
             # Wait, next_active IS the closure. So we should always report it.
             # IF move_trans was empty (stuck), next_active is empty.
             if not epsilon_trans and not move_trans:
                  # Rejected / Dead branch
                  pass
             elif not epsilon_trans:
                  # Just update active states without highlighting new edges
                   history.append({
                    "step": "epsilon",
                     "description": "State Update",
                    "active": [s.name for s in next_active],
                    "transitions": []
                })

        current_states = next_active

    # 4. Check Acceptance
    accepted = any(s in nfa.accept_states for s in current_states)
    
    return accepted, history
