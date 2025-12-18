from automata.pda import PDA

def nfa_to_pda(nfa):
    pda = PDA()

    pda.states = nfa.states.copy()
    pda.input_alphabet = nfa.alphabet.copy()
    pda.start_state = nfa.start_state
    pda.accept_states = nfa.accept_states.copy()

    for (state, symbol), targets in nfa.transitions.items():
        for t in targets:
            pda.add_transition(
                state,
                symbol,
                pda.start_stack_symbol,
                t,
                pda.start_stack_symbol
            )

    return pda
