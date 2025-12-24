def dfa_to_tm(dfa):
    """
    Converts a DFA to a strict single-tape Deterministic Turing Machine (DTM).
    

    """
    tm_transitions = []
    
    # 1. Standard Input Transitions (Simulate DFA)
    for t in dfa["transitions"]:
        tm_transitions.append({
            "from": t["from"],
            "read": t["symbol"],
            "to": t["to"],
            "write": t["symbol"],
            "move": "R"
        })

    # 2. End-of-Input Transitions (Decide Acceptance)
    # We iterate over ALL DFA states to define behavior on Blank ('_')
    for state in dfa["states"]:
        is_accepting = state in dfa["accept"]
        
        target = "q_accept" if is_accepting else "q_reject"
        
        tm_transitions.append({
            "from": state,
            "read": "_",
            "to": target,
            "write": "_",
            "move": "R"
        })

    # 3. Construct Final TM Structure
    all_states = dfa["states"] + ["q_accept", "q_reject"]
    
    return {
        "states": all_states,
        "start": dfa["start"],
        "accept": ["q_accept"], # Only explicit q_accept is the halting accept state
        "reject": ["q_reject"], # Explicit reject state
        "transitions": tm_transitions,
        "tape_alphabet": ["_"] # Implicitly includes input alphabet
    }
