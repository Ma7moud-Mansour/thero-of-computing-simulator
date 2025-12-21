import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from fastapi import FastAPI
from pydantic import BaseModel

from regex.regex_parser import insert_concatenation
from regex.postfix import to_postfix
from regex.thompson import regex_to_nfa

from conversions.nfa_to_dfa import nfa_to_dfa
from conversions.dfa_to_tm import dfa_to_tm
from conversions.nfa_to_pda import nfa_to_pda
from conversions.cfg_to_pda import cfg_to_pda

from simulation.nfa_simulator import simulate_nfa
from simulation.tm_simulator import simulate_tm
from cfg.parser import parse_with_tree
from cfg.grammar import Grammar

#------------------------------------------
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


#------------------------------------------
class regexInput(BaseModel):
    regex: str

class SimulateInput(BaseModel):
    regex: str
    string: str

class CFGInput(BaseModel):
    grammar: dict
    start: str
    string: str

#------------------------------------------

def serialize_nfa(nfa):
    return {
        "states": [s.name for s in nfa.states],
        "start": nfa.start_state.name,
        "accept": [s.name for s in nfa.accept_states],
        "transitions": [
            {"from": s.name, "symbol": sym or "ε", "to": t.name}
            for (s, sym), targets in nfa.transitions.items()
            for t in targets
        ]
    }

#------------------------------------------
def normalize_nfa(nfa):
    # BFS Traversal for logical naming
    queue = [nfa.start_state]
    mapping = {nfa.start_state: "q0"}
    nfa.start_state.name = "q0"
    visited = {nfa.start_state}
    count = 1

    while queue:
        current = queue.pop(0)
        
        # Sort transitions by symbol to make traversal deterministic
        # (state, symbol) -> connections
        # We need to look at transitions FROM current
        outgoing = []
        for key, targets in nfa.transitions.items():
            if key[0] == current:
                 symbol = key[1] if key[1] else "ε" # Treat None as epsilon for sorting
                 # Sort targets by some property if possible, or just name
                 # Since targets are states we haven't named yet, we use their current name (creation ID)
                 # This ensures deterministic order based on creation sequence
                 sorted_targets = sorted(list(targets), key=lambda x: int(x.name[1:]) if x.name.startswith("q") and x.name[1:].isdigit() else x.name) 
                 outgoing.append((symbol, sorted_targets))
        
        # Sort by symbol (a, b, then epsilon)
        # We want 'a' (char) to be named before 'epsilon' usually? 
        # Actually standard is usually follow epsilon first. Let's do string sort. 'a' < 'ε' (unicode)? 
        # 'ε' is usually larger. So 'a' gets q1, epsilon gets q2.
        outgoing.sort(key=lambda x: x[0])

        for _, targets in outgoing:
            for next_state in targets:
                if next_state not in visited:
                    visited.add(next_state)
                    name = f"q{count}"
                    count += 1
                    mapping[next_state] = name
                    next_state.name = name
                    queue.append(next_state)
    
    
    # Prune unreachable states to ensure strict consistency between Simulation and UI.
    # If a state is not reachable from start (BFS), it shouldn't exist in the NFA for our purposes.
    nfa.states = visited
    
    return nfa

#------------------------------------------
@app.post("/nfa")
def build_nfa(data: regexInput):
    regex = insert_concatenation(data.regex.strip())
    postfix = to_postfix(regex)
    
    from core.state import State
    State._id = 0
    
    nfa = regex_to_nfa(postfix)
    normalize_nfa(nfa)
    return serialize_nfa(nfa)

@app.post("/simulate/nfa")
def simulate_nfa_api(data: SimulateInput):
    regex = insert_concatenation(data.regex.strip())
    postfix = to_postfix(regex)
    
    from core.state import State
    State._id = 0
    
    nfa = regex_to_nfa(postfix)
    normalize_nfa(nfa)

    accepted, history = simulate_nfa(nfa, data.string)

    return {
        "accepted": accepted,
        "steps": history,
        "nfa": serialize_nfa(nfa)
    }

@app.post("/dfa")
def build_dfa(data: regexInput):
    regex = insert_concatenation(data.regex.strip())
    postfix = to_postfix(regex)
    
    from core.state import State
    State._id = 0
    
    nfa = regex_to_nfa(postfix)
    # Note: We might want to normalize NFA before converting? 
    # Usually doesn't matter for DFA structure, but for consistency let's do it.
    normalize_nfa(nfa) 
    dfa = nfa_to_dfa(nfa)

    return {
        "states": list(dfa.states),
        "start": dfa.start_state,
        "accept": list(dfa.accept_states),
        "transitions": [
            {"from": s, "symbol": a, "to": t}
            for (s, a), t in dfa.transitions.items()
        ]
    }

@app.post("/simulate/tm")
def simulate_tm_api(data: SimulateInput):
    regex = insert_concatenation(data.regex.strip())
    postfix = to_postfix(regex)
    nfa = regex_to_nfa(postfix)
    dfa = nfa_to_dfa(nfa)
    tm = dfa_to_tm(dfa)

    accepted, history = simulate_tm(tm, data.string)

    return {
        "accepted": accepted,
        "steps": history
    }
@app.post("/cfg/parse")
def parse_cfg(data: CFGInput):
    g = Grammar(data.start)
    for lhs, rhss in data.grammar.items():
        for rhs in rhss:
            g.add_production(lhs, rhs)

    accepted, tree = parse_with_tree(g, data.string)
    return {"accepted": accepted}
