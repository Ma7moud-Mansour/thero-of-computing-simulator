from automata.pda import PDA
from core.state import State

def cfg_to_pda(grammar):
    pda = PDA()
    q = State("q")

    pda.states.add(q)
    pda.start_state = q
    pda.accept_states.add(q)

    pda.stack_alphabet.update(grammar.productions.keys())
    pda.start_stack_symbol = grammar.start

    
    terminals = set()
    for lhs, rhss in grammar.productions.items():
        for rhs in rhss:
            # Note: stored as (state, input, stack_top) -> (next_state, push)
            # Ensure push is hashable (tuple)
            push_content = tuple(rhs) if isinstance(rhs, list) else (rhs,)
            if len(push_content) == 1 and push_content[0] == "": 
                push_content = () # empty tuple for epsilon

            pda.add_transition(q, None, lhs, q, push_content)
            
            # Collect terminals from RHS
            for symbol in rhs:
                if symbol not in grammar.productions:
                    terminals.add(symbol)

    # 2. Terminals: (q, a, a) -> (q, ε)
    pda.input_alphabet.update(terminals)
    pda.stack_alphabet.update(terminals)
    
    for t in terminals:
        pda.add_transition(q, t, t, q, "")

    return pda
