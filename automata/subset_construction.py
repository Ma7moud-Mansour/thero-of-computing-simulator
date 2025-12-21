from simulation.nfa_simulator import epsilon_closure, move

def get_alphabet(nfa):
    """
    Extracts the alphabet from the NFA transitions.
    Excludes None (epsilon).
    """
    alphabet = set()
    for (state, symbol) in nfa.transitions.keys():
        if symbol is not None:
            alphabet.add(symbol)
    return sorted(list(alphabet))

def nfa_to_dfa(nfa):
    """
    Converts an NFA to a DFA using the Subset Construction Algorithm.
    
    Returns:
        dict: A dictionary representing the DFA structure.
        {
            "states": ["D0", "D1", ...],
            "transitions": [{"from": "D0", "to": "D1", "symbol": "a"}],
            "start_state": "D0",
            "accept_states": ["D1", ...],
            "state_map": {"D0": ["q0", "q1"], ...}
        }
    """
    
    # 1. Initial State: Epsilon closure of NFA start state
    start_closure, _ = epsilon_closure(nfa, {nfa.start_state})
    start_tuple = tuple(sorted([s.name for s in start_closure])) # Use state names for stability
    
    # Map: frozenset(state_names) -> DFA State ID "D{i}"
    # We use names to represent states to avoid object identity issues if any, 
    # but strictly we should use objects. However, names are unique in our normalized NFA.
    # Let's map {frozenset(names)} -> "D0"
    
    dfa_states = {} # { frozenset(names): "D0" }
    queue = []
    
    # Register Start State
    start_key = frozenset([s.name for s in start_closure])
    dfa_states[start_key] = "D0"
    queue.append(start_closure) # Store actual objects to pass to move/closure
    
    transitions = []
    alphabet = get_alphabet(nfa)
    
    processed_count = 0
    
    while queue:
        current_nfa_states = queue.pop(0)
        current_names = frozenset([s.name for s in current_nfa_states])
        current_id = dfa_states[current_names]
        
        for char in alphabet:
            # 2. Move(D, a)
            move_result, _ = move(nfa, current_nfa_states, char)
            
            if not move_result:
                # Dead state (implicitly handling or explicit?)
                # Standard DFA usually has total transitions, but for simplicity we often omit dead states
                # unless strict definition requires total function. 
                # Let's omit dead transitions for cleaner graph, unless it's an acceptor logic requirement.
                # Theory usually implies a sink state. But visualized DFAs often omit dead edges.
                # User asked for "Formal Definition". Formal DFA is a 5-tuple, delta is total.
                # However, usually we don't visualize the dead state explicitly if it clutters.
                # Let's skip for now, or add if "Dead State" needed.
                continue
            
            # 3. Epsilon Closure of Move Result
            next_closure, _ = epsilon_closure(nfa, move_result)
            next_names = frozenset([s.name for s in next_closure])
            
            if next_names not in dfa_states:
                new_id = f"D{len(dfa_states)}"
                dfa_states[next_names] = new_id
                queue.append(next_closure)
            
            target_id = dfa_states[next_names]
            
            transitions.append({
                "from": current_id,
                "to": target_id,
                "symbol": char
            })

    # 4. Identify Accept States
    # A DFA state is accepting if it contains ANY NFA accept state
    accept_ids = []
    nfa_accept_names = set([s.name for s in nfa.accept_states])
    
    state_map_serializable = {}
    
    for state_set, d_id in dfa_states.items():
        # state_set is frozenset of names
        state_map_serializable[d_id] = sorted(list(state_set))
        
        if not state_set.isdisjoint(nfa_accept_names):
            accept_ids.append(d_id)
            
    return {
        "states": sorted(list(dfa_states.values()), key=lambda x: int(x[1:])),
        "transitions": transitions,
        "start": "D0",
        "accept": sorted(accept_ids, key=lambda x: int(x[1:])),
        "state_map": state_map_serializable
    }
