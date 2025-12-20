def insert_concatenation(regex):
    result = ""
    operators = set("|*()")
    for i in range(len(regex)):
        c1 = regex[i]
        result += c1

        if i + 1 < len(regex):
            c2 = regex[i + 1]
            if (c1 not in "|(." and
                c2 not in "|)*."):
                result += "."
    return result
