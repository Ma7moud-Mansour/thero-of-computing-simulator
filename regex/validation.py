import string

def validate_regex(regex: str) -> bool:
    """
    Validates a regular expression based on strict formal language rules.
    Raises ValueError with specific message if invalid.
    Returns True if valid.
    """
    if not regex:
        raise ValueError("Empty regular expression")

    # 1. Allowed Alphabet
    # Alphanumeric + union(|) + star(*) + parens()
    # Note: We treat space as invalid unless explicit epsilon is needed, 
    # but for standard regex input spaces are usually ignored or invalid. 
    # Strict rule: No spaces allowed based on user prompt "Any other character is invalid".
    valid_chars = set(string.ascii_letters + string.digits + "|*()")
    for i, char in enumerate(regex):
        if char not in valid_chars:
            raise ValueError(f"Illegal character '{char}' at position {i}")

    # 2. Parentheses Validation
    balance = 0
    for i, char in enumerate(regex):
        if char == '(':
            balance += 1
            # Check for empty parens "()"
            if i + 1 < len(regex) and regex[i+1] == ')':
                raise ValueError(f"Empty parentheses '()' at position {i}")
        elif char == ')':
            balance -= 1
            if balance < 0:
                raise ValueError(f"Unmatched closing parenthesis at position {i}")
    
    if balance != 0:
        raise ValueError("Unmatched opening parenthesis")

    # 3. Operator Placement Rules
    # | (Union)
    if regex[0] == '|':
        raise ValueError("Union operator '|' cannot be at the start")
    if regex[-1] == '|':
        raise ValueError("Union operator '|' cannot be at the end")

    # * (Kleene Star)
    if regex[0] == '*':
        raise ValueError("Kleene star '*' cannot be at the start")

    for i, char in enumerate(regex):
        # Context checks
        prev = regex[i-1] if i > 0 else None
        next_char = regex[i+1] if i < len(regex) - 1 else None

        if char == '|':
            if prev == '(':
                raise ValueError(f"Union operator '|' cannot immediately follow '(' at position {i}")
            if next_char == ')':
                raise ValueError(f"Union operator '|' cannot immediately precede ')' at position {i}")
            if next_char == '|':
                raise ValueError(f"Double union operator '||' at position {i}")
            if next_char == '*':
                raise ValueError(f"Invalid sequence '|*' at position {i}")

        if char == '*':
            # Must apply to something
            if prev in ['(', '|']:
                raise ValueError(f"Kleene star '*' cannot follow '{prev}' at position {i}")
            # Double star
            if next_char == '*':
                raise ValueError(f"Double Kleene star '**' at position {i}")

    return True
