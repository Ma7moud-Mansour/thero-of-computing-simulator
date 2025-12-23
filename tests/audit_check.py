import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from regex.regex_parser import insert_concatenation
from regex.postfix import to_postfix
from regex.thompson import regex_to_nfa
from simulation.nfa_simulator import simulate_nfa
from api.main import normalize_nfa

def test_audit(regex, tests):
    print(f"\n--- Auditing: {regex} ---")
    concat = insert_concatenation(regex)
    postfix = to_postfix(concat)
    nfa = regex_to_nfa(postfix)
    normalize_nfa(nfa)
    
    print(f"  Concat: {concat}")
    print(f"  Postfix: {postfix}")
    print(f"  States: {[s.name for s in nfa.states]}")
    print(f"  Start: {nfa.start_state.name}, Accept: {[s.name for s in nfa.accept_states]}")
    
    # Check for invalid backward edges from accept states logic?
    # Not easily programmatically checked without graph traversal, but manual simulation does it.
    
    all_pass = True
    for s, expected in tests:
        accepted, _ = simulate_nfa(nfa, s)
        res_str = "PASS" if accepted == expected else "FAIL"
        print(f"  [{res_str}] Input '{s}' -> {accepted} (Expected: {expected})")
        if accepted != expected: all_pass = False
    
    return all_pass

cases = [
    ("(a|b)*ab", [
        ("ab", True), ("aab", True), ("bab", True), ("abab", True),
        ("aba", False), ("abb", False), ("ba", False), ("a", False)
    ]),
    ("(a|b)*abb", [
        ("abb", True), ("aabb", True), ("babb", True),
        ("ab", False), ("abba", False)
    ]),
    ("a(b|c)*a", [
        ("aa", True), ("aba", True), ("aca", True), ("abbcca", True),
        ("a", False), ("ab", False), ("ac", False)
    ])
]

overall = True
for r, t in cases:
    if not test_audit(r, t):
        overall = False

if overall:
    print("\n[RESULT] AUDIT PASSED: All tricky cases handled correctly.")
else:
    print("\n[RESULT] AUDIT FAILED: Discrepancies found.")
