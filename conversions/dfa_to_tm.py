from automata.tm import TuringMachine

BLANK = "_"

def dfa_to_tm(dfa):
    tm = TuringMachine()

    tm.start_state = dfa.start_state
    tm.accept_states = dfa.accept_states.copy()

    for (state, symbol), next_state in dfa.transitions.items():
        tm.transitions[(state, symbol)] = (next_state, symbol, "R")

    # End of input handling
    for state in dfa.states:
        tm.transitions[(state, BLANK)] = (
            state,
            BLANK,
            "S"  # Stay
        )

    return tm
