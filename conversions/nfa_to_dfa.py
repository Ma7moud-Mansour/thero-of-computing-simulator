from automata.dfa import DFA
from simulation.nfa_simulator import epsilon_closure, move

def nfa_to_dfa(nfa):
    dfa = DFA()
    start = frozenset(epsilon_closure(nfa, {nfa.start_state}))
    states_map = {start: "Q0"}
    unmarked = [start]

    dfa.start_state = "Q0"
    dfa.states.add("Q0")

    while unmarked:
        current = unmarked.pop()
        current_name = states_map[current]

        for sym in nfa.alphabet:
            next_set = frozenset(
                epsilon_closure(nfa, move(nfa, current, sym))
            )
            if not next_set:
                continue

            if next_set not in states_map:
                name = f"Q{len(states_map)}"
                states_map[next_set] = name
                dfa.states.add(name)
                unmarked.append(next_set)

            dfa.transitions[(current_name, sym)] = states_map[next_set]

    for state_set, name in states_map.items():
        if any(s in nfa.accept_states for s in state_set):
            dfa.accept_states.add(name)

    dfa.alphabet = nfa.alphabet
    return dfa
