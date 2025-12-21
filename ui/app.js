/**
 * NFA Studio - Professional Visualization Engine
 * Architecture:
 * 1. LayoutEngine: Computes coordinates using Layered Graph approach.
 * 2. Renderer: Draws the graph using SVG with smart edge routing.
 * 3. Simulator: Manages playback state and highlighting.
 */

// Global State
let simulator;
const API_BASE = "http://127.0.0.1:8000";

// ==========================================
// 1. Layout Engine
// ==========================================
class LayoutEngine {
  constructor() {
    this.config = {
      xSpacing: 250,
      ySpacing: 180,
      startX: 150,
      centerY: 400
    };
  }

  compute(nfa, options = {}) {
    const config = { ...this.config, ...options };

    // Step 1: Layer Assignment (BFS)
    const layers = {};
    const ranks = {};
    const visited = new Set();
    const queue = [{ state: nfa.start, rank: 0 }];

    // Initialize
    nfa.states.sort().forEach(s => ranks[s] = 0);
    visited.add(nfa.start);

    let maxRank = 0;

    while (queue.length > 0) {
      const current = queue.shift();
      ranks[current.state] = current.rank;

      if (!layers[current.rank]) layers[current.rank] = [];
      layers[current.rank].push(current.state);

      maxRank = Math.max(maxRank, current.rank);

      // Get Neighbors
      const neighbors = nfa.transitions
        .filter(t => t.from === current.state)
        .map(t => t.to);

      // Sort neighbors for deterministic layout
      neighbors.sort();

      neighbors.forEach(next => {
        if (!visited.has(next)) {
          visited.add(next);
          queue.push({ state: next, rank: current.rank + 1 });
        }
      });
    }

    // Handle states not reached by BFS (if any - though backend prunes them)
    // Just place them at rank 0 or maxRank

    // Step 2: Calculate Coordinates
    const positions = {};

    // Re-center layers vertically
    Object.keys(layers).forEach(rank => {
      const states = layers[rank];
      const height = (states.length - 1) * config.ySpacing;
      const startY = config.centerY - (height / 2);

      states.forEach((s, i) => {
        positions[s] = {
          x: config.startX + (rank * config.xSpacing),
          y: startY + (i * config.ySpacing),
          rank: parseInt(rank),
          layerIndex: i
        };
      });
    });

    // Determine Canvas Size
    let maxX = 0, maxY = 0;
    Object.values(positions).forEach(p => {
      maxX = Math.max(maxX, p.x);
      maxY = Math.max(maxY, p.y);
    });

    return {
      positions,
      ranks,
      width: Math.max(1000, maxX + 200),
      height: Math.max(800, maxY + 200)
    };
  }
}

// ==========================================
// 2. Renderer
// ==========================================
class Renderer {
  constructor(svgId) {
    this.svg = document.getElementById(svgId);
    this.defsInjected = false;
    this.stateMap = {}; // DOM Element Map
    this.edgeMap = [];  // Array of {dom, transition}
  }

  initDefs() {
    if (this.defsInjected) return;
    const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
    defs.innerHTML = `
            <marker id="arrow" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="6" markerHeight="6" orient="auto">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#777" />
            </marker>
            <marker id="arrow-active" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="6" markerHeight="6" orient="auto">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#4ec9b0" />
            </marker>
        `;
    this.svg.appendChild(defs);
    this.defsInjected = true;
  }

  clear() {
    this.svg.innerHTML = "";
    this.defsInjected = false;
    this.stateMap = {};
    this.edgeMap = [];
    this.initDefs();
  }

  draw(nfa, layout) {
    this.clear();
    this.svg.setAttribute("width", layout.width);
    this.svg.setAttribute("height", layout.height);

    const { positions, ranks } = layout;

    // --- DRAW EDGES ---
    this.drawEdges(nfa, positions, ranks);

    // --- DRAW STATES ---
    Object.keys(positions).forEach(s => {
      this.drawState(s, positions[s], nfa.start === s, nfa.accept.includes(s));
    });
  }

  drawState(name, pos, isStart, isAccept) {
    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
    g.setAttribute("id", `state-${name}`);
    g.setAttribute("class", "state-group");
    g.style.cursor = "pointer";

    // Start Indicator
    if (isStart) {
      const arrow = document.createElementNS("http://www.w3.org/2000/svg", "path");
      arrow.setAttribute("d", `M ${pos.x - 50} ${pos.y} L ${pos.x - 25} ${pos.y}`);
      arrow.setAttribute("stroke", "#4ec9b0");
      arrow.setAttribute("stroke-width", "3");
      arrow.setAttribute("marker-end", "url(#arrow-active)");
      this.svg.appendChild(arrow);
    }

    // Outer Circle
    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", pos.x);
    circle.setAttribute("cy", pos.y);
    circle.setAttribute("r", 20);
    circle.setAttribute("fill", "#252526");
    circle.setAttribute("stroke", isAccept ? "#4ec9b0" : "#9cdcfe");
    circle.setAttribute("stroke-width", "3");
    g.appendChild(circle);

    // Inner Circle (Accept)
    if (isAccept) {
      const inner = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      inner.setAttribute("cx", pos.x);
      inner.setAttribute("cy", pos.y);
      inner.setAttribute("r", 15);
      inner.setAttribute("fill", "none");
      inner.setAttribute("stroke", "#4ec9b0");
      inner.setAttribute("stroke-width", "2");
      g.appendChild(inner);
    }

    // Label
    const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
    text.setAttribute("x", pos.x);
    text.setAttribute("y", pos.y + 5);
    text.setAttribute("text-anchor", "middle");
    text.setAttribute("font-size", "12");
    text.setAttribute("fill", "white");
    text.textContent = name;
    g.appendChild(text);

    this.svg.appendChild(g);
    this.stateMap[name] = g;
  }

  drawEdges(nfa, positions, ranks) {
    // Group edges
    const groups = {};
    nfa.transitions.forEach(t => {
      const key = `${t.from}|${t.to}`;
      if (!groups[key]) groups[key] = [];
      groups[key].push(t);
    });

    Object.values(groups).forEach(group => {
      const { from, to } = group[0];
      const a = positions[from];
      const b = positions[to];
      const rankA = a.rank;
      const rankB = b.rank;

      group.forEach((t, index) => {
        const isEpsilon = t.symbol === "ε";
        // Offset calculation (Jitter)
        // Use state ID to generate unique noise
        const seed = (parseInt(from.replace(/\D/g, '') || 0) * 13 + parseInt(to.replace(/\D/g, '') || 0) * 7);
        const jitter = (seed % 30) - 15;

        // Group Fan-out
        const fanOut = (index - (group.length - 1) / 2) * 25;

        let pathD = "";
        let cpX, cpY, labelX, labelY;

        const midX = (a.x + b.x) / 2;
        const midY = (a.y + b.y) / 2;

        if (from === to) {
          // Loop
          const h = 50 + Math.abs(fanOut);
          pathD = `M ${a.x} ${a.y - 25} C ${a.x - 30} ${a.y - 25 - h}, ${a.x + 30} ${a.y - 25 - h}, ${a.x} ${a.y - 25}`;
          cpX = a.x; cpY = a.y - 25 - h;
        } else if (Math.abs(rankA - rankB) === 1) {
          // Neighbor
          // Slight curve for style
          const curve = fanOut + jitter;
          // Calc normal
          const dx = b.x - a.x;
          const dy = b.y - a.y;
          const len = Math.sqrt(dx * dx + dy * dy);
          const nx = -dy / len;
          const ny = dx / len;

          cpX = midX + nx * curve * 3;
          cpY = midY + ny * curve * 3;

          pathD = `M ${a.x} ${a.y} Q ${cpX} ${cpY} ${b.x} ${b.y}`;
        } else if (rankB > rankA) {
          // Forward Skip (Go OVER)
          const arch = -80 - ((rankB - rankA) * 30) + fanOut + jitter;
          cpX = midX + jitter;
          cpY = midY + arch;
          pathD = `M ${a.x} ${a.y} Q ${cpX} ${cpY} ${b.x} ${b.y}`;
        } else {
          // Backward Edge (Go UNDER)
          const arch = 100 + ((rankA - rankB) * 30) + fanOut + jitter;
          cpX = midX + jitter;
          cpY = midY + arch;
          pathD = `M ${a.x} ${a.y} Q ${cpX} ${cpY} ${b.x} ${b.y}`;
        }

        // Label config
        // Bezier at t=0.5
        labelX = 0.25 * a.x + 0.5 * cpX + 0.25 * b.x;
        labelY = 0.25 * a.y + 0.5 * cpY + 0.25 * b.y;

        // Draw Path
        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        path.setAttribute("d", pathD);
        path.setAttribute("fill", "none");
        path.setAttribute("stroke", isEpsilon ? "#777" : "#aaa");
        path.setAttribute("stroke-width", "2");
        path.setAttribute("stroke-dasharray", isEpsilon ? "5,5" : "0");
        path.setAttribute("marker-end", "url(#arrow)");
        this.svg.appendChild(path);

        // Label Box
        const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        rect.setAttribute("x", labelX - 10);
        rect.setAttribute("y", labelY - 10);
        rect.setAttribute("width", 20);
        rect.setAttribute("height", 20);
        rect.setAttribute("fill", "#1e1e1e");
        this.svg.appendChild(rect);

        const txt = document.createElementNS("http://www.w3.org/2000/svg", "text");
        txt.setAttribute("x", labelX);
        txt.setAttribute("y", labelY + 4);
        txt.setAttribute("text-anchor", "middle");
        txt.setAttribute("fill", "#ddd");
        txt.setAttribute("font-size", "12");
        txt.textContent = t.symbol;
        this.svg.appendChild(txt);

        this.edgeMap.push({
          dom: path,
          data: t,
          from: from,
          to: to
        });
      });
    });
  }

  highlight(activeStates, transitions) {
    // Reset
    this.svg.querySelectorAll("circle").forEach(c => c.setAttribute("fill", "#252526")); // Reset to BG
    this.svg.querySelectorAll("path").forEach(p => {
      if (p.getAttribute("marker-end") === "url(#arrow)") {
        p.setAttribute("stroke", p.getAttribute("stroke-dasharray") !== "0" ? "#777" : "#aaa");
        p.setAttribute("stroke-width", "2");
      }
    });

    // 1. Highlight States
    activeStates.forEach(name => {
      const g = this.stateMap[name];
      if (g) {
        // Outer circle
        g.children[0].setAttribute("fill", "#264f78");
      }
    });

    // 2. Highlight Edges
    if (transitions) {
      transitions.forEach(t => {
        // Find matching edge dom
        const match = this.edgeMap.find(e =>
          e.from === t.from &&
          e.to === t.to &&
          e.data.symbol === t.symbol
        );

        if (match) {
          match.dom.setAttribute("stroke", "#4ec9b0");
          match.dom.setAttribute("stroke-width", "4");
        }
      });
    }
  }
}

// ==========================================
// 3. Simulator Controller
// ==========================================
class Simulator {
  constructor() {
    this.history = [];
    this.currentStep = 0;
    this.nfaData = null;
    this.mode = 'NFA'; // 'NFA' or 'DFA'

    this.layoutEngine = new LayoutEngine();
    this.renderer = new Renderer("canvas");
  }

  async loadNFA(regex) {
    try {
      this.mode = 'NFA';
      const res = await fetch(`${API_BASE}/nfa`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ regex })
      });
      const nfa = await res.json();
      this.nfaData = this.normalize(nfa);

      const layout = this.layoutEngine.compute(this.nfaData);
      this.renderer.draw(this.nfaData, layout);

      this.resetSimulation();
    } catch (e) {
      console.error(e);
      alert("Error building NFA");
    }
  }

  async runSimulation(regex, string) {
    try {
      let endpoint = '/simulate/nfa';
      if (this.mode === 'DFA') endpoint = '/simulate/dfa';
      if (this.mode === 'TM') endpoint = '/simulate/tm';

      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ regex, string })
      });
      const data = await res.json();

      this.history = data.steps;
      if (this.mode === 'TM') {
        this.nfaData = data.tm;
      } else {
        this.nfaData = this.normalize(data.nfa); // Sync structure
      }

      // Redraw to ensure consistency
      const spacing = (this.mode === 'DFA' || this.mode === 'TM') ? { xSpacing: 350, ySpacing: 250 } : {};
      const layout = this.layoutEngine.compute(this.nfaData, spacing);
      this.renderer.draw(this.nfaData, layout);

      this.currentStep = 0;
      this.updateView();
    } catch (e) {
      console.error(e);
      alert("Simulation Error");
    }
  }

  normalize(nfa) {
    // Ensure format
    return nfa;
  }

  next() {
    if (this.currentStep < this.history.length - 1) {
      this.currentStep++;
      this.updateView();
    }
  }

  prev() {
    if (this.currentStep > 0) {
      this.currentStep--;
      this.updateView();
    }
  }

  updateView() {
    const step = this.history[this.currentStep];
    if (!step) return;

    document.getElementById("stepCounter").innerText = `Step ${this.currentStep + 1} / ${this.history.length}`;
    document.getElementById("statusText").innerText = step.description || step.step;

    this.renderer.highlight(step.active || [step.state], step.transitions);

    if (this.mode === 'TM') {
      document.getElementById("tape-container").style.display = "block";
      const tapeArr = step.tape ? step.tape.split('') : ["_"];
      this.renderTape(tapeArr, step.head);
    } else {
      document.getElementById("tape-container").style.display = "none";
    }

    if (this.currentStep === this.history.length - 1) {
      const accepted = (this.mode === 'TM') ? (step.state && this.nfaData.accept.includes(step.state)) :
        step.active.some(s => this.nfaData.accept.includes(s));

      const statusEl = document.getElementById("statusText");
      if (accepted) {
        statusEl.innerText = "Accepted ✅";
        statusEl.style.color = "#4ec9b0";
      } else {
        statusEl.innerText = "Rejected ❌";
        statusEl.style.color = "#f44747";
      }
    } else {
      document.getElementById("statusText").style.color = "#d4d4d4";
    }
  }

  async loadDFA(regex) {
    try {
      this.mode = 'DFA';
      document.getElementById("statusText").innerText = "Building DFA...";
      const res = await fetch(`${API_BASE}/dfa`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ regex })
      });
      const dfa = await res.json();

      // Normalize DFA structure if needed, but we aligned backend to match NFA keys
      this.nfaData = dfa;

      // Recompute layout for DFA WITH EXTRA SPACING
      const layout = this.layoutEngine.compute(this.nfaData, { xSpacing: 350, ySpacing: 250 });
      this.renderer.draw(this.nfaData, layout);

      this.resetSimulation();
      document.getElementById("statusText").innerText = "DFA Ready";
      document.getElementById("stepCounter").innerText = "Deterministic Finite Automaton";

    } catch (e) {
      console.error(e);
      alert("Error building DFA");
    }
  }

  async loadTM(regex) {
    try {
      this.mode = 'TM';
      document.getElementById("statusText").innerText = "Building Turing Machine...";
      const res = await fetch(`${API_BASE}/tm`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ regex })
      });
      const tm = await res.json();

      this.nfaData = tm;

      const layout = this.layoutEngine.compute(this.nfaData, { xSpacing: 350, ySpacing: 250 });
      this.renderer.draw(this.nfaData, layout);

      this.resetSimulation();
      document.getElementById("statusText").innerText = "TM Ready";
      document.getElementById("stepCounter").innerText = "Standard Single-Tape TM";

      document.getElementById("tape-container").style.display = "block";
      this.renderTape(["_"], 0);

    } catch (e) {
      console.error(e);
      alert("Error building TM");
    }
  }

  renderTape(tapeChars, headPos) {
    const container = document.getElementById("tape-content");
    container.innerHTML = "";

    tapeChars.forEach((char, i) => {
      const cell = document.createElement("div");
      cell.style.width = "30px";
      cell.style.height = "30px";
      cell.style.border = "1px solid #555";
      cell.style.display = "flex";
      cell.style.alignItems = "center";
      cell.style.justifyContent = "center";
      cell.style.fontSize = "1.1rem";
      cell.style.fontFamily = "monospace";
      cell.style.background = i === headPos ? "#264f78" : "#1e1e1e";
      cell.innerText = char === "_" ? "␣" : char;

      if (i === headPos) {
        cell.style.border = "2px solid #007acc";
        cell.style.boxShadow = "0 0 5px #007acc";
      }

      container.appendChild(cell);
    });
  }

  resetSimulation() {
    this.history = [];
    this.currentStep = 0;
    document.getElementById("stepCounter").innerText = "Ready";
    document.getElementById("statusText").innerText = "";
    this.renderer.highlight([], []);
  }
}

// ==========================================
// Initialization
// ==========================================
simulator = new Simulator();

window.buildNFA = () => {
  const regex = document.getElementById("regex").value;
  simulator.loadNFA(regex);
};

window.buildDFA = () => {
  const regex = document.getElementById("regex").value;
  simulator.loadDFA(regex);
};

window.buildTM = () => {
  const regex = document.getElementById("regex").value;
  simulator.loadTM(regex);
};

window.simulate = () => {
  const regex = document.getElementById("regex").value;
  const str = document.getElementById("inputString").value;
  simulator.runSimulation(regex, str);
};

window.nextStep = () => simulator.next();
window.prevStep = () => simulator.prev();

// Build initial
window.onload = () => window.buildNFA();
