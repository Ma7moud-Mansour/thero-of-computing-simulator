let currentStep = 0;
let steps = [];
let positions = {};

function layout(states) {
    const cx = 500, cy = 350, r = 260;
    const step = 2 * Math.PI / states.length;
    let pos = {};
    states.forEach((s, i) => {
      pos[s] = {
        x: cx + r * Math.cos(i * step),
        y: cy + r * Math.sin(i * step)
      };
    });
    return pos;
  }
  

function drawNFA(nfa) {
  const svg = document.getElementById("canvas");
  svg.innerHTML = "";

  layout(nfa.states);

  // transitions
  nfa.transitions.forEach(t => {
    const a = positions[t.from];
    const b = positions[t.to];

    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", a.x);
    line.setAttribute("y1", a.y);
    line.setAttribute("x2", b.x);
    line.setAttribute("y2", b.y);
    line.setAttribute("stroke", t.symbol === "ε" ? "#888" : "#aaa");
    line.setAttribute("stroke-dasharray", t.symbol === "ε" ? "5,5" : "0");

    svg.appendChild(line);
  });

  // states
  nfa.states.forEach(s => {
    const { x, y } = positions[s];
    const c = document.createElementNS("http://www.w3.org/2000/svg", "circle");

    c.setAttribute("cx", x);
    c.setAttribute("cy", y);
    c.setAttribute("r", 28);
    c.setAttribute("fill", "#252526");
    c.setAttribute("stroke", nfa.accept.includes(s) ? "#4ec9b0" : "#9cdcfe");
    c.setAttribute("stroke-width", "3");
    c.setAttribute("id", s);

    svg.appendChild(c);
  });
}
async function simulate() {
    const regex = document.getElementById("regex").value;
    const string = document.getElementById("string").value;
  
    const res = await fetch("http://127.0.0.1:8000/simulate/nfa", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ regex, string })
    });
  
    const data = await res.json();
    drawNFA(data.nfa);
  
    steps = data.steps;
    currentStep = 0;
  
    animate();
  }
  
  function animate() {
    if (currentStep >= steps.length) return;
  
    document.querySelectorAll("circle").forEach(c => {
      c.setAttribute("fill", "#252526");
    });
  
    steps[currentStep].forEach(s => {
      document.getElementById(s).setAttribute("fill", "#007acc");
    });
  
    currentStep++;
    setTimeout(animate, 700);
  }
  
  function drawAutomaton(data) {
    const svg = document.getElementById("canvas");
    svg.innerHTML = "";
  
    const pos = layout(data.states);
  
    data.transitions.forEach(t => {
      const a = pos[t.from], b = pos[t.to];
      let line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("x1", a.x);
      line.setAttribute("y1", a.y);
      line.setAttribute("x2", b.x);
      line.setAttribute("y2", b.y);
      line.setAttribute("stroke", "#aaa");
      svg.appendChild(line);
    });
  
    data.states.forEach(s => {
      const {x,y} = pos[s];
      let c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      c.setAttribute("cx", x);
      c.setAttribute("cy", y);
      c.setAttribute("r", 30);
      c.setAttribute("fill", "#252526");
      c.setAttribute("stroke", data.accept.includes(s) ? "#4ec9b0" : "#9cdcfe");
      c.setAttribute("stroke-width", "3");
      c.setAttribute("id", s);
      svg.appendChild(c);
    });
  }

  function animateSteps(steps) {
    let i = 0;
    function tick() {
      if (i >= steps.length) return;
  
      document.querySelectorAll("circle")
        .forEach(c => c.setAttribute("fill", "#252526"));
  
      steps[i].forEach(s =>
        document.getElementById(s).setAttribute("fill", "#007acc")
      );
  
      i++;
      setTimeout(tick, 700);
    }
    tick();
  }
  