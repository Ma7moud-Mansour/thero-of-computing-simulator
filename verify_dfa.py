import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from regex.regex_parser import insert_concatenation
from regex.postfix import to_postfix
from regex.thompson import regex_to_nfa
from simulation.nfa_simulator import simulate_nfa
from automata.subset_construction import nfa_to_dfa
from simulation.dfa_simulator import simulate_dfa
from core.state import State

def test_equivalence(regex_str, test_strings):
    print(f"\n--- Regex: {regex_str} ---")
    
    State._id = 0
    concat = insert_concatenation(regex_str)
    postfix = to_postfix(concat)
    nfa = regex_to_nfa(postfix)
    
    dfa = nfa_to_dfa(nfa)
    print(f"DFA States: {len(dfa['states'])}, Accepts: {dfa['accept_states']}")
    
    all_pass = True
    for s in test_strings:
        nfa_res, _ = simulate_nfa(nfa, s)
        dfa_res, _ = simulate_dfa(dfa, s)
        
        status = "MATCH" if nfa_res == dfa_res else "MISMATCH"
        if status == "MISMATCH":
            all_pass = False
            print(f"FAIL: Input '{s}' -> NFA: {nfa_res}, DFA: {dfa_res}")
        else:
            # print(f"PASS: Input '{s}' -> Both {nfa_res}")
            pass
            
    if all_pass:
        print("[OK] Equivalence Verified")
    else:
        print("[FAIL] Equivalence Failed")

tests = [
    ("(a|b)*ab", ["ab", "aab", "bab", "aaab", "abbab", "a", "b", "aba"]),
    ("(a|b)*abb", ["abb", "aabb", "babb", "ab", "baba"]),
    ("a(b|c)*a", ["aa", "aba", "aca", "abc", "a"]),
    ("", ["", "a"])
]

for pat, strings in tests:
    test_equivalence(pat, strings)
