def simulate_pda(pda, input_string):
    from collections import deque

    stack_start = [pda.start_stack_symbol]
    queue = deque()
    queue.append((pda.start_state, 0, stack_start))

    visited = set()

    while queue:
        state, pos, stack = queue.popleft()

        if (state, pos, tuple(stack)) in visited:
            continue
        visited.add((state, pos, tuple(stack)))

        if pos == len(input_string) and state in pda.accept_states:
            return True

        inp = input_string[pos] if pos < len(input_string) else None
        top = stack[-1] if stack else None

        for key in [
            (state, inp, top),
            (state, None, top)
        ]:
            if key in pda.transitions:
                for next_state, push in pda.transitions[key]:
                    new_stack = stack[:-1]
                    if push:
                        for c in reversed(push):
                            new_stack.append(c)

                    queue.append((
                        next_state,
                        pos + (inp is not None),
                        new_stack
                    ))

    return False
