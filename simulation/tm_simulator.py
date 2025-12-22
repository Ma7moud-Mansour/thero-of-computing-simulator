def simulate_tm(tm, input_string):
    """
    Simulates a Deterministic Turing Machine with strict halting conditions.
    
    Halting:
    - Stops IMMEDIATELY upon entering 'q_accept' or 'q_reject'.
    - Input tape is effectively infinite to the right, filled with '_'.
    """
    # Initialize Tape
    # We convert input string to list. Empty string = just blanks.
    tape = list(input_string) if input_string else []
    if not tape:
        tape = ["_"]
        
    head = 0
    current_state = tm["start"]
    history = []
    
    step_count = 0
    MAX_STEPS = 5000 # Safety limit for loops
    
    # Explicit Halting States
    ACCEPT_STATE = "q_accept"
    REJECT_STATE = "q_reject"
    
    # Record Initial State
    history.append({
        "step": step_count,
        "state": current_state,
        "tape": "".join(tape).replace("_", " "), # Visuals prefer space? stick to logic chars
        "tape_raw": "".join(tape), # raw for frontend logic
        "head": head,
        "description": "Initial State",
        "active": [current_state],
        "transitions": []
    })
    
    while step_count < MAX_STEPS:
        # Check Halting Conditions logic BEFORE reading (standard definition)
        # Actually standard def: enters state -> halts.
        if current_state == ACCEPT_STATE or current_state == REJECT_STATE:
            break

        step_count += 1
        
        # 1. Read Symbol
        if head < len(tape) and head >= 0:
            char_read = tape[head]
        else:
            char_read = "_" # Explicit Blank
            # Dynamically extend tape for visualization if we went past bounds
            if head >= len(tape):
                tape.append("_")
            
        # 2. Find Transition
        transition = None
        for t in tm["transitions"]:
            if t["from"] == current_state and t["read"] == char_read:
                transition = t
                break
        
        # Implicit Rejection (No transition defined)
        if not transition:
            # Transition to implicit reject, or just break?
            # User wants: "Missing transitions imply rejection"
            # We'll treat getting stuck as a reject outcome, but to show it distinctively:
            history.append({
                "step": step_count,
                "state": "REJECTED (No Transition)",
                "tape": "".join(tape),
                "head": head,
                "description": f"No transition for ({current_state}, '{char_read}') -> Halt & Reject",
                "active": [],
                "transitions": []
            })
            return False, history

        # 3. Apply Transition
        # Write
        tape[head] = transition["write"]
        
        # Move
        direction = transition["move"]
        if direction == "R":
            head += 1
        elif direction == "L":
            head -= 1
            if head < 0: head = 0 # Standard semi-infinite tape? Left bounded.
        
        prev_state = current_state
        current_state = transition["to"]
        
        # Log Step
        history.append({
            "step": step_count,
            "state": current_state,
            "tape": "".join(tape), # For simple view
            "head": head,
            "description": f"Read '{transition['read']}' → '{transition['write']}', {direction}",
            "active": [current_state],
            "transitions": [{
                "from": prev_state,
                "to": current_state,
                "label": f"{transition['read']} → {transition['write']}, {direction}"
            }]
        })
        
        # Immediate Check after transition (for loop termination)
        if current_state == ACCEPT_STATE:
            break
        if current_state == REJECT_STATE:
            break

    accepted = (current_state == ACCEPT_STATE)
    return accepted, history
