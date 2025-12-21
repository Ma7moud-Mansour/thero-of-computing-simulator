def simulate_tm(tm, input_string):
    """
    Simulates a Single-Tape Turing Machine.
    Tape is dynamic.
    Blank symbol is '_'.
    """
    tape = list(input_string) if input_string else ["_"] # Ensure tape has at least one cell if empty? 
    # Actually empty string input means tape is just blanks? 
    # Standard: input is written on tape, rest is blanks.
    # We will simulate valid length.
    
    if not input_string:
        tape = ["_"]
    
    head = 0
    current_state = tm["start"]
    history = []
    
    step_count = 0
    MAX_STEPS = 1000 # Prevent infinite loops
    
    # Log Initial State
    history.append({
        "step": step_count,
        "state": current_state,
        "tape": "".join(tape),
        "head": head,
        "description": "Initial State",
        "active": [current_state], # For graph highlighting
        "transitions": []
    })
    
    while step_count < MAX_STEPS:
        step_count += 1
        
        # 1. Read Symbol
        if head < len(tape) and head >= 0:
            char_under_head = tape[head]
        else:
            char_under_head = "_" # Blank
            
        # 2. Find Transition
        transition = None
        for t in tm["transitions"]:
            if t["from"] == current_state and t["read"] == char_under_head:
                transition = t
                break
        
        # If no transition found for explicit blank or symbol, check Halt condition
        if not transition:
            # If current state is accept, we accept.
            # But usually TM halts -> Output.
            # Here we just stop.
            break
            
        # 3. Execute Transition
        # Write
        if head < len(tape) and head >= 0:
            tape[head] = transition["write"]
        elif head >= len(tape):
            # Extend tape to right
            tape.append(transition["write"])
            
        # Move
        move_dir = transition["move"]
        if move_dir == "R":
            head += 1
        elif move_dir == "L":
            head -= 1
            
        prev_state = current_state
        current_state = transition["to"]
        
        # Log Step
        history.append({
            "step": step_count,
            "state": current_state,
            "tape": "".join(tape).replace("_", " "), # Visual clean up? Or keep _? Let's keep _ for logic, replace in UI if needed. actually UI expects string.
            "head": head,
            "description": f"Read '{transition['read']}' → Write '{transition['write']}', Move {move_dir}",
            "active": [current_state],
            "transitions": [{
                "from": prev_state,
                "to": current_state,
                "label": f"{transition['read']} → {transition['write']}, {move_dir}"
            }]
        })
        
        # Check explicit accept halt (DFA-TM halts when entering accept? or consumes input?)
        # Since this is a DFA-converted TM, it mimics DFA. It consumes the string.
        # It will likely halt when it reads the blank after the string.
        # But our transition table only has alphabet symbols.
        # So it will Halt as soon as it reads '_'.
        
    accepted = current_state in tm["accept"]
    
    # Final cleanup: If we halted because we ran out of transitions (read blank), 
    # check if we are in accept state.
    
    return accepted, history
