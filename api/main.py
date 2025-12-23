import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from regex.regex_parser import insert_concatenation
from regex.postfix import to_postfix
from regex.thompson import regex_to_nfa
from core.state import State
from conversions.nfa_to_dfa import nfa_to_dfa

from conversions.nfa_to_dfa import nfa_to_dfa
from conversions.dfa_to_tm import dfa_to_tm
from conversions.nfa_to_pda import nfa_to_pda
from conversions.cfg_to_pda import cfg_to_pda

from simulation.nfa_simulator import simulate_nfa
from simulation.tm_simulator import simulate_tm
from cfg.parser import parse_with_tree
from cfg.grammar import Grammar
from regex.validation import validate_regex

#------------------------------------------
app = FastAPI()

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

class SimulateTMInput(BaseModel):
    tm: dict
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

app.mount("/static", StaticFiles(directory="ui"), name="static")

@app.get("/")
def home():
    return FileResponse("ui/index.html")

@app.post("/nfa")
def build_nfa(data: regexInput):
    try:
        validate_regex(data.regex.strip())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    regex = insert_concatenation(data.regex.strip())
    postfix = to_postfix(regex)
    
    State._id = 0
    
    nfa = regex_to_nfa(postfix)
    normalize_nfa(nfa)
    return serialize_nfa(nfa)

@app.post("/simulate/nfa")
def simulate_nfa_api(data: SimulateInput):
    try:
        validate_regex(data.regex.strip())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    regex = insert_concatenation(data.regex.strip())
    postfix = to_postfix(regex)
    
    State._id = 0
    
    nfa = regex_to_nfa(postfix)
    normalize_nfa(nfa)

    accepted, history = simulate_nfa(nfa, data.string)

    return {
        "accepted": accepted,
        "steps": history
    }

@app.post("/dfa")
def build_dfa(data: regexInput):
    try:
        validate_regex(data.regex.strip())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    regex = insert_concatenation(data.regex.strip())
    postfix = to_postfix(regex)
    
    State._id = 0
    
    nfa = regex_to_nfa(postfix)
    # Note: We might want to normalize NFA before converting? 
    # Usually doesn't matter for DFA structure, but for consistency let's do it.
    normalize_nfa(nfa) 
    
    from automata.subset_construction import nfa_to_dfa
    dfa = nfa_to_dfa(nfa)

    return dfa

@app.post("/simulate/dfa")
def simulate_dfa_api(data: SimulateInput):
    try:
        validate_regex(data.regex.strip())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    regex = insert_concatenation(data.regex.strip())
    postfix = to_postfix(regex)
    
    State._id = 0
    
    nfa = regex_to_nfa(postfix)
    normalize_nfa(nfa)
    
    from automata.subset_construction import nfa_to_dfa
    dfa = nfa_to_dfa(nfa)
    
    from simulation.dfa_simulator import simulate_dfa
    accepted, history = simulate_dfa(dfa, data.string)
    
    return {
        "accepted": accepted,
        "steps": history
    }


@app.post("/build_tm")
def build_tm(data: regexInput):
    try:
        validate_regex(data.regex.strip())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    regex = insert_concatenation(data.regex.strip())
    postfix = to_postfix(regex)
    
    State._id = 0
    
    nfa = regex_to_nfa(postfix)
    normalize_nfa(nfa)
    
    from automata.subset_construction import nfa_to_dfa
    dfa = nfa_to_dfa(nfa)
    
    from automata.dfa_to_tm import dfa_to_tm
    tm = dfa_to_tm(dfa)
    
    return tm

@app.post("/simulate/tm")
def simulate_tm_api(data: SimulateTMInput):
    # TM is supplied directly; no regex processing needed.
    accepted, history = simulate_tm(data.tm, data.string)
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
    
    derivations = get_leftmost_derivation(tree) if tree else []

    return {
        "accepted": accepted,
        "tree": serialize_tree(tree) if tree else None,
        "derivations": derivations
    }

def get_leftmost_derivation(root):
    if not root:
        return []
    
    # Store the current sentential form as a list of Nodes
    # Initially just the root
    current_form = [root]
    history = [ [root.symbol] ] # Store strings
    
    # We need to iteratively expand the leftmost non-terminal
    while True:
        # Find leftmost non-terminal that has children (and hasn't been expanded in our 'form' view logic)
        # Actually, extracting derivation from a static tree is slightly distinct from generating it.
        # In the tree, the structure is already fixed. 
        # We need to simulate the expansion process.
        
        # Easier approach:
        # Recursive? No, linear steps needed.
        # We have the tree.
        # Step 0: S
        # Step 1: Replace S with its children -> e.g. A B
        # Step 2: Replace A (leftmost) with its children -> a B
        # ...
        
        # Let's use a list of LogicNodes where LogicNode points to the Tree Node
        # Loop:
        #   Find first node in 'current_form' that is a variable AND has children.
        #   Replace it with its children.
        #   Record new form.
        #   If no variables left, stop.
        
        change_made = False
        new_form = []
        
        # Find the leftmost expandable node index
        expand_index = -1
        for i, node in enumerate(current_form):
            # Check if it has children (implies it was a variable that got expanded)
            # Terminals in the tree have no children.
            if node.children:
                expand_index = i
                break
        
        if expand_index == -1:
            break # All terminals
            
        # Construct next step
        # Prefix: 0 to expand_index
        new_form.extend(current_form[:expand_index])
        # Expansion: children of the node
        new_form.extend(current_form[expand_index].children)
        # Suffix: expand_index+1 to end
        new_form.extend(current_form[expand_index+1:])
        
        current_form = new_form
        
        # Record string representation
        # Filter out epsilons for display, unless it's the ONLY thing (meaning empty string)
        step_str = [n.symbol for n in current_form if n.symbol != "ε"]
        if not step_str: 
            step_str = ["ε"] # Represents empty string
            
        history.append(step_str)
        
    return [" ".join(h) for h in history]

def serialize_tree(node):
    if not node:
        return None
    return {
        "symbol": node.symbol,
        "children": [serialize_tree(child) for child in node.children]
    }

@app.post("/cfg/pda")
def build_cfg_pda(data: CFGInput):
    # Reconstruct Grammar object ? Or just pass dict directly if cfg_to_pda accepts dict?
    # cfg_to_pda expects a Grammar entry.
    g = Grammar(data.start)
    for lhs, rhss in data.grammar.items():
        for rhs in rhss:
            g.add_production(lhs, rhs)
            
    pda = cfg_to_pda(g)
    # Serialize using general PDA serializer
    return serialize_pda(pda)

#------------------------------------------
def serialize_pda(pda):
    return {
        "states": [s.name for s in pda.states],
        "start": pda.start_state.name,
        "accept": [s.name for s in pda.accept_states],
        "transitions": [
            {
                "from": s.name,
                "symbol": sym or "ε",
                "pop": pop_sym,
                "to": t.name,
                "push": "".join(push) if isinstance(push, (list, tuple)) else str(push)
            }
            # pda.transitions key is (state, input, stack_top)
            for (s, sym, pop_sym), targets in pda.transitions.items()
            for (t, push) in targets
        ]
    }

@app.post("/pda")
def build_pda(data: regexInput):
    try:
        validate_regex(data.regex.strip())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    regex = insert_concatenation(data.regex.strip())
    postfix = to_postfix(regex)
    
    State._id = 0
    
    nfa = regex_to_nfa(postfix)
    normalize_nfa(nfa)
    
    pda = nfa_to_pda(nfa)
    return serialize_pda(pda)

@app.post("/simulate/pda")
def simulate_pda_api(data: SimulateInput):
    try:
        validate_regex(data.regex.strip())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    regex = insert_concatenation(data.regex.strip())
    postfix = to_postfix(regex)
    
    State._id = 0
    
    nfa = regex_to_nfa(postfix)
    normalize_nfa(nfa)
    
    pda = nfa_to_pda(nfa)
    
    from simulation.pda_simulator import simulate_pda, simulate_general_pda
    accepted, history = simulate_pda(pda, data.string)
    
    return {
        "accepted": accepted,
        "steps": history
    }


@app.post("/simulate/cfg/pda")
def simulate_cfg_pda(data: CFGInput):
    g = Grammar(data.start)
    for lhs, rhss in data.grammar.items():
        for rhs in rhss:
            g.add_production(lhs, rhs)
            
    pda = cfg_to_pda(g)
    
    from simulation.pda_simulator import simulate_general_pda
    accepted, history = simulate_general_pda(pda, data.string, accept_by_empty_stack=True)
    
    return {
        "accepted": accepted,
        "steps": history
    }
