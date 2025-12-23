import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from regex.regex_parser import insert_concatenation
from regex.postfix import to_postfix
from regex.thompson import regex_to_nfa
from api.main import normalize_nfa, serialize_nfa

def get_nfa_structure(regex):
    concat = insert_concatenation(regex)
    postfix = to_postfix(concat)
    nfa = regex_to_nfa(postfix)
    normalize_nfa(nfa)
    return serialize_nfa(nfa)

regex = "(a|b)*ab"

print(f"Run 1: {regex}")
nfa1 = get_nfa_structure(regex)
print(f"Run 2: {regex}")
nfa2 = get_nfa_structure(regex)

# Compare States
states1 = sorted(nfa1["states"])
states2 = sorted(nfa2["states"])
if states1 != states2:
    print(f"ERROR: State sets differ!\n{states1}\n{states2}")
else:
    print("States set: MATCH")

# Compare Transitions
# We need to sort transitions to be comparable
def sort_trans(t):
    return (t["from"], t["symbol"], t["to"])

trans1 = sorted(nfa1["transitions"], key=sort_trans)
trans2 = sorted(nfa2["transitions"], key=sort_trans)

if trans1 != trans2:
    print("ERROR: Transitions differ!")
    for t1, t2 in zip(trans1, trans2):
        if t1 != t2:
            print(f"  Diff: {t1} vs {t2}")
else:
    print("Transitions: MATCH")

print(f"Total States: {len(states1)}")
print(f"Accept States: {nfa1['accept']}")
if nfa1['accept'] != nfa2['accept']:
     print(f"ERROR: Accept states differ! {nfa1['accept']} vs {nfa2['accept']}")
