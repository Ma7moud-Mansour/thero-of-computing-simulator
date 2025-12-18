from automata.pda import PDA

def cfg_to_pda(grammar):
    pda = PDA()
    q = "q"

    pda.states.add(q)
    pda.start_state = q
    pda.accept_states.add(q)

    pda.stack_alphabet.update(grammar.productions.keys())
    pda.start_stack_symbol = grammar.start

    for lhs, rhss in grammar.productions.items():
        for rhs in rhss:
            pda.add_transition(q, None, lhs, q, rhs)

    return pda
