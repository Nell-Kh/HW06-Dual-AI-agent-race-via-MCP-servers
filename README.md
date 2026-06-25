<div align="center">
  <h1>🚨 The Dual-AI Agent Race 🏃‍♂️💨</h1>
  <p><em>An Advanced Multi-Agent Reinforcement Learning Project powered by LLMs and MCP Servers</em></p>
</div>

---

## 📖 Table of Contents
1. [Project Motivation & Overview](#1-project-motivation--overview)
2. [Why We Built Two Cops: The Evolution of Strategy](#2-why-we-built-two-cops-the-evolution-of-strategy)
3. [Deep Dive: Agent Strategies & Decision Making](#3-deep-dive-agent-strategies--decision-making)
    - [Cop 1: The Deterministic 3-Barrier Sweep](#cop-1-the-deterministic-3-barrier-sweep)
    - [Cop 2: The Chaos Probabilistic Patroller](#cop-2-the-chaos-probabilistic-patroller)
    - [The Thief: The Non-Deterministic Ghost](#the-thief-the-non-deterministic-ghost)
4. [System Architecture (The MCP Backbone)](#4-system-architecture-the-mcp-backbone)
    - [Zero-Cheating Architecture](#zero-cheating-architecture)
    - [The TurnExecutor Flow](#the-turnexecutor-flow)
5. [The LLM Integration & Dynamic Dialogue](#5-the-llm-integration--dynamic-dialogue)
6. [Reinforcement Learning & Q-Tables](#6-reinforcement-learning--q-tables)
7. [The Autonomous Simulation Pipeline](#7-the-autonomous-simulation-pipeline)
8. [Analytics, Metrics, & Learning Curves](#8-analytics-metrics--learning-curves)
9. [Cinematic HTML Replays & User Interface](#9-cinematic-html-replays--user-interface)
10. [Setup & Installation Instructions](#10-setup--installation-instructions)

---

## 1. Project Motivation & Overview

**The Dual-AI Agent Race** is a highly competitive, multi-agent simulation where a **Cop** hunts down a **Thief** on a 5x5 grid. The core constraint and unique technical challenge of this project is its architectural backbone: the simulation environment and the agents communicate exclusively via **Model Context Protocol (MCP)** servers. 

This guarantees complete logical isolation. The Cop cannot peek at the global game state; it must request its valid moves and receive partial observations just like a real-world entity. 

### Core Game Mechanics
- **Grid Size:** 5x5 Matrix.
- **The Cop:** 
  - Goal: Catch the Thief by moving onto the exact same cell.
  - Vision: Radius of 1 cell (can only see immediately adjacent cells).
  - Movement: 8-directional (Orthogonal and Diagonal).
  - Special Ability: Can **Place a Barrier**. Placing a barrier consumes a turn but permanently blocks a cell for the remainder of the simulation. Max 5 barriers.
- **The Thief:**
  - Goal: Evade the Cop and survive for exactly 25 turns. 
  - Vision: Radius of 2 cells (a massive strategic advantage).
  - Movement: 8-directional (Orthogonal and Diagonal).
- **Scoring System:**
  - Cop Wins: Cop +20 points, Thief -5 points.
  - Thief Wins: Thief +10 points, Cop -5 points.

This project implements a fascinating blend of LLM-driven reasoning (`gpt-4o-mini`), Reinforcement Learning (Q-Tables), and strict algorithmic pathfinding to create highly intelligent agents.

---

## 2. Why We Built Two Cops: The Evolution of Strategy

One of the most defining moments in the development of this project was the realization that **a perfectly deterministic Cop breeds a perfectly predictable game.** 

### Phase 1: The Quest for Perfection
Initially, our goal was to build the ultimate Cop. We needed an agent that mathematically removed the Thief's ability to escape. We designed **Cop 1 (The Deterministic 3-Barrier Sweep)**. It flawlessly drops barriers down the center of the map, trapping the Thief on one half, and then systematically sweeps the trapped zone. 

However, we ran into a massive problem. If the Cop always does the exact same thing, the Thief will eventually learn the exact sequence of moves to evade it. We needed to know if our Thief was *actually* smart, or if it was just memorizing the Cop's path.

### Phase 2: The Chaos Update
To robustly stress-test our Thief, we realized we needed a second, entirely different opponent. We built **Cop 2 (The Chaos Probabilistic Patroller)**. Cop 2 throws away the strict, predictable barrier line. Instead, it relies on probabilistic variance, wandering the map, dropping barriers dynamically, and instantly snapping into heat-seeking chase sequences when it spots the Thief.

By having **Two Cops**, we created a robust training environment. 
- **Cop 1** acts as our primary, unstoppable submission for the final match. 
- **Cop 2** acts as the unpredictable training dummy that ensures our Thief never gets stuck in hardcoded loops.

---

## 3. Deep Dive: Agent Strategies & Decision Making

The intelligence of the agents is distributed across specific Planner modules that define their strategic behaviors. 

### Cop 1: The Deterministic 3-Barrier Sweep
Cop 1 is the ultimate flawless hunter. It relies on a strictly deterministic pathfinding algorithm that systematically cuts the map in half.

**Algorithmic Breakdown:**
1. **The Wall:** The Cop navigates to column 2. It drops a barrier at `(0,2)`, moves down to `(1,2)`, drops a barrier, moves down to `(2,2)`, and drops a final barrier. 
2. **The Sweep:** The Cop then moves to the left or right half of the grid (the 3x3 trapped zones). It methodically steps through sweeping waypoints.

**The Mathematical Proof of 100% Win-Rate:**
Because the 5x5 grid is split at Column 2, the trapped zones are exactly 2x5.
The Cop runs a precise sweep pattern that visits `(0,0)`, `(2,1)`, and `(4,0)`. 
Since the Cop's legal vision radius is a Chebyshev distance of `1`, standing on `(2,1)` mathematically covers `(1,0)` through `(3,2)`. By executing this 3-point sweep, the maximum distance from the Cop to *any* cell in the trapped 2x5 zone never exceeds 1. 
Therefore, 100% of the half-grid is perfectly scanned, leaving 0 safe squares. The Thief mathematically cannot evade detection!

```mermaid
sequenceDiagram
    participant C as Cop 1
    participant G as Grid
    C->>G: Move to (0,2)
    C->>G: Action: place_barrier at (0,2)
    C->>G: Move to (1,2)
    C->>G: Action: place_barrier at (1,2)
    C->>G: Move to (2,2)
    C->>G: Action: place_barrier at (2,2)
    Note over C,G: The grid is now split! Cop systematically sweeps the 3x3 halves.
```

### Cop 2: The Chaos Probabilistic Patroller
A deterministic strategy is easily exploited if the opponent memorizes it. To counter this, **Cop 2** introduces extreme Chaos.

**Algorithmic Breakdown:**
1. **Probabilistic Barrier Placement:** On any given turn, if the Cop has barriers remaining, it rolls a pseudo-random number generator. It has exactly a `15% probability` of dropping a barrier dynamically on its current cell. 
2. **Random Waypoint Navigation:** Instead of sweeping a strict grid, the Cop randomly selects an unvisited corner or edge of the map and navigates toward it.
3. **The Snap Chase:** The moment the Thief enters the Cop's vision radius (Chebyshev distance <= 1), the Cop completely abandons its patrol route and instantly switches to a greedy heat-seeking algorithm, closing the distance on the exact coordinates of the Thief.

### The Thief: The Non-Deterministic Ghost
The Thief uses the highly advanced `CornerPlanner` strategy, turning it into an absolute ghost.

**Algorithmic Breakdown:**
1. **Constant Distance Calculation:** The Thief constantly calculates its exact Chebyshev distance from the Cop. 
2. **The 2-Step Rule:** It attempts to maintain exactly **2 steps of distance** at all times. This keeps the Thief safely outside the Cop's vision radius of 1, but close enough that the Thief's vision radius of 2 can still track the Cop's movements. 
3. **Non-Deterministic Evasion:** Early iterations of the Thief always moved `Up-Left` when chased from the `Down-Right`. Cops quickly exploited this. We upgraded the Thief to evaluate *all* mathematically optimal escape routes, group them into a list, and **randomly select one**. This non-deterministic evasion shatters the Cop's ability to trap the Thief in a predictable cornering loop!

---

## 4. System Architecture (The MCP Backbone)

To guarantee zero cheating and complete state isolation, the project uses the **Model Context Protocol (MCP)** standard developed by Anthropic. 

### Zero-Cheating Architecture
In a standard Python project, agents could simply import the global `GameState` and read `thief.row` and `thief.col`. We explicitly prevent this. 
- The Game Orchestrator runs in the main process.
- The `Cop MCP Server` and `Thief MCP Server` run as isolated subprocesses communicating entirely via JSON-RPC over `stdio`.
- Agents must send a `call_tool` request to the Orchestrator to ask "What do I see?" The Orchestrator applies their vision radius and returns a strictly filtered text string.

```mermaid
graph TD
    O[Game Orchestrator] -->|Sends Partial Observation String| CS(Cop MCP Server)
    O -->|Sends Partial Observation String| TS(Thief MCP Server)
    
    CS -->|Queries Belief State & Valid Moves| CP{Cop Planner}
    TS -->|Queries Belief State & Valid Moves| TP{Thief Planner}
    
    CP -->|JSON Action & Dialogue| O
    TP -->|JSON Action & Dialogue| O
    
    O -->|Executes Move Validator & State Updates| G[(Global Game Grid)]
    G -.-> O
```

### The TurnExecutor Flow
Every single turn is processed through a strict pipeline:
1. **Observation Generation:** The Orchestrator calculates the Euclidean distance between agents. If distance > vision radius, it returns `"No sign of the opponent."`
2. **Belief State Update:** If the Cop saw the Thief last turn but not this turn, the belief state updates to: `"Last saw opponent 1 step North, 1 turn ago."`
3. **LLM Generation:** The observation, valid moves, and belief state are formatted into a prompt and sent to `gpt-4o-mini`. 
4. **Action Override:** The LLM generates the dialogue, but the Action is overridden by our strict Python Planners (e.g., The 3-Barrier Sweep) to guarantee perfect strategic execution without LLM hallucinations.
5. **Move Application:** The `MoveValidator` checks for map boundaries and barriers, and applies the action to the grid.

---

## 5. The LLM Integration & Dynamic Dialogue

While the physical movements of the agents are driven by Python algorithms, the **personality and conversational dynamics** of the agents are driven entirely by `gpt-4o-mini`.

We implemented a sophisticated `PromptBuilder` that instructs the LLM to generate highly contextual, dramatic dialogue reacting directly to the game state.

**Example Cop Prompt Variables:**
- `Observation`: "You see the opponent 1 step South-East."
- `History`: ["T3: I moved down", "T4: I placed a barrier"]
- `Opponent Message`: "Catch me if you can, flatfoot!"

**The Output:**
Instead of generic phrases, the LLM parses the opponent's message and the grid state to generate responses like: *"You can run South-East all you want, but this barrier just cut off your escape!"*

This creates a deeply immersive, interactive simulation where the agents actually talk to each other while hunting.

---

## 6. Reinforcement Learning & Q-Tables

Running entirely in the background alongside the deterministic planners is a robust Q-Learning reinforcement architecture.

**State Encoding:**
We compress the 5x5 grid state into an integer. The state tracks the Cop's coordinates and the Thief's coordinates. 

**The Bellman Equation:**
After every move, the `TurnExecutor` calculates the reward and updates the Q-Table using the Bellman Equation:
`Q(s, a) = Q(s, a) + α * (R + γ * max_a' Q(s', a') - Q(s, a))`

**Reward Structure:**
- Cop catches Thief: `+10`
- Invalid Move (hitting a wall/barrier): `-1`
- Standard Move: `-0.1` (encourages catching the Thief faster)

Over thousands of episodes, the Q-Table maps the optimal policies for closing distance on the grid.

---

## 7. The Autonomous Simulation Pipeline

Generating data for these agents requires massive, repetitive simulations. Running games manually would be impossible. We built an autonomous `pipeline.py` script to handle the entire lifecycle.

**The Pipeline Lifecycle:**
1. **Configuration Swap:** It dynamically opens `config/config.json` and toggles between Cop 1 (`use_sweep_cop: False`) and Cop 2 (`use_sweep_cop: True`).
2. **Subprocess Management:** It spawns the MCP servers, binds them to ports, and ensures they don't deadlock.
3. **Execution Loop:** It plays **12 full games** (6 games for Cop 1 vs Thief, and 6 games for Cop 2 vs Thief).
4. **Financial Tracking:** It integrates with `cost_tracker.py` to count the exact number of prompt and completion tokens used by `gpt-4o-mini`, multiplying them by OpenAI's pricing API to generate a final `cost_report.json` detailing exactly how many fractions of a cent the run cost.
5. **Artifact Generation:** It saves out the massive `transcript.jsonl` and the rich HTML Replays.

---

## 8. Analytics, Metrics, & Learning Curves

The system tracks every metric of the simulation and generates massive data visualizations using Matplotlib and Seaborn.

### Q-Learning Convergence
The reinforcement learning metrics show the Cop slowly converging on optimal states over thousands of episodes. The rolling average of rewards trends heavily upwards as the Cop learns the map geometry.
![Learning Curve](assets/learning_curve.png)

### Strategy Heatmap
By tracking hyperparameter tuning, we can analyze the success rates of various grid states. The heatmap displays the direct correlation between the Cop's Vision Radius and the maximum allowable barriers, proving that increasing barriers exponentially increases the Cop's win-rate even with low vision.
![Hyperparameter Heatmap](assets/hyperparameter_heatmap.png)

### Win-Rate Comparison
A bar chart breakdown of Cop 1 vs Cop 2 win-rates against the Non-Deterministic Ghost Thief. This graph proves the thesis of our project: the deterministic Wall-Builder (Cop 1) is a fundamentally different class of threat compared to the Chaos Patroller (Cop 2).
![Strategy Comparison](assets/strategy_comparison.png)

---

## 9. Cinematic HTML Replays & User Interface

Reading terminal output is incredibly difficult when debugging 25-turn multi-agent games. To solve this, we built a custom HTML/CSS rendering engine in `html_replay.py`.

Every time the pipeline finishes, it outputs a highly stylized, cinematic HTML replay file allowing you to scrub back and forth through the turns visually!

**Features of the UI:**
- Interactive timeline scrubber to jump instantly to Turn 14.
- CSS-rendered 5x5 grid with distinct sprites for the Cop (Police Car) and Thief (Masked Robber).
- Visual barrier blocks rendering dynamically on the DOM.
- A dedicated Dialogue Box that renders the LLM-generated quips like a comic book.

*(A video demonstration of the UI dashboard will be provided upon the final submission run).*

---

## 10. Setup & Installation Instructions

Want to run the Dual-AI Agent Race yourself? It's incredibly easy to deploy.

### Prerequisites
- Python 3.10 or higher.
- `uv` package manager installed on your system.
- An active OpenAI API key.

### Step-by-Step Instructions

1. **Clone and Install Dependencies:**
   Navigate to the project root and use `uv` to sync the virtual environment:
   ```bash
   uv sync
   ```

2. **Set your OpenAI API Key:**
   The agents require access to `gpt-4o-mini` for dialogue generation.
   ```bash
   export OPENAI_API_KEY="your-sk-key-here"
   ```

3. **Run the Complete Autonomous Pipeline:**
   This script will handle everything. It swaps the configs, boots the MCP servers, plays 12 full games, tracks token costs, and saves the replays. (Note: This takes roughly 10 minutes to complete due to the high volume of LLM requests).
   ```bash
   uv run python pipeline.py
   ```

4. **Watch the Cinematic Replays:**
   Once the pipeline finishes, the `results/` folder will be populated. Open the HTML files directly in your web browser to watch the race unfold!
   ```bash
   open results/replay_cop1.html
   ```

---
<div align="center">
  <i>Built from scratch for the Advanced Agentic AI Course.</i>
  <br>
  <i>May the best AI win.</i>
</div>
