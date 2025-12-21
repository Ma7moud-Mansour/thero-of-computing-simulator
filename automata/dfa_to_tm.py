def dfa_to_tm(dfa):
    """
    Converts a DFA to a Deterministic Turing Machine (DTM).
    The TM simulates the DFA by reading input from left to right,
    never modifying the tape (writes back the same symbol), 
    and moving Right.

    TM Structure:
    {
        "states": [...],
        "start": "...",
        "accept": [...],
        "transitions": [
            { "from": "q", "read": "a", "to": "p", "write": "a", "move": "R" }
        ],
        "alphabet": [...]
    }
    """
    tm_transitions = []
    
    # Copy transitions: (q, a) -> p BECOMES (q, a) -> (p, a, R)
    for t in dfa["transitions"]:
        tm_transitions.append({
            "from": t["from"],
            "read": t["symbol"],
            "to": t["to"],
            "write": t["symbol"], # DFA doesn't write, so we write back what we read
            "move": "R"
        })

    return {
        "states": dfa["states"],
        "start": dfa["start"],
        "accept": dfa["accept"],
        "transitions": tm_transitions,
        "input_alphabet": [], # Can be derived if needed
        "tape_alphabet": []   # TM extends input with '_'
    }
