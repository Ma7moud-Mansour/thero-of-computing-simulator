import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from regex.regex_parser import insert_concatenation
from regex.postfix import to_postfix
from regex.thompson import regex_to_nfa
from api.main import normalize_nfa

regex = "(a|b)*ab"
concat = insert_concatenation(regex)
postfix = to_postfix(concat)
nfa = regex_to_nfa(postfix)
normalize_nfa(nfa) # Normalize to have readable names q0, q1...

print(f"States: {[s.name for s in nfa.states]}")
print(f"Start: {nfa.start_state.name}")
print(f"Accept: {[s.name for s in nfa.accept_states]}")
print("Transitions:")

sorted_transitions = sorted(nfa.transitions.items(), key=lambda x: (x[0][0].name, x[0][1] or ""))

for (state, symbol), targets in sorted_transitions:
    symbol_str = symbol if symbol else "Epsilon"
    target_names = [t.name for t in targets]
    print(f"  {state.name} --{symbol_str}--> {target_names}")

# Check for transitions FROM accept state
for s in nfa.accept_states:
    has_transitions = False
    for (src, sym), targets in nfa.transitions.items():
        if src == s:
             print(f"WARNING: Accept state {s.name} has outgoing transition on {sym} to {[t.name for t in targets]}")
             has_transitions = True
    if not has_transitions:
        print(f"Accept state {s.name} is terminal (Good).")
