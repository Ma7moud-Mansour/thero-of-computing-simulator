# Theory of Computing Simulator

This project creates a visual simulator for Automata Theory concepts, including NFA construction and simulation.

## Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)

## Installation

1. Open your terminal or command prompt.
2. Navigate to the project root directory.
3. Install the necessary Python libraries:

```bash
pip install fastapi uvicorn
```

*(Note: If you plan to run the legacy desktop app, you might also need `PySide6`, but for the Web Simulator, only the above are required.)*

## Running the Web Simulator

### 1. Start the Backend API
The simulator uses a Python FastAPI backend to handle logic.

Run the following command in the project directory:

```bash
python -m uvicorn api.main:app --reload
```

You should see output indicating the server is running at `http://127.0.0.1:8000`.

### 2. Run the User Interface
Open the `ui/index.html` file in your modern web browser (Chrome, Edge, Firefox).

- **Option A**: Double-click `ui/index.html` in your file explorer.
- **Option B**: Right-click -> Open With -> Google Chrome.

## Features

- **Regex to NFA**: Convert regular expressions like `(a|b)*ab` into NFA graphs.
- **Visualization**: Clear, rank-based visualization of states and transitions.
- **Simulation**: Step-by-step visual simulation of input strings, highlighting active states and transitions along the path.
