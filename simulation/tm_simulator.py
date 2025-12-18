BLANK = "_"

def simulate_tm(tm, input_string):
    tape = list(input_string) + [BLANK]
    head = 0
    state = tm.start_state

    history = []

    while True:
        history.append((state, tape.copy(), head))

        symbol = tape[head]
        key = (state, symbol)

        if key not in tm.transitions:
            break

        next_state, write, move = tm.transitions[key]

        tape[head] = write
        state = next_state

        if move == "R":
            head += 1
            if head == len(tape):
                tape.append(BLANK)
        elif move == "L":
            head = max(0, head - 1)

        elif move == "S":
            break

    accepted = state in tm.accept_states
    return accepted, history

