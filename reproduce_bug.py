import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from regex.regex_parser import insert_concatenation
from regex.postfix import to_postfix
from regex.thompson import regex_to_nfa
from simulation.nfa_simulator import simulate_nfa
from api.main import normalize_nfa

regex = "(a|b)*ab"
concat = insert_concatenation(regex)
postfix = to_postfix(concat)
nfa = regex_to_nfa(postfix)
normalize_nfa(nfa)

print(f"Regex: {regex}")
print(f"Concat: {concat}")
print(f"Postfix: {postfix}")

test_strings = ["abb", "aba", "ab", "abab", "a", "b"]

for s in test_strings:
    accepted, history = simulate_nfa(nfa, s)
    print(f"Input '{s}': {accepted}")
    if s == "abb" and accepted:
        print("!! BUG CONFIRMED: 'abb' should be REJECTED !!")
    if s == "aba" and accepted:
        print("!! BUG CONFIRMED: 'aba' should be REJECTED !!")
