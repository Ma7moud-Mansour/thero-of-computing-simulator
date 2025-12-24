def simulate_pda(pda, input_string):
    def epsilon_closure(states):
        stack = list(states)
        closure = set(states)
        transitions = []
        while stack:
            s = stack.pop()
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
                            "label": "ε, Z0 → Z0",
                            "read": "ε",
                            "pop": "Z0",
                            "push": "Z0"
                        })
        return closure, transitions

    def move(states, char):
        next_states = set()
        transitions = []        
        for s in states:
            key = (s, char, "Z0")
            if key in pda.transitions:
                targets = pda.transitions[key]
                for (t, push) in targets:
                    next_states.add(t)
                    transitions.append({
                        "from": s.name,
                        "to": t.name,
                        "label": f"{char}, Z0 → Z0",
                        "read": char,
                        "pop": "Z0",
                        "push": "Z0"
                    })
        return next_states, transitions
    
    history = []
    start_node = pda.start_state
    current_states, initial_epsilon = epsilon_closure({start_node})
    history.append({
        "step": "initial",
        "description": "Start & Initial ε-closure",
        "active": [s.name for s in current_states],
        "transitions": initial_epsilon,
        "stack": ["Z0"]
    })
    # 2. Process Input
    for char in input_string:
        move_dest, move_trans = move(current_states, char)
        next_active, epsilon_trans = epsilon_closure(move_dest)
        history.append({
            "step": "consume",
            "char": char,
            "description": f"Consume '{char}'",
            "active": [s.name for s in move_dest],
            "transitions": move_trans,
            "stack": ["Z0"]
        })
        if epsilon_trans or (not epsilon_trans and not move_trans):
             history.append({
                "step": "epsilon",
                "description": f"ε-closure after '{char}'",
                "active": [s.name for s in next_active],
                "transitions": epsilon_trans,
                "stack": ["Z0"]
            })
        else:
             history.append({
                "step": "epsilon",
                "description": "State Update",
                "active": [s.name for s in next_active],
                "transitions": [],
                "stack": ["Z0"]
            })  
        current_states = next_active

    # 3. Acceptance
    accepted = any(s in pda.accept_states for s in current_states)    
    return accepted, history

def simulate_general_pda(pda, input_string, accept_by_empty_stack=False):
    def format_stack(s):
        return list(s)
    start_node = pda.start_state
    start_stack = [pda.start_stack_symbol]
    MAX_STEPS = 1000
    queue = [ {
        "state": start_node,
        "stack": start_stack,
        "remaining": input_string,
        "history": [],
        "steps_count": 0
    } ]
    import heapq
    pq = []
    entry_count = 0
    initial_config = {
        "state": start_node,
        "stack": start_stack,
        "remaining": input_string,
        "history": [{
            "step": "initial",
            "description": "Start",
            "state": start_node.name,
            "stack": format_stack(start_stack),
            "remaining": input_string,
            "active": [start_node.name],
            "transitions": []
        }]
    }
    heapq.heappush(pq, (len(input_string), 0, entry_count, initial_config))
    entry_count += 1
    best_rejected_history = initial_config["history"]
    while pq:
        _, steps, _, config = heapq.heappop(pq)
        state = config["state"]
        stack = config["stack"]
        remaining = config["remaining"]
        history = config["history"]
        if len(remaining) == 0:
            if accept_by_empty_stack:
                if len(stack) == 0:
                    return True, history
            elif state in pda.accept_states:
                return True, history
        if steps > MAX_STEPS:
            continue
        possible_moves = []
        stack_top = stack[-1] if stack else None
        def get_next_configs(input_char_key, input_char_actual, consume_input):
            if stack_top is None: return []
            key = (state, input_char_key, stack_top)
            results = []
            if key in pda.transitions:
                for target, push in pda.transitions[key]:
                    new_stack = stack[:-1]
                    push_list = list(push) if push else []
                    final_stack = new_stack + list(reversed(push_list))
                    new_remaining = remaining[1:] if consume_input else remaining
                    action_desc = f"{'ε' if input_char_actual is None else input_char_actual}, {stack_top} → {''.join(push_list) if push_list else 'ε'}"
                    new_history_step = {
                        "step": steps + 1,
                        "state": target.name,
                        "description": action_desc,
                        "stack": format_stack(final_stack),
                        "remaining": new_remaining,
                        "active": [target.name],
                        "transitions": [{
                            "from": state.name,
                            "to": target.name,
                            "label": action_desc
                        }]
                    }                    
                    results.append({
                        "state": target,
                        "stack": final_stack,
                        "remaining": new_remaining,
                        "history": history + [new_history_step],
                        "steps_count": steps + 1
                    })
            return results

        possible_moves.extend(get_next_configs(None, None, False))        
        if remaining:
            char = remaining[0]
            possible_moves.extend(get_next_configs(char, char, True))            
        for pm in possible_moves:
            heapq.heappush(pq, (len(pm["remaining"]), pm["steps_count"], entry_count, pm))
            entry_count += 1
        if len(history) > len(best_rejected_history):
            best_rejected_history = history

    return False, best_rejected_history
