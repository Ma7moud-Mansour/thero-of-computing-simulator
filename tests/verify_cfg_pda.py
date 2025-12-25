import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.getcwd()))

from cfg.grammar import Grammar
from conversions.cfg_to_pda import cfg_to_pda
from simulation.pda_simulator import simulate_general_pda

def test_cfg_pda():
    print("Testing CFG -> PDA Simulation...")
    
    # Grammar: S -> a S b | epsilon
    # Language: a^n b^n
    g = Grammar("S")
    g.add_production("S", ["a", "S", "b"])
    g.add_production("S", "") # epsilon
    
    print("1. Converting CFG to PDA...")
    pda = cfg_to_pda(g)
    print(f"   PDA States: {len(pda.states)}")
    print(f"   PDA Transitions: {len(pda.transitions)}")
    
    test_cases = [
        ("", True),
        ("ab", True),
        ("aabb", True),
        ("aaabbb", True),
        ("a", False),
        ("b", False),
        ("aabbb", False),
        ("ba", False)
    ]
    
    passed = 0
    for s, expected in test_cases:
        accepted, history = simulate_general_pda(pda, s, accept_by_empty_stack=True)
        res_str = "ACCEPTED" if accepted else "REJECTED"
        exp_str = "ACCEPTED" if expected else "REJECTED"
        
        if accepted == expected:
            print(f"   [PASS] '{s}': Got {res_str}")
            passed += 1
        else:
            print(f"   [FAIL] '{s}': Got {res_str}, Expected {exp_str}")
            # Debug traces
            pass
            
    if passed == len(test_cases):
        print("\nAll tests passed!")
    else:
        print(f"\nFailed {len(test_cases) - passed} tests.")

if __name__ == "__main__":
    test_cfg_pda()
