from core.state import State

def epsilon_closure(nfa, states):
    stack = list(states)
    closure = set(states)
    transitions = []
    while stack:
        s = stack.pop()
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

def move(nfa, states, symol):
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
        move_dest, move_trans = move(nfa, current_states, char)
        next_active, epsilon_trans = epsilon_closure(nfa, move_dest)
        history.append({
            "step": "consume",
            "char": char,
            "description": f"Consume '{char}'",
            "active": [s.name for s in move_dest],
            "transitions": move_trans
        })
        if epsilon_trans or len(move_dest) > 0:
             history.append({
                "step": "epsilon",
                "description": f"ε-closure after '{char}'",
                "active": [s.name for s in next_active],
                "transitions": epsilon_trans
            })
        else:
             if not epsilon_trans and not move_trans:
                  pass
             elif not epsilon_trans:
                   history.append({
                    "step": "epsilon",
                     "description": "State Update",
                    "active": [s.name for s in next_active],
                    "transitions": []
                })
        current_states = next_active
    accepted = any(s in nfa.accept_states for s in current_states)    
    return accepted, history
