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
@app.post("/nfa")
def build_nfa(data: regexInput):
    regex = insert_concatenation(data.regex.strip())
    postfix = to_postfix(regex)
    nfa = regex_to_nfa(postfix)
    return serialize_nfa(nfa)

@app.post("/simulate/nfa")
def simulate_nfa_api(data: SimulateInput):
    regex = insert_concatenation(data.regex.strip())
    postfix = to_postfix(regex)
    nfa = regex_to_nfa(postfix)

    accepted, history = simulate_nfa(nfa, data.string)

    return {
        "accepted": accepted,
        "steps": [[s.name for s in step] for step in history],
        "nfa": serialize_nfa(nfa)
    }

@app.post("/dfa")
def build_dfa(data: regexInput):
    regex = insert_concatenation(data.regex.strip())
    postfix = to_postfix(regex)
    nfa = regex_to_nfa(postfix)
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
