def simulate_tm(tm, input_string):
    tape = list(input_string) if input_string else []
    if not tape:
        tape = ["_"]
        
    head = 0
    current_state = tm["start"]
    history = []
    
    step_count = 0
    MAX_STEPS = 5000
    ACCEPT_STATE = "q_accept"
    REJECT_STATE = "q_reject"

    history.append({
        "step": step_count,
        "state": current_state,
        "tape": "".join(tape).replace("_", " "),
        "tape_raw": "".join(tape),
        "head": head,
        "description": "Initial State",
        "active": [current_state],
        "transitions": []
    })
    
    while step_count < MAX_STEPS:
        if current_state == ACCEPT_STATE or current_state == REJECT_STATE:
            break

        step_count += 1
        
        # 1. Read Symbol
        if head < len(tape) and head >= 0:
            char_read = tape[head]
        else:
            char_read = "_"
            if head >= len(tape):
                tape.append("_")
            
        # 2. Find Transition
        transition = None
        for t in tm["transitions"]:
            if t["from"] == current_state and t["read"] == char_read:
                transition = t
                break
        

        if not transition:
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
        tape[head] = transition["write"]        
        direction = transition["move"]
        if direction == "R":
            head += 1
        elif direction == "L":
            head -= 1
            if head < 0: head = 0
        
        prev_state = current_state
        current_state = transition["to"]
        
        history.append({
            "step": step_count,
            "state": current_state,
            "tape": "".join(tape),
            "head": head,
            "description": f"Read '{transition['read']}' → '{transition['write']}', {direction}",
            "active": [current_state],
            "transitions": [{
                "from": prev_state,
                "to": current_state,
                "label": f"{transition['read']} → {transition['write']}, {direction}"
            }]
        })
        
        if current_state == ACCEPT_STATE:
            break
        if current_state == REJECT_STATE:
            break

    accepted = (current_state == ACCEPT_STATE)
    return accepted, history
