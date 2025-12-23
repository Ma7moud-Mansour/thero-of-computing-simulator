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

    // Drag State
    this.dragState = null; // { nodeId, startX, startY, initialNodeX, initialNodeY }

    // Bind methods
    this.handleMouseMove = this.handleMouseMove.bind(this);
    this.handleMouseUp = this.handleMouseUp.bind(this);

    // Global listeners for drag
    document.addEventListener("mousemove", this.handleMouseMove);
    document.addEventListener("mouseup", this.handleMouseUp);
  }

  initDefs() {
    if (this.defsInjected) return;
    const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
    defs.innerHTML = `
            <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#777" />
            </marker>
            <marker id="arrow-active" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto">
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

    // Store layout for updates
    this.layout = layout;
    const { positions, ranks } = layout;

    // reset drag state on redraw
    this.dragState = null;

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
    g.style.cursor = "grab";

    // Colors
    let strokeColor = "#9cdcfe"; // Default Blue
    if (isAccept) strokeColor = "#4ec9b0"; // Green (if marked accept in NFA/DFA)

    // Explicit TM States
    if (name === "q_accept") strokeColor = "#4ec9b0";
    else if (name === "q_reject") strokeColor = "#f44747";

    // Drag start listener
    g.addEventListener("mousedown", (e) => this.handleMouseDown(e, name));

    // Start Indicator
    if (isStart) {
      const arrow = document.createElementNS("http://www.w3.org/2000/svg", "path");
      const sourcePt = { x: pos.x - 60, y: pos.y };
      const boundaryPt = this.getBoundaryPoint(pos, sourcePt, 22);

      arrow.setAttribute("d", `M ${sourcePt.x} ${sourcePt.y} L ${boundaryPt.x} ${boundaryPt.y}`);
      arrow.setAttribute("stroke", "#4ec9b0");
      arrow.setAttribute("stroke-width", "3");
      arrow.setAttribute("marker-end", "url(#arrow-active)");
      g.appendChild(arrow);
    }

    // Outer Circle
    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", pos.x);
    circle.setAttribute("cy", pos.y);
    circle.setAttribute("r", 20);
    circle.setAttribute("fill", "#252526");
    circle.setAttribute("stroke", strokeColor);
    circle.setAttribute("stroke-width", "3");
    g.appendChild(circle);

    // Inner Circle (Accept)
    // Show inner circle for regular accepted states OR q_accept
    if (isAccept || name === "q_accept") {
      const inner = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      inner.setAttribute("cx", pos.x);
      inner.setAttribute("cy", pos.y);
      inner.setAttribute("r", 15);
      inner.setAttribute("fill", "none");
      inner.setAttribute("stroke", strokeColor);
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



  // --- Geometry Helpers ---

  getBoundaryPoint(center, target, radius) {
    const dx = target.x - center.x;
    const dy = target.y - center.y;
    const dist = Math.sqrt(dx * dx + dy * dy);

    if (dist === 0) return { x: center.x, y: center.y - radius }; // Default for loops

    const scale = radius / dist;
    return {
      x: center.x + dx * scale,
      y: center.y + dy * scale
    };
  }

  intersectLineLine(p1, p2, p3, p4) {
    // Check if line segment p1-p2 intersects p3-p4
    const det = (p2.x - p1.x) * (p4.y - p3.y) - (p4.x - p3.x) * (p2.y - p1.y);
    if (det === 0) return false;

    const lambda = ((p4.y - p3.y) * (p4.x - p1.x) + (p3.x - p4.x) * (p4.y - p1.y)) / det;
    const gamma = ((p1.y - p2.y) * (p4.x - p1.x) + (p2.x - p1.x) * (p4.y - p1.y)) / det;

    return (0 < lambda && lambda < 1) && (0 < gamma && gamma < 1);
  }

  drawEdges(nfa, positions, ranks) {
    // Group edges
    const groups = {};
    const pairCounts = {}; // Track A-B vs B-A

    nfa.transitions.forEach(t => {
      const key = `${t.from}|${t.to}`;
      if (!groups[key]) groups[key] = [];
      groups[key].push(t);

      // Track bidirectional existence
      const pairKey = [t.from, t.to].sort().join('|');
      pairCounts[pairKey] = (pairCounts[pairKey] || 0) + 1;
    });

    Object.values(groups).forEach(group => {
      const { from, to } = group[0];

      // We rely on this.layout.positions being up-to-date
      const a = positions[from];
      const b = positions[to];
      const rankA = a.rank;
      const rankB = b.rank;

      // Determine if bidirectional
      const isReverse = groups[`${to}|${from}`] !== undefined && from !== to;

      group.forEach((t, index) => {
        const isEpsilon = t.symbol === "ε";

        // Calculate Path
        const { pathD, labelX, labelY } = this.calculateEdgePath(
          a, b, index, group.length, from, to, isReverse
        );

        // Draw Path
        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        path.setAttribute("d", pathD);
        path.setAttribute("fill", "none");
        path.setAttribute("stroke", isEpsilon ? "#777" : "#aaa");
        path.setAttribute("stroke-width", "2");
        path.setAttribute("stroke-dasharray", isEpsilon ? "5,5" : "0");
        path.setAttribute("marker-end", "url(#arrow)");
        this.svg.appendChild(path);

        // Label Group (rect + text) for easier updating
        const labelGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");

        // Label Box
        const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        rect.setAttribute("x", labelX - 10);
        rect.setAttribute("y", labelY - 10);
        rect.setAttribute("width", 20);
        rect.setAttribute("height", 20);
        rect.setAttribute("fill", "#1e1e1e");
        labelGroup.appendChild(rect);

        const txt = document.createElementNS("http://www.w3.org/2000/svg", "text");
        txt.setAttribute("x", labelX);
        txt.setAttribute("y", labelY + 4);
        txt.setAttribute("text-anchor", "middle");
        txt.setAttribute("fill", "#ddd");
        txt.setAttribute("font-size", "12");

        if (t.read !== undefined) {
          // TM Label
          txt.textContent = `${t.read} → ${t.write}, ${t.move}`;
          // Resize rect approx
          const w = txt.textContent.length * 6 + 10;
          rect.setAttribute("width", w);
          rect.setAttribute("x", labelX - w / 2);
        } else if (t.pop !== undefined && t.push !== undefined) {
          // PDA Label
          // Use Z0 -> Z0 unless it's a real push/pop (which it isn't in Strict mode, but let's be generic)
          // Format: input, pop -> push
          const sym = t.symbol || "ε";
          txt.textContent = `${sym}, ${t.pop} → ${t.push}`;
          const w = txt.textContent.length * 6 + 10;
          rect.setAttribute("width", w);
          rect.setAttribute("x", labelX - w / 2);
        } else {
          txt.textContent = t.symbol;
        }

        labelGroup.appendChild(txt);

        this.svg.appendChild(labelGroup);

        this.edgeMap.push({
          dom: path,
          labelGroup: labelGroup, // Store label group
          rect: rect,
          text: txt,
          data: t,
          from: from,
          to: to,
          index: index,
          groupSize: group.length,
          rankA: rankA,
          rankB: rankB,
          isReverse: isReverse // Store for drag updates
        });
      });
    });
  }

  calculateEdgePath(a, b, index, groupSize, fromId, toId, isReverse) {
    const RADIUS = 22; // 20 + padding for stroke

    let pathD = "";
    let cpX, cpY, labelX, labelY;

    if (fromId === toId) {
      // --- Self-Loop ---
      // Arc above the node
      const angSpan = Math.PI / 4; // 45 degrees
      const startAng = -Math.PI / 2 - angSpan / 2;
      const endAng = -Math.PI / 2 + angSpan / 2;

      // Fan out loops if multiple
      const offset = (index - (groupSize - 1) / 2) * 15;
      const loopH = 40 + Math.abs(offset) + (groupSize * 5);

      const sx = a.x + RADIUS * Math.cos(startAng - (offset * 0.05));
      const sy = a.y + RADIUS * Math.sin(startAng - (offset * 0.05));
      const ex = a.x + RADIUS * Math.cos(endAng + (offset * 0.05));
      const ey = a.y + RADIUS * Math.sin(endAng + (offset * 0.05));

      // Cubic Bezier Control Points
      const c1x = a.x - 10 - offset;
      const c1y = a.y - loopH;
      const c2x = a.x + 10 + offset;
      const c2y = a.y - loopH;

      pathD = `M ${sx} ${sy} C ${c1x} ${c1y}, ${c2x} ${c2y}, ${ex} ${ey}`;

      labelX = a.x + offset;
      labelY = a.y - loopH - 10;

    } else {
      // --- Standard Edge ---

      // Base Logic: 
      // If single connection (groupSize=1) AND not bidirectional -> Straight Line
      // UNLESS: Collision detected

      let isSimple = groupSize === 1 && !isReverse;

      const start = this.getBoundaryPoint(a, b, RADIUS);
      const end = this.getBoundaryPoint(b, a, RADIUS);

      // Check collisions to force curve
      if (isSimple) {
        // Iterate other edges
        for (let edge of this.edgeMap) {
          // Self check (skip if not created yet or same)
          if (!edge.dom) continue;

          // Skip connected edges (sharing ends)
          if (edge.from === fromId || edge.from === toId || edge.to === fromId || edge.to === toId) continue;

          // Get edge positions
          const otherA = this.layout.positions[edge.from];
          const otherB = this.layout.positions[edge.to];

          // Only check Line-Line intersection (ignoring curve-line for perf/complexity)
          // Ideally we'd check path bounding boxes if we want perfection.
          // Here: Check if our straight line crosses their straight line (approx)
          if (this.intersectLineLine(a, b, otherA, otherB)) {
            isSimple = false;
            break;
          }
        }
      }

      if (isSimple) {
        pathD = `M ${start.x} ${start.y} L ${end.x} ${end.y}`;
        labelX = (start.x + end.x) / 2;
        labelY = (start.y + end.y) / 2;
      } else {
        // Curvature needed
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const midX = (a.x + b.x) / 2;
        const midY = (a.y + b.y) / 2;

        // Fan out
        // Base offset for bidirectional separation
        const biDirOffset = isReverse ? 30 : 0;

        // If we forced curve due to collision but no other group reasons, ensure min curve
        const baseCurve = (!isReverse && groupSize === 1) ? 40 : 0;

        // Multi-edge spread
        const spread = (index - (groupSize - 1) / 2) * 20;

        const totalCurve = biDirOffset + spread + baseCurve;

        // Normal vector
        const len = Math.sqrt(dx * dx + dy * dy);
        const nx = -dy / len;
        const ny = dx / len;

        cpX = midX + nx * totalCurve;
        cpY = midY + ny * totalCurve;

        // Improve start/end attachment for curves
        // Instead of center-to-center boundary, we can angle the start/end slightly
        // based on the control point to make it look "attached" naturally.

        const curvStart = this.getBoundaryPoint(a, { x: cpX, y: cpY }, RADIUS);
        const curvEnd = this.getBoundaryPoint(b, { x: cpX, y: cpY }, RADIUS);

        pathD = `M ${curvStart.x} ${curvStart.y} Q ${cpX} ${cpY} ${curvEnd.x} ${curvEnd.y}`;

        // Label at T=0.5
        labelX = 0.25 * curvStart.x + 0.5 * cpX + 0.25 * curvEnd.x;
        labelY = 0.25 * curvStart.y + 0.5 * cpY + 0.25 * curvEnd.y;
      }
    }

    return { pathD, labelX, labelY };
  }

  handleMouseDown(event, nodeId) {
    event.stopPropagation(); // Prevent panning if implemented on bg
    event.preventDefault();

    const nodePos = this.layout.positions[nodeId];

    // Get mouse pos relative to SVG
    const pt = this.svg.createSVGPoint();
    pt.x = event.clientX;
    pt.y = event.clientY;
    const svgP = pt.matrixTransform(this.svg.getScreenCTM().inverse());

    this.dragState = {
      nodeId: nodeId,
      startX: svgP.x,
      startY: svgP.y,
      initialNodeX: nodePos.x,
      initialNodeY: nodePos.y
    };

    // Visual feedback
    if (this.stateMap[nodeId]) {
      this.stateMap[nodeId].style.cursor = "grabbing";
    }
  }

  handleMouseMove(event) {
    if (!this.dragState) return;

    event.preventDefault();

    const { nodeId, startX, startY, initialNodeX, initialNodeY } = this.dragState;

    // Current Mouse Pos
    const pt = this.svg.createSVGPoint();
    pt.x = event.clientX;
    pt.y = event.clientY;
    const svgP = pt.matrixTransform(this.svg.getScreenCTM().inverse());

    const dx = svgP.x - startX;
    const dy = svgP.y - startY;

    // Update Node Logic Position
    const newX = initialNodeX + dx;
    const newY = initialNodeY + dy;

    this.layout.positions[nodeId].x = newX;
    this.layout.positions[nodeId].y = newY;

    // Update Node Visuals
    const g = this.stateMap[nodeId];
    if (g) {
      // We need to update all children or transform the group. 
      // Original code sets cx/cy on circles and x/y on text/path.
      // It's cleaner to transform the group, BUT the original code didn't use transform.
      // Let's update the attributes directly to match the renderer style.

      // 1. Update Start Arrow (if exists)
      const arrow = g.querySelector("path[marker-end]");
      if (arrow) {
        // Same logic as create: source is (newX - 60, newY)
        const sourcePt = { x: newX - 60, y: newY };
        // The node center is (newX, newY). 
        // getBoundaryPoint(center, target, radius)
        // We want point on boundary of (newX, newY) towards sourcePt
        const boundaryPt = this.getBoundaryPoint({ x: newX, y: newY }, sourcePt, 22);

        arrow.setAttribute("d", `M ${sourcePt.x} ${sourcePt.y} L ${boundaryPt.x} ${boundaryPt.y}`);
      }

      // 2. Update Circles
      const circles = g.querySelectorAll("circle");
      circles.forEach(c => {
        c.setAttribute("cx", newX);
        c.setAttribute("cy", newY);
      });

      // 3. Update Text
      const text = g.querySelector("text");
      if (text) {
        text.setAttribute("x", newX);
        text.setAttribute("y", newY + 5);
      }
    }

    // Update Edges
    this.updateConnectedEdges(nodeId);
  }

  handleMouseUp(event) {
    if (this.dragState) {
      if (this.stateMap[this.dragState.nodeId]) {
        this.stateMap[this.dragState.nodeId].style.cursor = "grab";

        // Re-calculate drag state one last time to snap perfect positions? 
        // Not needed, but we can ensure visual states are cleared.
      }
      this.dragState = null;
    }
  }

  updateConnectedEdges(movedNodeId) {
    // Find edges connected to this node
    const connectedEdges = this.edgeMap.filter(e => e.from === movedNodeId || e.to === movedNodeId);

    connectedEdges.forEach(edge => {
      const a = this.layout.positions[edge.from];
      const b = this.layout.positions[edge.to];

      const { pathD, labelX, labelY } = this.calculateEdgePath(
        a, b, edge.index, edge.groupSize, edge.from, edge.to, edge.isReverse
      );


      // Update Path
      edge.dom.setAttribute("d", pathD);

      // Update Label
      if (edge.labelGroup) { // Check if we are using the new group structure
        const rect = edge.labelGroup.querySelector("rect");
        const txt = edge.labelGroup.querySelector("text");

        if (rect) {
          rect.setAttribute("x", labelX - 10);
          rect.setAttribute("y", labelY - 10);
        }
        if (txt) {
          txt.setAttribute("x", labelX);
          txt.setAttribute("y", labelY + 4);
        }
      }
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
    this.mode = 'NFA'; // 'NFA', 'DFA', or 'TM'
    this.tmCache = null;
    this.currentInputString = "";

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
      this.currentInputString = "";
      document.getElementById("inputTracker").innerHTML = "";
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
      if (this.mode === 'PDA') endpoint = '/simulate/pda';
      if (this.mode === 'CFG_PDA') endpoint = '/simulate/cfg/pda';

      let payload = { regex, string };
      if (this.mode === 'TM') {
        if (!this.tmCache) {
          alert("Please construct TM first");
          return;
        }
        payload = { tm: this.tmCache, string };
      }
      if (this.mode === 'CFG_PDA') {
        // Need grammar and start symbol
        // We can cache them in `this.cfgCache` when building PDA
        if (!this.cfgCache) {
          alert("Please construct PDA from CFG first");
          return;
        }
        payload = { ...this.cfgCache, string };
      }

      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      this.history = data.steps;
      this.currentInputString = string;
      this.renderInputTracker(string);

      // CRITICAL: DO NOT Update Data or Redraw Graph
      // The graph (NFA/DFA/PDA/TM) is static during simulation.
      // this.nfaData = ... (REMOVED)
      // this.renderer.draw(...) (REMOVED)

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

    // Update Text Elements
    // If in CFG mode, update cfg specific elements if needed, or share IDs?
    // The Status Text and Step Counter are shared IDs if we didn't duplicate them.
    // In index.html, we created `cfgStepCounter` and `cfgStatusText` for CFG tab.
    // We should update those if in CFG mode.

    if (this.mode === 'CFG_PDA') {
      const sc = document.getElementById("cfgStepCounter");
      const st = document.getElementById("cfgStatusText");
      if (sc) sc.innerText = `Step ${this.currentStep + 1} / ${this.history.length}`;
      if (st) st.innerText = step.description || step.step;
    } else {
      document.getElementById("stepCounter").innerText = `Step ${this.currentStep + 1} / ${this.history.length}`;
      document.getElementById("statusText").innerText = step.description || step.step;
    }

    // Update Input Tracker
    if (this.mode === 'TM') {
      this.updateInputTracker(step.head);
    } else {
      // Step 0 is initial, Step 1 processes char 0, etc.
      const charIndex = this.currentStep - 1;
      this.updateInputTracker(charIndex);
    }

    if (this.mode === 'TM') {
      document.getElementById("tape-container").style.display = "block";
      const tapeArr = step.tape ? step.tape.split('') : ["_"];
      this.renderTape(tapeArr, step.head);

      // Update Info Panel
      document.getElementById("tm-time").innerText = `Time: ${this.currentStep}`;
      document.getElementById("tm-state").innerText = `State: ${step.state}`;

      const t = step.transitions && step.transitions[0];
      if (t) {
        document.getElementById("tm-transition").innerText = `Transition: ${t.label}`;
      } else if (this.currentStep === 0) {
        document.getElementById("tm-transition").innerText = `Start Configuration`;
      } else {
        document.getElementById("tm-transition").innerText = `Halted`;
      }
    } else {
      document.getElementById("tape-container").style.display = "none";
    }

    if (this.mode === 'PDA' || this.mode === 'CFG_PDA') {
      document.getElementById("stack-container").style.display = "block";
      this.renderStack(step.stack || ["Z0"]);
    } else {
      document.getElementById("stack-container").style.display = "none";
    }

    if (this.currentStep === this.history.length - 1) {
      let accepted = false;
      let rejected = false;

      if (this.mode === 'TM') {
        // TM Checks Exact State
        if (step.state === "q_accept") accepted = true;
        if (step.state === "q_reject") rejected = true;

        if (step.state && step.state.startsWith("REJECTED")) rejected = true;
      } else {
        // NFA/DFA/PDA Check
        // PDA active states effectively same as NFA
        // For CFG PDA, we check acceptance by empty stack or accept state?
        // Our backend simulate_general_pda checks accept state.
        if (step.active) {
          accepted = step.active.some(s => this.nfaData.accept.includes(s));
        }
      }

      const statusEl = (this.mode === 'CFG_PDA') ? document.getElementById("cfgStatusText") : document.getElementById("statusText");
      if (accepted) {
        statusEl.innerText = "Halted & Accepted ✅";
        statusEl.style.color = "#4ec9b0";
      } else if (rejected) {
        statusEl.innerText = "Halted & Rejected ❌";
        statusEl.style.color = "#f44747";
      } else {
        if (this.mode === 'TM') {
          statusEl.innerText = "Stopped (Limit Reached) ⚠️";
          statusEl.style.color = "#dcdcaa";
        } else {
          statusEl.innerText = "Rejected ❌";
          statusEl.style.color = "#f44747";
        }
      }
    } else {
      const statusEl = (this.mode === 'CFG_PDA') ? document.getElementById("cfgStatusText") : document.getElementById("statusText");
      statusEl.style.color = "#d4d4d4";
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
      if (!res.ok) throw new Error((await res.json()).detail);
      const dfa = await res.json();

      this.nfaData = dfa;
      const layout = this.layoutEngine.compute(this.nfaData, { xSpacing: 350, ySpacing: 250 });
      this.renderer.draw(this.nfaData, layout);

      this.resetSimulation();
      this.currentInputString = "";
      document.getElementById("inputTracker").innerHTML = "";
      document.getElementById("statusText").innerText = "DFA Ready";
      document.getElementById("stepCounter").innerText = "Deterministic Finite Automaton";

      document.getElementById("tape-container").style.display = "none";
      document.getElementById("stack-container").style.display = "none";
    } catch (e) {
      console.error(e);
      alert(e.message || "Error building DFA");
    }
  }

  async loadPDA(regex) {
    try {
      this.mode = 'PDA';
      document.getElementById("statusText").innerText = "Building PDA...";
      const res = await fetch(`${API_BASE}/pda`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ regex })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail);
      }
      const pda = await res.json();

      this.nfaData = this.normalize(pda);
      const layout = this.layoutEngine.compute(this.nfaData, { xSpacing: 200, ySpacing: 150 });
      this.renderer.draw(this.nfaData, layout);

      document.getElementById("tape-container").style.display = "none";
      document.getElementById("stack-container").style.display = "none";

      this.resetSimulation();
      this.currentInputString = "";
      document.getElementById("inputTracker").innerHTML = "";

      document.getElementById("statusText").innerText = "PDA Ready";
      document.getElementById("stepCounter").innerText = "Strict PDA (NFA Wrapper)";

    } catch (e) {
      console.error(e);
      alert(e.message || "Error building PDA");
    }
  }

  async loadTM(regex) {
    try {
      this.mode = 'TM';
      document.getElementById("statusText").innerText = "Building Turing Machine...";
      const res = await fetch(`${API_BASE}/build_tm`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ regex })
      });
      if (!res.ok) throw new Error((await res.json()).detail);
      const tm = await res.json();

      this.tmCache = tm;
      this.nfaData = tm;

      const layout = this.layoutEngine.compute(this.nfaData, { xSpacing: 350, ySpacing: 250 });
      this.renderer.draw(this.nfaData, layout);

      this.resetSimulation();
      this.currentInputString = "";
      document.getElementById("inputTracker").innerHTML = "";
      document.getElementById("statusText").innerText = "TM Ready";
      document.getElementById("stepCounter").innerText = "Standard Single-Tape TM";

      document.getElementById("tape-container").style.display = "block";
      this.renderTape(["_"], 0);
      document.getElementById("stack-container").style.display = "none";

    } catch (e) {
      console.error(e);
      alert(e.message || "Error building TM");
    }
  }

  renderInputTracker(string) {
    let containerId = "inputTracker";
    if (this.mode === 'CFG_PDA') containerId = "inputTrackerCFG";

    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = "";
    if (!string) {
      const span = document.createElement("span");
      span.innerText = "ε";
      span.style.color = "#777";
      container.appendChild(span);
      return;
    }

    for (let i = 0; i < string.length; i++) {
      const span = document.createElement("span");
      span.innerText = string[i];
      span.id = `tracker-char-${i}`;
      span.style.padding = "0 2px";
      span.style.transition = "color 0.2s, transform 0.2s";
      container.appendChild(span);
    }
  }

  updateInputTracker(currentIndex) {
    const string = this.currentInputString;
    for (let i = 0; i < string.length; i++) {
      const span = document.getElementById(`tracker-char-${i}`);
      if (!span) continue;

      if (i < currentIndex) {
        span.style.color = "var(--success)"; // Green
        span.style.fontWeight = "normal";
        span.style.transform = "scale(1)";
      } else if (i === currentIndex) {
        span.style.color = "#f1c40f"; // Yellow/Gold
        span.style.fontWeight = "bold";
        span.style.transform = "scale(1.3)";
      } else {
        span.style.color = "#777"; // Gray
        span.style.fontWeight = "normal";
        span.style.transform = "scale(1)";
      }
    }
  }

  renderTape(tapeChars, headPos) {
    const container = document.getElementById("tape-content");
    if (!container) return;
    container.innerHTML = "";

    // Windowed View: Show e.g., radius=5 cells around head
    const radius = 6;
    for (let i = headPos - radius; i <= headPos + radius; i++) {
      const cell = document.createElement("div");
      cell.className = "tape-cell";

      // Determine content
      let char = "_";
      if (i >= 0 && i < tapeChars.length) char = tapeChars[i];

      if (char === "_") {
        cell.classList.add("blank");
        cell.innerText = "␣";
      } else {
        cell.innerText = char;
      }

      if (i === headPos) {
        cell.classList.add("active");
      }

      container.appendChild(cell);
    }
  }

  renderStack(stack) {
    const container = document.getElementById("stack-content");
    if (!container) return;
    container.innerHTML = "";
    if (!stack || stack.length === 0) {
      container.innerHTML = "<em>(empty)</em>";
      return;
    }
    // Stack visual: item[0] is bottom ?? Usually visual stack is top at top.
    // CSS is column-reverse, so first child is at bottom.
    // If stack list is [bottom, ..., top], then traversing and appending puts bottom at bottom (if column-reverse).
    // Let's assume stack (from backend) is [Z0].
    stack.forEach(symbol => {
      const div = document.createElement("div");
      div.innerText = symbol;
      div.style.cssText = "border: 1px solid #555; padding: 5px 10px; background: #252526; color: #fff; width: 80%; text-align: center; border-radius: 4px; font-weight: bold;";
      container.appendChild(div);
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

// Tab Logic
window.switchTab = (tab) => {
  document.querySelectorAll('.tab-content').forEach(el => el.style.display = 'none');
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.style.background = 'transparent';
    btn.style.color = '#aaa';
    if (btn.className.includes('active')) btn.classList.remove('active'); // fallback
  });

  if (tab === 'regex') {
    document.getElementById('tab-regex').style.display = 'block';
    document.getElementById('btn-regex').style.background = '#444';
    document.getElementById('btn-regex').style.color = 'white';

    // Show correct canvas
    document.getElementById("canvas").style.display = "block";

  } else if (tab === 'cfg') {
    document.getElementById('tab-cfg').style.display = 'block';
    document.getElementById('btn-cfg').style.background = '#444';
    document.getElementById('btn-cfg').style.color = 'white';
    document.getElementById("canvas").style.display = "block"; // Canvas visible for CFG Treehide it until PDA is built
    // For now, let's keep canvas visible but maybe clear it if user wants
  }
};

// Global Functions
window.buildNFA = () => {
  const regex = document.getElementById("regex").value;
  simulator.loadNFA(regex);
};

window.buildDFA = () => {
  const regex = document.getElementById("regex").value;
  simulator.loadDFA(regex);
};

window.buildPDA = () => {
  const regex = document.getElementById("regex").value;
  simulator.loadPDA(regex);
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

// CFG Functions
// Helper to parse textarea
function parseGrammarInput() {
  const raw = document.getElementById("grammarInput").value.trim();
  const lines = raw.split('\n');
  const grammar = {};
  let start = null;

  lines.forEach(line => {
    if (!line.trim()) return;
    // Format: S -> a S b | epsilon
    const parts = line.split('->');
    if (parts.length < 2) return;

    const lhs = parts[0].trim();
    if (!start) start = lhs;

    const rhsParts = parts[1].split('|');
    if (!grammar[lhs]) grammar[lhs] = [];

    rhsParts.forEach(r => {
      let production = r.trim();
      if (production === 'ε' || production === 'epsilon') {
        grammar[lhs].push(""); // empty string
      } else {
        // Split by spaces? Or chars? 
        // Project requirement usually implies single char terminals unless space separated.
        // Let's assume space separated for safety, or chars if no spaces.
        // Ideally backend handles this. Let's send list of strings.
        // For simplicity here, let's split by space if spaces exist, else chars.
        if (production.includes(' ')) {
          grammar[lhs].push(production.split(/\s+/));
        } else {
          grammar[lhs].push(production.split(''));
        }
      }
    });
  });
  return { grammar, start };
}

window.parseCFG = async () => {
  try {
    const { grammar, start } = parseGrammarInput();
    const string = document.getElementById("cfgInputString").value;
    const res = await fetch(`${API_BASE}/cfg/parse`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ grammar, start, string })
    });
    const data = await res.json();

    const resultDiv = document.getElementById("cfg-result-text");
    const derivDiv = document.getElementById("cfg-derivation-steps");
    const derivContent = document.getElementById("cfg-derivation-content");
    const svg = document.getElementById("canvas");

    // Reset UI
    derivDiv.style.display = "none";
    svg.innerHTML = ""; // clear Main Canvas

    if (data.accepted) {
      resultDiv.innerText = "Accepted ✅";
      resultDiv.style.color = "#4ec9b0";

      // 1. Show Derivation Steps
      if (data.derivations && data.derivations.length > 0) {
        derivDiv.style.display = "block";
        derivContent.innerText = data.derivations.join("\n↓\n");
      }

      // 2. Visual Tree
      if (data.tree) {
        simulator.renderer.initDefs(); // Ensure definitions exist if we cleared everything
        drawTree(data.tree, svg);
      }

    } else {
      resultDiv.innerText = "Rejected ❌";
      resultDiv.style.color = "#f44747";
    }
  } catch (e) {
    console.error(e);
    document.getElementById("cfg-result-text").innerText = "Error: " + e.message;
  }
};

function renderTreeText(node, prefix = "", isLeft = true) {
  if (!node) return "";

  // Simple Indented Representation
  let result = prefix;
  result += (prefix.length > 0 ? (isLeft ? "├── " : "└── ") : "") + node.symbol + "\n";

  if (node.children) {
    for (let i = 0; i < node.children.length; i++) {
      result += renderTreeText(node.children[i], prefix + (prefix.length > 0 ? (isLeft ? "│   " : "    ") : ""), i < node.children.length - 1);
    }
  }
  return result;
}

function drawTree(root, svg) {
  // Simple Reingold-Tilford compliant or just Layered layout
  // 1. Calculate positions
  const levels = {};
  let maxLevel = 0;

  // DFS to assign levels and count nodes at each level for X spacing (simpler than true RT)
  function traverse(node, depth, offset) {
    if (!node) return 0;
    if (!levels[depth]) levels[depth] = [];

    const obj = { node, x: 0, y: depth * 60 + 40, width: 40 };
    levels[depth].push(obj);
    maxLevel = Math.max(maxLevel, depth);

    let childWidth = 0;
    if (node.children) {
      node.children.forEach(child => {
        childWidth += traverse(child, depth + 1);
      });
    }
    // Store reference to children in obj later? 
    // Actually we need a valid tree logic.
    // Let's use a simpler heuristic:
    // X is based on inorder traversal index? No, leaf count.
  }

  // Better approach: Calculate simple tree layout
  // Check leaf count -> Width
  function getLeafCount(node) {
    if (!node.children || node.children.length === 0) return 1;
    return node.children.reduce((acc, c) => acc + getLeafCount(c), 0);
  }

  const totalLeaves = getLeafCount(root);
  const width = totalLeaves * 50;
  svg.setAttribute("width", Math.max(600, width + 100));
  svg.setAttribute("height", getDepth(root) * 80 + 100);

  let leafCounter = 0;
  function assignPositions(node, depth) {
    if (!node.children || node.children.length === 0) {
      node._x = leafCounter * 50 + 50;
      node._y = depth * 80 + 40;
      leafCounter++;
      return;
    }

    node.children.forEach(c => assignPositions(c, depth + 1));

    // Center over children
    const first = node.children[0];
    const last = node.children[node.children.length - 1];
    node._x = (first._x + last._x) / 2;
    node._y = depth * 80 + 40;
  }

  function getDepth(node) {
    if (!node.children || node.children.length === 0) return 1;
    return 1 + Math.max(...node.children.map(getDepth));
  }

  assignPositions(root, 0);

  // DRAW
  // Edges first
  function drawEdges(node) {
    if (node.children) {
      node.children.forEach(c => {
        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", node._x);
        line.setAttribute("y1", node._y + 15); // bottom of source
        line.setAttribute("x2", c._x);
        line.setAttribute("y2", c._y - 15); // top of target
        line.setAttribute("stroke", "#555");
        line.setAttribute("stroke-width", "2");
        svg.appendChild(line);
        drawEdges(c);
      });
    }
  }
  drawEdges(root);

  // Nodes second
  function drawNodes(node) {
    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");

    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", node._x);
    circle.setAttribute("cy", node._y);
    circle.setAttribute("r", 15);
    circle.setAttribute("fill", "#1e1e1e");
    circle.setAttribute("stroke", "#4ec9b0");
    circle.setAttribute("stroke-width", "2");

    const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
    text.setAttribute("x", node._x);
    text.setAttribute("y", node._y + 5);
    text.setAttribute("text-anchor", "middle");
    text.setAttribute("fill", "white");
    text.setAttribute("font-size", "12px");
    text.textContent = node.symbol === "" ? "ε" : node.symbol;

    g.appendChild(circle);
    g.appendChild(text);
    svg.appendChild(g);

    if (node.children) node.children.forEach(drawNodes);
  }
  drawNodes(root);
}

window.buildCFGPDA = async () => {
  try {
    const { grammar, start } = parseGrammarInput();
    // Since we are reusing the simulator graph logic, we can load it into the renderer
    // But we need a separate endpoint for getting the PDA structure from CFG
    const res = await fetch(`${API_BASE}/cfg/pda`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ grammar, start, string: "" }) // String not needed for build
    });
    const pda = await res.json();

    // Render this PDA
    // We reuse simulator.normalize and renderer.draw
    // Access simulator instance

    // Switch to PDA mode visualization logic
    // We use the same canvas.
    simulator.mode = 'CFG_PDA';
    simulator.cfgCache = { grammar, start }; // Cache for simulation
    simulator.nfaData = simulator.normalize(pda);

    const layout = simulator.layoutEngine.compute(simulator.nfaData, { xSpacing: 250, ySpacing: 150 });
    simulator.renderer.draw(simulator.nfaData, layout);

    document.getElementById("cfg-result-text").innerText = "PDA Constructed (See Graph)";
    document.getElementById("cfg-result-text").style.color = "#dcdcaa";

    // Show Controls
    document.getElementById("cfg-status-panel").style.display = "block";
    document.getElementById("tape-container").style.display = "none";
    document.getElementById("stack-container").style.display = "none"; // Hide initially until sim starts

    simulator.resetSimulation();
    simulator.renderInputTracker("");

  } catch (e) {
    console.error(e);
    alert("Error building PDA");
  }
};

window.simulateCFG = () => {
  const str = document.getElementById("cfgInputString").value;
  // Regex arg is ignored for CFG_PDA mode
  simulator.runSimulation(null, str);
};

// Keyboard Shortcuts
document.addEventListener("keydown", (e) => {
  if (e.key === "ArrowRight") simulator.next();
  if (e.key === "ArrowLeft") simulator.prev();
});

// Build initial
window.onload = () => {
  window.buildNFA();
  window.switchTab('regex'); // Default
};
