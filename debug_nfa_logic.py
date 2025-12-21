import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from regex.regex_parser import insert_concatenation
from regex.postfix import to_postfix
from regex.thompson import regex_to_nfa
from simulation.nfa_simulator import simulate_nfa
from api.main import normalize_nfa, serialize_nfa

regex = "(a|b)*ab"
input_str = "aab"

concat = insert_concatenation(regex)
postfix = to_postfix(concat)
nfa = regex_to_nfa(postfix)

# PRE-NORMALIZATION
print(f"Original States: {len(nfa.states)}")
print(f"Original Accept: {[s.name for s in nfa.accept_states]}")

normalize_nfa(nfa)

# POST-NORMALIZATION
serialized = serialize_nfa(nfa)
print(f"\nNormalized States ({len(serialized['states'])}): {serialized['states']}")
print(f"Normalized Accept: {serialized['accept']}")
print("Transitions:")
for t in serialized['transitions']:
    sym = t['symbol'] if t['symbol'] != "ε" else "EPS"
    print(f"  {t['from']} --{sym}--> {t['to']}")

accepted, history = simulate_nfa(nfa, input_str)
print(f"\nSimulation Result: {accepted}")
print("Last Step Active States:")
last_step = history[-1]
print(f"  {last_step['active']}")

# Check if any active state is in accept
active_names = last_step['active']
accept_names = serialized['accept']
matches = [s for s in active_names if s in accept_names]
print(f"Intersection (Active & Accept): {matches}")
