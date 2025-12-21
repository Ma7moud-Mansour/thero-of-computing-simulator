import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from regex.regex_parser import insert_concatenation
from regex.postfix import to_postfix
from regex.thompson import regex_to_nfa
from simulation.nfa_simulator import simulate_nfa

def test_regex(pattern, positive_cases, negative_cases):
    print(f"\n--- Testing Regex: {pattern} ---")
    try:
        concat = insert_concatenation(pattern)
        postfix = to_postfix(concat)
        nfa = regex_to_nfa(postfix)
        
        # 1. Structural Checks
        print(f"Stats: {len(nfa.states)} states, {len(nfa.transitions)} transitions")
        print(f"Start State: {nfa.start_state.name}")
        print(f"Accept States: {[s.name for s in nfa.accept_states]}")
        
        if len(nfa.accept_states) != 1:
            print("WARNING: NFA has multiple or zero accept states (Textbook Thompson usually has 1).")
        
        # Check for single component (BFS)
        # (Skip for brevity, simulation covers reachability)

        # 2. Logic Checks
        all_passed = True
        for s in positive_cases:
            res, _ = simulate_nfa(nfa, s)
            if not res:
                print(f"FAILED: Expected accept for '{s}'")
                all_passed = False
            else:
                print(f"PASS: Accepted '{s}'")

        for s in negative_cases:
            res, _ = simulate_nfa(nfa, s)
            if res:
                print(f"FAILED: Expected reject for '{s}'")
                all_passed = False
            else:
                print(f"PASS: Rejected '{s}'")
                
        return all_passed
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

tests = [
    ("(a|b)*ab", ["ab", "aab", "bab", "aaab", "abbab"], ["a", "b", "aba", "ba", ""]),
    ("(a|b)*abb", ["abb", "aabb", "babb"], ["ab", "abba", "baba"]),
    ("a(b|c)*a", ["aa", "aba", "aca", "abba", "acca", "abca"], ["a", "ab", "ac", "abc"]),
    ("", [""], ["a"]), # Empty regex vs empty string
]

success_count = 0
for pat, pos, neg in tests:
    if test_regex(pat, pos, neg):
        success_count += 1

print(f"\nSummary: {success_count}/{len(tests)} Regexes Passed Logic Verification")
