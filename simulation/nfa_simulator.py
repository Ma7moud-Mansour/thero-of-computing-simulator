def epsilon_closure(nfa, states):
    """
    Computes epsilon closure and tracks transitions taken.
    Returns: (closure_set, transitions_list)
    """
    stack = list(states)
    closure = set(states)
    transitions = []

    while stack:
        state = stack.pop()
        # Find epsilon transitions from this state
        key = (state, None)
        if key in nfa.transitions:
             targets = nfa.transitions[key]
             for t in targets:
                if t not in closure:
                    closure.add(t)
                    stack.append(t)
                    transitions.append({
                        "from": state.name,
                        "to": t.name,
                        "symbol": "ε"
                    })
                # Note: If we want to visualize loops or redundant paths, 
                # we might want to track even visited ones, 
                # but for closure set logic, we usually stop.
                # For visualization, showing the 'discovery' tree is usually enough.
                
    return closure, transitions


def move(nfa, states, symbol):
    """
    Computes next states for a symbol and tracks transitions.
    Returns: (next_states, transitions_list)
    """
    result = set()
    transitions = []
    
    for state in states:
        key = (state, symbol)
        if key in nfa.transitions:
            targets = nfa.transitions[key]
            for t in targets:
                result.add(t)
                transitions.append({
                    "from": state.name,
                    "to": t.name,
                    "symbol": symbol
                })
    return result, transitions


def simulate_nfa(nfa, input_string):
    """
    Simulates NFA and returns detailed history for key-frame animation.
    History structure:
    [
      { "active": [...], "transitions": [...], "step": "initial_epsilon" },
      { "active": [...], "transitions": [...], "step": "char", "char": "a" },
      { "active": [...], "transitions": [...], "step": "epsilon_after_char" },
      ...
    ]
    """
    
    # 1. Initial Epsilon Closure
    start_closure, start_transitions = epsilon_closure(nfa, {nfa.start_state})
    
    history = []
    
    # Record initial state
    history.append({
        "step": "initial",
        "active": [s.name for s in start_closure],
        "transitions": start_transitions
    })

    current_states = start_closure

    for char in input_string:
        # 2. Consume Character
        move_dest, move_trans = move(nfa, current_states, char)
        
        # Record move step
        history.append({
            "step": "consume",
            "char": char,
            "active": [s.name for s in move_dest], # These are active *after* move, *before* epsilon
            "transitions": move_trans
        })
        
        # 3. Epsilon Closure after move
        closure_dest, closure_trans = epsilon_closure(nfa, move_dest)
        current_states = closure_dest
        
        # Record epsilon step
        history.append({
            "step": "epsilon",
            "active": [s.name for s in current_states],
            "transitions": closure_trans
        })

    accepted = any(s in nfa.accept_states for s in current_states)
    return accepted, history
