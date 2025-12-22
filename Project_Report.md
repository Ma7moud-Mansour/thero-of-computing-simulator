# Design and Implementation of a Web-Based Automata Simulator for Regular Languages

## Abstract
This project presents a web-based educational tool designed to visualize the theoretical foundations of automata theory. The system addresses the pedagogical challenge of understanding the transformation from Regular Expressions to various automaton models (NFA, DFA, and PDA). By implementing Thompson’s Construction and the Subset Construction algorithm, the system provides an interactive platform where students can define regular languages and observe the step-by-step simulation of input strings. A key feature is the strict formal representation of a Pushdown Automaton (PDA) that simulates Finite Automaton behavior using an invariant stack, adhering to specific academic constraints. The system successfully demonstrates the equivalence of these models through a unified and interactive graphical interface.

## Detailed Description of the Project

### A) What Does It Do?
The primary purpose of this project is to serve as an interactive laboratory for exploring Regular Languages. It allows users to input a Regular Expression and automatically generates the corresponding Nondeterministic Finite Automaton (NFA). Users can further convert this NFA into a Deterministic Finite Automaton (DFA) or a formally defined Pushdown Automaton (PDA). The system simulates the processing of input strings on these automata, highlighting active states and transitions in real-time to demonstrate acceptance or rejection.

### B) Input Format
The system accepts two primary forms of input:
1.  **Regular Expression:** A string representing the language definition. The system supports standard operators including concatenation (implicit or explicit), union (`|`), and Kleene star (`*`). Strict validation ensures that the expression is well-formed (e.g., balanced parentheses, valid operator placement) before any construction begins.
2.  **Test Input String:** A sequence of characters (e.g., `aab`) to be tested against the generated automaton.

### C) Output Format
The system provides multiple visualization and data outputs:
*   **Automaton Graphs:** Directed graphs where nodes represent states and edges represent transitions. Visual distinctions are made for Start states (green), Accept states (double-circled), and Active states (highlighted during simulation).
*   **Simulation History:** A step-by-step log of the computation, showing the current state(s), the input symbol being read, and the decision made.
*   **Result Status:** CLEAR visual indicators for "Halted & Accepted", "Halted & Rejected", or "Rejected".
*   **PDA Stack Visualization:** For the PDA mode, a dedicated panel displays the stack content. Per strict project requirements, this stack is initialized with `Z0` and remains invariant throughout the simulation (`Z0` is never popped or pushed over), visually demonstrating that the regular language can be recognized without utilizing the stack's memory capability.

### D) Inside Mechanism
The system architecture strictly separates the **Definition** of the automaton from its **Simulation**.
1.  **Regex Parsing & Validation:** The input regex is parsed and validated for syntax errors. It is then converted into a postfix expression to facilitate processing.
2.  **NFA Construction:** Thompson’s Construction algorithm is used to build an NFA from the postfix expression. This involves creating basic automata for symbols and combining them using recursive rules for union, concatenation, and star.
3.  **DFA Conversion:** The NFA is converted to a DFA using the Subset Construction (Powerset Construction) algorithm, resulting in a deterministic model equivalent to the original NFA.
4.  **PDA Representation:** The NFA is wrapped in a formal PDA structure. Transitions are mapped from `(q, a) → p` to `(q, a, Z0) → (p, Z0)`. This ensures formally correct PDA syntax while maintaining NFA behavior.
5.  **Simulation Logic:** The simulation runs entirely on the client-side using the pre-computed definition. It does not rebuild the graph. For NFA operations, it computes the epsilon-closure of states at each step. For DFA, it follows the single active state transition.

## Programming Language, Tools & Libraries Used

*   **Backend Language:** Python 3.11
    *   **Framework:** **FastAPI** was chosen for its high performance and automatic validation capabilities. It handles the core logic for regex parsing, automaton construction, and graphical layout computation.
    *   **Libraries:** Standard Python libraries were used for logic to ensure transparency and educational value.
*   **Frontend Language:** JavaScript (ES6+)
    *   **Visualization:** Custom **SVG** rendering engine. No heavy external graphing libraries were used; a custom layout algorithm was implemented to ensure readable state placement.
    *   **Interface:** HTML5 and CSS3 Grid/Flexbox for a responsive layout.
*   **Architecture:** Client-Server model. The backend performs the heavy computational theory logic (automaton construction), while the frontend manages the interactive simulation state and visualization.

## Images of the Project with Output

*(Figure 1: Visualization of an NFA generated from the regex `(a|b)*ab`, showing epsilon transitions and hierarchical structure.)*

*(Figure 2: Simulation of a DFA processing the string `aab`. The current state is highlighted in yellow, and the input tracker shows the current character.)*

*(Figure 3: Strict PDA Representation. The graph displays transitions labeled `(a, Z0 → Z0)`, and the dedicated Stack Panel shows the static `['Z0']` content, verifying strict adherence to the project constraints.)*

## Limitations

*   **Stack Utilization:** The current PDA implementation is strictly limited to simulating Regular Languages. It does not support Context-Free Grammars that require active pushing and popping (e.g., $a^n b^n$), as the stack functionality is intentionally restricted to an invariant `Z0` for this module.
*   **Performance:** The simulation is optimized for educational visualization of small to medium-sized automata. Extremely complex regular expressions may result in visual clutter due to the number of states generated by Thompson’s Construction.
*   **Symbol Support:** The alphabet is currently restricted to standard alphanumeric characters to maintain simplicity in the visualization.
