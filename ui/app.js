// ===== GLOBAL STATE FOR SIMULATION =====
let simulationHistory = [];
let currentStep = 0;
let nfaData = null;

async function buildNFA() {
  const regex = document.getElementById("regex").value.trim();
  if (!regex) return;

  const res = await fetch("http://127.0.0.1:8000/nfa", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ regex })
  });

  const nfa = await res.json();
  nfaData = processNFA(nfa);
  drawNFA(nfaData);

  // Clear simulation
  simulationHistory = [];
  currentStep = 0;
  updateSimulationControls();
}

async function simulate() {
  const regex = document.getElementById("regex").value.trim();
  const string = document.getElementById("inputString").value.trim();
  if (!regex) return;

  const res = await fetch("http://127.0.0.1:8000/simulate/nfa", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ regex, string })
  });

  const result = await res.json();
  simulationHistory = result.steps; // New structure
  nfaData = processNFA(result.nfa); // Ensure we have the same states if re-fetched

  // Reset and draw initial state
  currentStep = 0;
  drawNFA(nfaData);
  highlightStep(0);
  updateSimulationControls();
}


const stateMap = {}; // Maps BackendName -> FrontendName
// Note: Backend now guarantees normalized names (q0...qn).
// We primarily use stateMap to ensure mapping consistency if explicit lookup is needed later.

function processNFA(nfa) {
  // 1. Reset state map
  Object.keys(stateMap).forEach(k => delete stateMap[k]);

  // 2. Map directly: Backend Name IS the Frontend Name
  nfa.states.sort();
  nfa.states.forEach(s => stateMap[s] = s);

  const cleanup = (s) => stateMap[s];

  return {
    states: nfa.states.map(cleanup),
    start: cleanup(nfa.start),
    accept: nfa.accept.map(cleanup),
    transitions: nfa.transitions.map(t => ({
      from: cleanup(t.from),
      to: cleanup(t.to),
      symbol: t.symbol,
      originalFrom: t.from,
      originalTo: t.to
    }))
  };
}

function computeLayout(nfa) {
  // BFS to assign generic "Ranks" (X-coords)
  const ranks = {};
  const visited = new Set();
  const queue = [{ state: nfa.start, rank: 0 }];

  nfa.states.forEach(s => ranks[s] = 0);
  visited.add(nfa.start);

  // Track max rank to normalize width
  let maxRank = 0;

  while (queue.length > 0) {
    const { state, rank } = queue.shift();
    ranks[state] = rank;
    maxRank = Math.max(maxRank, rank);

    // Find neighbors
    const neighbors = nfa.transitions
      .filter(t => t.from === state)
      .map(t => t.to);

    neighbors.forEach(next => {
      if (!visited.has(next)) {
        visited.add(next);
        queue.push({ state: next, rank: rank + 1 });
      }
    });
  }

  // Assign Y coords based on grouping by Rank
  const levels = {};
  for (const [state, rank] of Object.entries(ranks)) {
    if (!levels[rank]) levels[rank] = [];
    levels[rank].push(state);
  }

  const pos = {};
  const X_SPACING = 150;
  const Y_SPACING = 100;
  const START_X = 100;
  const CENTER_Y = 350;

  Object.keys(levels).forEach(rank => {
    const levelStates = levels[rank];
    const count = levelStates.length;
    const totalHeight = (count - 1) * Y_SPACING;
    const startY = CENTER_Y - totalHeight / 2;

    levelStates.forEach((s, i) => {
      pos[s] = {
        x: START_X + rank * X_SPACING,
        y: startY + i * Y_SPACING
      };
    });
  });

  return pos;
}


function drawNFA(nfa) {
  const svg = document.getElementById("canvas");
  svg.innerHTML = "";

  // Definitions for markers
  const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
  defs.innerHTML = `
    <marker id="arrow" viewBox="0 0 10 10" refX="28" refY="5"
      markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#aaa" />
    </marker>
    <marker id="arrow-active" viewBox="0 0 10 10" refX="28" refY="5"
      markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#4ec9b0" />
    </marker>
  `;
  svg.appendChild(defs);

  const pos = computeLayout(nfa);

  // --- Transitions ---
  // Group by (from, to) to handle multiple edges
  const edgeGroups = {};
  nfa.transitions.forEach((t, i) => {
    const key = `${t.from}-${t.to}`;
    if (!edgeGroups[key]) edgeGroups[key] = [];
    edgeGroups[key].push({ ...t, id: i }); // Add ID for highlighting
  });

  Object.values(edgeGroups).forEach(group => {
    const { from, to } = group[0];
    const a = pos[from];
    const b = pos[to];
    const isLoop = from === to;

    // If multiple edges between same nodes, spread them out
    group.forEach((t, i) => {
      const offset = (i - (group.length - 1) / 2) * 20;

      let pathD = "";
      let labelX = 0, labelY = 0;

      if (isLoop) {
        pathD = `M ${a.x} ${a.y - 28} 
                      C ${a.x - 40} ${a.y - 100}, ${a.x + 40} ${a.y - 100}, ${a.x} ${a.y - 28}`;
        labelX = a.x;
        labelY = a.y - 90 - offset;
      } else {
        // Quadratic Bezier for curve if needed, or simple line
        // We add 'offset' to curvature
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const midX = (a.x + b.x) / 2;
        const midY = (a.y + b.y) / 2;

        // Normal vector for offset
        const dist = Math.sqrt(dx * dx + dy * dy);
        const nomX = -dy / dist;
        const nomY = dx / dist;

        const curveness = 30 + Math.abs(offset * 2);
        // Apply curvature mostly if it is backward edge or to separate

        const cpX = midX + nomX * offset * 3;
        const cpY = midY + nomY * offset * 3 - (Math.abs(dx) > 0 ? 30 : 0); // slight arc up

        pathD = `M ${a.x} ${a.y} Q ${cpX} ${cpY} ${b.x} ${b.y}`;

        labelX = cpX;
        labelY = cpY; // approximate
      }

      const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.setAttribute("d", pathD);
      path.setAttribute("id", `edge-${t.from}-${t.to}-${t.symbol}-${t.id || i}`); // logic ID
      path.setAttribute("class", "edge");
      path.setAttribute("fill", "none");
      path.setAttribute("stroke", t.symbol === "ε" ? "#777" : "#aaa");
      path.setAttribute("stroke-width", "2");
      path.setAttribute("stroke-dasharray", t.symbol === "ε" ? "5,5" : "0");
      path.setAttribute("marker-end", "url(#arrow)");
      svg.appendChild(path);

      const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
      text.setAttribute("x", labelX);
      text.setAttribute("y", labelY);
      text.setAttribute("fill", "#ddd");
      text.setAttribute("font-size", "14");
      text.setAttribute("text-anchor", "middle");
      text.setAttribute("class", "edge-label");
      text.textContent = t.symbol;

      // Background for text readability
      const bbox = { x: labelX - 10, y: labelY - 10, width: 20, height: 20 }; // approx
      const bg = document.createElementNS("http://www.w3.org/2000/svg", "rect");
      bg.setAttribute("x", bbox.x);
      bg.setAttribute("y", bbox.y);
      bg.setAttribute("width", bbox.width);
      bg.setAttribute("height", bbox.height);
      bg.setAttribute("fill", "#1e1e1e");
      svg.appendChild(bg);

      svg.appendChild(text);

      // Store DOM ref for animation
      t.domElement = path;
    });
  });

  // --- States ---
  Object.keys(pos).forEach(s => {
    const { x, y } = pos[s];
    const isAccept = nfa.accept.includes(s);
    const isStart = s === nfa.start;

    // Start Arrow
    if (isStart) {
      const arrow = document.createElementNS("http://www.w3.org/2000/svg", "path");
      arrow.setAttribute("d", `M ${x - 60} ${y} L ${x - 30} ${y}`);
      arrow.setAttribute("stroke", "#4ec9b0");
      arrow.setAttribute("stroke-width", "3");
      arrow.setAttribute("marker-end", "url(#arrow-active)");
      svg.appendChild(arrow);
    }

    // Group for State
    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
    g.setAttribute("id", `state-${s}`);

    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", x);
    circle.setAttribute("cy", y);
    circle.setAttribute("r", 20);
    circle.setAttribute("fill", "#252526");
    circle.setAttribute("stroke", isAccept ? "#4ec9b0" : "#9cdcfe");
    circle.setAttribute("stroke-width", "3");
    g.appendChild(circle);

    if (isAccept) {
      const inner = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      inner.setAttribute("cx", x);
      inner.setAttribute("cy", y);
      inner.setAttribute("r", 15);
      inner.setAttribute("fill", "none");
      inner.setAttribute("stroke", "#4ec9b0");
      inner.setAttribute("stroke-width", "2");
      g.appendChild(inner);
    }

    const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
    label.setAttribute("x", x);
    label.setAttribute("y", y + 5);
    label.setAttribute("fill", "white");
    label.setAttribute("font-size", "12");
    label.setAttribute("text-anchor", "middle");
    label.textContent = s;
    g.appendChild(label);

    svg.appendChild(g);
  });
}

function highlightStep(index) {
  if (!simulationHistory || index < 0 || index >= simulationHistory.length) return;

  const step = simulationHistory[index];

  // 1. Reset all styles
  document.querySelectorAll("circle").forEach(c => c.setAttribute("fill", "#252526"));
  document.querySelectorAll(".edge").forEach(e => {
    e.setAttribute("stroke", (e.getAttribute("stroke-dasharray") !== "0") ? "#777" : "#aaa");
    e.setAttribute("stroke-width", "2");
  });
  document.querySelectorAll("path[marker-end='url(#arrow-active)']").forEach(p => p.setAttribute("marker-end", "url(#arrow)"));


  // 2. Highlight Active States
  step.active.forEach(sBackendName => {
    const sName = stateMap[sBackendName];
    if (sName) {
      const g = document.getElementById(`state-${sName}`);
      if (g) {
        g.querySelector("circle").setAttribute("fill", "#264f78"); // Active Color
      }
    }
  });

  // 3. Highlight Transitions Taken
  if (step.transitions) {
    step.transitions.forEach(t => {
      const fromName = stateMap[t.from];
      const toName = stateMap[t.to];
      const symbol = t.symbol;

      // Find matching DOM elements.
      // Since we didn't store backend IDs in DOM, we search by matching attributes.
      // This is slightly inefficient but robust unless we have duplicate edges with same symbol (NFA allows this)
      // Better: nfaData has 'transitions' with 'from' and 'to' mapped.
      // We can iterate nfaData.transitions to find which one matches t.from/t.to/t.symbol
      // AND has a domElement.

      if (nfaData && nfaData.transitions) {
        nfaData.transitions.forEach(nfaT => {
          if (nfaT.from === fromName && nfaT.to === toName && nfaT.symbol === symbol) {
            if (nfaT.domElement) {
              nfaT.domElement.setAttribute("stroke", "#4ec9b0");
              nfaT.domElement.setAttribute("stroke-width", "4");
            }
          }
        });
      }
    });
  }
}

// Helper to update controls - placeholder if HTML doesn't have them
function updateSimulationControls() {
  const status = document.getElementById("status");
  if (!status) return;

  if (simulationHistory.length === 0) {
    status.textContent = "";
    return;
  }

  const step = simulationHistory[currentStep];
  const total = simulationHistory.length;
  let info = `Step ${currentStep + 1}/${total}`;

  if (step.step === "initial") {
    info += " (Start)";
  } else if (step.step === "consume") {
    info += ` [Consume '${step.char}']`;
  } else if (step.step === "epsilon") {
    info += " [ε-closure]";
  }

  // Check acceptance at the last step
  if (currentStep === total - 1) {
    // We know the result is in the parent response object, but we only stored 'steps' in simulationHistory.
    // We can infer acceptance by checking if any active state is an accept state.
    // But nfaData has accept states.
    const isAccepted = step.active.some(s => nfaData.accept.includes(stateMap[s] || s));
    // Note: stateMap maps Backend->Frontend. nfaData.accept has Frontend names.
    // So we need to map step.active (Backend) -> Frontend first.

    info += isAccepted ? " ✅ ACCEPTED" : " ❌ REJECTED";
    status.style.color = isAccepted ? "#4ec9b0" : "#f44747";
  } else {
    status.style.color = "#ddd";
  }

  status.textContent = info;
}

function nextStep() {
  if (currentStep < simulationHistory.length - 1) {
    currentStep++;
    highlightStep(currentStep);
    updateSimulationControls();
  }
}

function prevStep() {
  if (currentStep > 0) {
    currentStep--;
    highlightStep(currentStep);
    updateSimulationControls();
  }
}

// Expose to global scope for HTML buttons
window.buildNFA = buildNFA;
window.simulate = simulate;
window.nextStep = nextStep;
window.prevStep = prevStep;

