def simulate_dfa(dfa_data, input_string):
    """
    Simulates a DFA given its structure (dict) and input string.
    Returns: (accepted: bool, history: list)
    """
    current_state = dfa_data["start_state"]
    history = []
    
    history.append({
        "step": "initial",
        "state": current_state,
        "description": "Start"
    })
    
    for char in input_string:
        # Find transition
        # Deterministic: Only one transition per symbol
        next_state = None
        for t in dfa_data["transitions"]:
            if t["from"] == current_state and t["symbol"] == char:
                next_state = t["to"]
                break
        
        if next_state:
            history.append({
                "step": "move",
                "char": char,
                "from": current_state,
                "to": next_state,
                "description": f"Read '{char}' -> {next_state}"
            })
            current_state = next_state
        else:
            # Trap / Dead state implicit
            history.append({
                "step": "dead",
                "char": char,
                "from": current_state,
                "description": f"No transition for '{char}' (Dead)"
            })
            return False, history

    accepted = current_state in dfa_data["accept_states"]
    return accepted, history
