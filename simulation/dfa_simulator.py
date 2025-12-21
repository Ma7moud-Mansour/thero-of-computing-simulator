def simulate_dfa(dfa_data, input_string):
    """
    Simulates a DFA given its structure (dict) and input string.
    Returns: (accepted: bool, history: list)
    """
    current_state = dfa_data["start"]
    history = []
    
    # Initial State
    history.append({
        "step": "initial",
        "description": "Start",
        "active": [current_state],
        "transitions": []
    })
    
    for char in input_string:
        # Find transition
        next_state = None
        for t in dfa_data["transitions"]:
            if t["from"] == current_state and t["symbol"] == char:
                next_state = t["to"]
                break
        
        if next_state:
            history.append({
                "step": "move",
                "char": char,
                "description": f"Read '{char}' -> {next_state}",
                "active": [next_state],
                "transitions": [{
                    "from": current_state, 
                    "to": next_state, 
                    "symbol": char
                }]
            })
            current_state = next_state
        else:
            # Trap / Dead state implicit
            history.append({
                "step": "dead",
                "char": char,
                "description": f"No transition for '{char}' (Dead)",
                "active": [],
                "transitions": []
            })
            return False, history

    accepted = current_state in dfa_data["accept"]
    return accepted, history
