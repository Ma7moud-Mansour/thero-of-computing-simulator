def epsilon_closure(nfa, states):
    stack = list(states)
    closure = set(states)

    while stack:
        state = stack.pop()
        for (s, sym), targets in nfa.transitions.items():
            if s == state and sym is None:
                for t in targets:
                    if t not in closure:
                        closure.add(t)
                        stack.append(t)
    return closure


def move(nfa, states, symbol):
    result = set()
    for state in states:
        key = (state, symbol)
        if key in nfa.transitions:
            result.update(nfa.transitions[key])
    return result


def simulate_nfa(nfa, input_string):
    current_states = epsilon_closure(nfa, {nfa.start_state})
    history = [current_states]

    for char in input_string:
        current_states = epsilon_closure(
            nfa,
            move(nfa, current_states, char)
        )
        history.append(current_states)

    accepted = any(s in nfa.accept_states for s in current_states)
    return accepted, history
