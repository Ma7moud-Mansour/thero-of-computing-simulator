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

def simulate_general_pda(pda, input_string, accept_by_empty_stack=False):
    """
    General PDA Simulation.
    Supports:
    - Stack operations (Push tuple/string, Pop symbol)
    - Non-deterministic epsilon transitions
    - Terminal matching against Input
    
    Structure of transitions in 'pda':
    - keys: (state, input_char, stack_top)  -> input_char can be None (epsilon)
    - values: list of (next_state, push_content)
    """
    
    # helper to format stack for history
    def format_stack(s):
        return list(s)
        
    start_node = pda.start_state
    start_stack = [pda.start_stack_symbol]
    
    # State: { "state": node, "stack": [...] }
    # We need to track paths. BFS/DFS? 
    # Since we want to find *an* accepting path (or all for debugging?), let's do BFS for shortest path or exploration.
    # But for a simulator that shows "steps", we usually just show one successful path or trace all?
    # The existing simulators (NFA) show "active states".
    # For PDA, "active configuration" includes stack. Infinite state space possible.
    # We cannot show "all active states" easily if stacks diverge.
    
    # Compromise: Depth-First Search to find ONE accepting path.
    # If found, return that history.
    # If not, return the longest path or a failure message.
    
    # Limit steps to prevent infinite loops (e.g., epsilon loops pushing to stack)
    MAX_STEPS = 1000
    
    queue = [ {
        "state": start_node,
        "stack": start_stack,
        "remaining": input_string,
        "history": [],
        "steps_count": 0
    } ]
    
    # Priority Queue might be better to prefer consuming input?
    # Let's try simple DFS/BFS. DFS is better for finding a deep accept, but BFS finds shortest.
    # Standard NFA sim does "parallel" simulation.
    # For PDA, we can't easily merge configurations (state, stack).
    # Let's try to find *an* acceptance trace.
    
    import heapq
    # (heuristic_cost, step_count, entry_id, config)
    # Heuristic: len(remaining_input)
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
            "active": [start_node.name], # For UI comp
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
        
        # Check Acceptance
        # Accept if: Input empty AND (Accept State OR Empty Stack if that's the mode, but usually accept state for this proj)
        if len(remaining) == 0:
            if accept_by_empty_stack:
                if len(stack) == 0:
                    return True, history
            elif state in pda.accept_states:
                return True, history
        
        if steps > MAX_STEPS:
            continue
            
        # Possible Moves
        # 1. Epsilon Input Transisions (state, None, stack_top)
        # 2. Real Input Transitions (state, char, stack_top) (only if remaining > 0)
        
        possible_moves = []
        
        stack_top = stack[-1] if stack else None
        
        # Helper to apply transition
        def get_next_configs(input_char_key, input_char_actual, consume_input):
            if stack_top is None: return [] # Cannot pop empty stack usually (unless logic allows?)
            # Usually transition requires stack top.
            
            key = (state, input_char_key, stack_top)
            results = []
            if key in pda.transitions:
                for target, push in pda.transitions[key]:
                    # Construct new stack
                    # Pop stack_top (already accessed)
                    new_stack = stack[:-1]
                    # Push new symbols
                    # push is tuple or string. If tuple ('S', 'a'), usually 'S' is first pushed? 
                    # Standard PDA: Push "ABC" -> C on top? Or A on top?
                    # In `cfg_to_pda`: push_content = tuple(rhs).
                    # If rhs is "AB", we want to match A then B.
                    # So A should be top.
                    # If stack is ..., and we push A, B. Stack becomes ..., B, A. 
                    # Wait. If derive S -> AB. Buffer: A B.
                    # We match A then B.
                    # So A needs to be on top.
                    # If we perform operations: Pop S, Push B, Push A. Top is A.
                    # So we reverse the push content when extending list.
                    
                    push_list = list(push) if push else []
                    # push_list is [A, B]. We want A at end of list (top).
                    # So extend with REVERSED push list?
                    # Example: S -> a S b. Push: a, S, b.
                    # We want 'a' on top.
                    # So list should be [..., b, S, a].
                    # So reverse `push`.
                    
                    final_stack = new_stack + list(reversed(push_list))
                    
                    # New remaining
                    new_remaining = remaining[1:] if consume_input else remaining
                    
                    # Log
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

        # 1. Epsilon moves
        possible_moves.extend(get_next_configs(None, None, False))
        
        # 2. Input moves
        if remaining:
            char = remaining[0]
            possible_moves.extend(get_next_configs(char, char, True))
            
        for pm in possible_moves:
            # Heuristic: shorter remaining string is better
            heapq.heappush(pq, (len(pm["remaining"]), pm["steps_count"], entry_count, pm))
            entry_count += 1
            
        # Keep track of longest path for rejection info
        if len(history) > len(best_rejected_history):
            best_rejected_history = history

    return False, best_rejected_history
