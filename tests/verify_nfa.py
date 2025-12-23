import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from regex.regex_parser import insert_concatenation
from regex.postfix import to_postfix
from regex.thompson import regex_to_nfa
from simulation.nfa_simulator import simulate_nfa
from api.main import normalize_nfa # Import normalization

def test_regex(regex, test_cases):
    print(f"Testing regex: {regex}")
    try:
        concat = insert_concatenation(regex)
        postfix = to_postfix(concat)
        nfa = regex_to_nfa(postfix)
        normalize_nfa(nfa) # Apply normalization
        
        print(f"  Concatenation: {concat}")
        print(f"  Postfix: {postfix}")
        print(f"  NFA: {len(nfa.states)} states")
        print(f"  Start State: {nfa.start_state.name} (Expected: q0)")
        
        if nfa.start_state.name != "q0":
             print(f"  FAILED: Start state is {nfa.start_state.name}")
             return False

        all_passed = True
        for string, expected in test_cases:
            accepted, history = simulate_nfa(nfa, string)
            
            if accepted != expected:
                print(f"  FAILED: '{string}' -> Got {accepted}, Expected {expected}")
                all_passed = False
            else:
                print(f"  PASSED: '{string}' -> {accepted}")
        
        if all_passed:
            print(f"  => Regex '{regex}' VERIFIED")
        else:
            print(f"  => Regex '{regex}' FAILED")
            
        return all_passed
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

tests = [
    ("(a|b)*abb", [
        ("abb", True),
        ("aabb", True),
        ("babb", True),
        ("ababb", True),
        ("ab", False),
        ("a", False),
        ("b", False),
        ("", False)
    ]),
    ("a.b", [ 
        ("ab", True),
        ("a", False),
        ("b", False)
    ]),
    ("ab", [ 
        ("ab", True),
        ("a", False),
        ("b", False)
    ]),
    ("a|b", [
        ("a", True),
        ("b", True),
        ("ab", False),
        ("", False)
    ]),
     ("a*", [
        ("", True),
        ("a", True),
        ("aa", True),
        ("b", False)
    ])
]

passed_count = 0
for regex, cases in tests:
    if test_regex(regex, cases):
        passed_count += 1

print(f"\nTotal Passed: {passed_count}/{len(tests)}")
