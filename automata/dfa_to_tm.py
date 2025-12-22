def dfa_to_tm(dfa):
    """
    Converts a DFA to a strict single-tape Deterministic Turing Machine (DTM).
    
    ACADEMIC MODEL:
    - States: Q_dfa U {q_accept, q_reject}
    - Moves: Right (R) only for this simulation.
    - Transitions:
        1. Input symbols: (q, a) -> (p, a, R) [Simulate DFA move]
        2. End of Input (_): 
           If q is accepting in DFA -> (q, _) -> (q_accept, _, R) [Halt & Accept]
           If q is NOT accepting    -> (q, _) -> (q_reject, _, R) [Halt & Reject]
    """
    tm_transitions = []
    
    # 1. Standard Input Transitions (Simulate DFA)
    for t in dfa["transitions"]:
        tm_transitions.append({
            "from": t["from"],
            "read": t["symbol"],
            "to": t["to"],
            "write": t["symbol"], # Read-only behavior on input
            "move": "R"
        })

    # 2. End-of-Input Transitions (Decide Acceptance)
    # We iterate over ALL DFA states to define behavior on Blank ('_')
    for state in dfa["states"]:
        is_accepting = state in dfa["accept"]
        
        target = "q_accept" if is_accepting else "q_reject"
        
        tm_transitions.append({
            "from": state,
            "read": "_",      # Blank symbol
            "to": target,
            "write": "_",     # Keep blank
            "move": "R"       # Move right (irrelevant as we halt)
        })

    # 3. Construct Final TM Structure
    # Add new special states
    all_states = dfa["states"] + ["q_accept", "q_reject"]
    
    return {
        "states": all_states,
        "start": dfa["start"],
        "accept": ["q_accept"], # Only explicit q_accept is the halting accept state
        "reject": ["q_reject"], # Explicit reject state
        "transitions": tm_transitions,
        "tape_alphabet": ["_"] # Implicitly includes input alphabet
    }
