def simulate_pda(pda, input_string):
    """
    Strict PDA Simulation (Wrapper around NFA logic).
    
    Behavior:
    - Identical state traversal to NFA (Epsilon-Closure).
    - Stack is INVARIANT: Always ['Z0'].
    - Transitions are strictly labeled: (input, Z0 -> Z0).
    """

    # -------------------------------------------------
    # Helper: Epsilon Closure (Reused Logic)
    # -------------------------------------------------
    def epsilon_closure(states):
        stack = list(states)
        closure = set(states)
        transitions = []
        
        while stack:
            s = stack.pop()
            # In our PDA structure (from nfa_to_pda), transitions are:
            # (state, input, stack_top) -> [(next_state, push)]
            # Epsilon input is None or "ε"
            # Stack top is ALWAYS "Z0" for this strict mode.
            
            # Key: (s, None, "Z0")
            key = (s, None, "Z0")
            if key in pda.transitions:
                targets = pda.transitions[key]
                for (t, push) in targets:
                    if t not in closure:
                        closure.add(t)
                        stack.append(t)
                        transitions.append({
                            "from": s.name,
                            "to": t.name,
                            "label": "ε, Z0 → Z0", # Strict Label
                            "read": "ε",
                            "pop": "Z0",
                            "push": "Z0"
                        })
        return closure, transitions

    # -------------------------------------------------
    # Helper: Move (Consume Char)
    # -------------------------------------------------
    def move(states, char):
        next_states = set()
        transitions = []
        
        for s in states:
            # Key: (state, char, "Z0")
            key = (s, char, "Z0")
            if key in pda.transitions:
                targets = pda.transitions[key]
                for (t, push) in targets:
                    next_states.add(t)
                    transitions.append({
                        "from": s.name,
                        "to": t.name,
                        "label": f"{char}, Z0 → Z0", # Strict Label
                        "read": char,
                        "pop": "Z0",
                        "push": "Z0"
                    })
        return next_states, transitions

    # -------------------------------------------------
    # Main Simulation Loop
    # -------------------------------------------------
    history = []
    
    # 1. Start
    start_node = pda.start_state
    # Epsilon allow from start? Yes.
    current_states, initial_epsilon = epsilon_closure({start_node})
    
    history.append({
        "step": "initial",
        "description": "Start & Initial ε-closure",
        "active": [s.name for s in current_states],
        "transitions": initial_epsilon,
        "stack": ["Z0"] # Invariant Stack
    })
    
    # 2. Process Input
    for char in input_string:
        # Move
        move_dest, move_trans = move(current_states, char)
        
        # Epsilon Closure
        next_active, epsilon_trans = epsilon_closure(move_dest)
        
        history.append({
            "step": "consume",
            "char": char,
            "description": f"Consume '{char}'",
            "active": [s.name for s in move_dest],
            "transitions": move_trans,
            "stack": ["Z0"] # Invariant Stack
        })
        
        if epsilon_trans or (not epsilon_trans and not move_trans):
             # Log epsilon step if we did closure OR if we died
             history.append({
                "step": "epsilon",
                "description": f"ε-closure after '{char}'",
                "active": [s.name for s in next_active],
                "transitions": epsilon_trans,
                "stack": ["Z0"] # Invariant Stack
            })
        else:
            # Just update state list
             history.append({
                "step": "epsilon",
                "description": "State Update",
                "active": [s.name for s in next_active],
                "transitions": [],
                "stack": ["Z0"] # Invariant Stack
            })
            
        current_states = next_active

    # 3. Acceptance
    accepted = any(s in pda.accept_states for s in current_states)
    
    return accepted, history
