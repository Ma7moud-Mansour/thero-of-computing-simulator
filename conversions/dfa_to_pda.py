from automata.pda import PDA

def dfa_to_pda(dfa):
    pda = PDA()

    pda.states = dfa.states.copy()
    pda.input_alphabet = dfa.alphabet.copy()
    pda.start_state = dfa.start_state
    pda.accept_states = dfa.accept_states.copy()

    for (state, symbol), next_state in dfa.transitions.items():
        pda.add_transition(
            state,
            symbol,
            pda.start_stack_symbol,
            next_state,
            pda.start_stack_symbol
        )

    return pda
