# Formal Computation Engine
### An Interactive Visual Execution Engine for Formal Computation Models

A web-based environment for constructing, visualizing, executing, and **comparing** formal computation models (NFA, DFA, PDA, Turing Machine) derived from the same language specification. The engine provides step-by-step execution traces, complexity metrics, and side-by-side comparison of computational processes — bridging the gap between theoretical formalism and observable machine behavior.

## Core Capabilities

- **Multi-Model Construction**: Regex → NFA (Thompson) → DFA (Subset Construction) → TM
- **CFG Processing**: Recursive descent parsing with parse tree visualization, CFG → PDA
- **Step-by-Step Execution**: Full execution history with state highlighting, transitions, tape/stack visualization
- **Comparison Mode**: Side-by-side execution of NFA vs DFA vs TM on the same input, with complexity metrics (states, transitions, execution steps)
- **Interactive Graph**: Draggable state nodes, curved edge routing, real-time layout updates

## Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)

## Installation

1. Open your terminal or command prompt.
2. Navigate to the project root directory.
3. Install the necessary Python libraries:

```bash
pip install fastapi uvicorn
```

## Running the Engine

### 1. Start the Backend API

```bash
python -m uvicorn api.main:app --reload
```

The server will start at `http://127.0.0.1:8000`.

### 2. Open the Interface

Navigate to `http://127.0.0.1:8000` in your browser, or open `ui/index.html` directly.

## Architecture

```
core/           → Base classes (State, Automaton)
automata/       → Machine definitions (NFA, DFA, PDA, TM) + subset construction
regex/          → Regex validation, parsing, infix→postfix, Thompson's construction
cfg/            → Grammar definition, recursive descent parser, parse trees
conversions/    → Cross-model transformations (NFA→DFA, DFA→TM, NFA→PDA, CFG→PDA)
simulation/     → Step-by-step simulators for each machine type
api/            → FastAPI backend with all endpoints
ui/             → Web frontend (HTML + CSS + JS with SVG visualization)
```
