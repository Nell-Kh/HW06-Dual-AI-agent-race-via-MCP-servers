# HW06 — Dual AI Agent Race via MCP Servers

This project features a competitive simulation where two autonomous AI agents (the Cop and the Thief) maneuver on a 5×5 grid and communicate in natural language via independent Model Context Protocol (MCP) servers. The architecture leverages OpenAI's gpt-4o-mini for natural dialogue, implements partial observation mechanics within a Dec-POMDP framework, trains the Thief via Q-table Reinforcement Learning prior to execution, and automatically emails a comprehensive JSON report to the lecturer upon completion.

## Installation

**Requirements:** Python 3.10+, `uv`.

**Steps:**
1. Clone the repository.
2. Install dependencies with `uv sync`.
3. Create a `.env` file in the root directory containing the following credentials:
   - `OPENAI_API_KEY`
   - `GMAIL_SENDER`
   - `GMAIL_APP_PASSWORD`

## How to Run

```bash
uv run python main.py
```

## Formal Model: Dec-POMDP

The system is modeled as a Decentralized Partially Observable Markov Decision Process (Dec-POMDP) represented by the tuple ⟨n, S, {Aᵢ}, P, R, {Ωᵢ}, O, γ⟩:
- **n**: The number of agents (2: Cop and Thief).
- **S**: The state space (grid coordinates and barrier locations).
- **{Aᵢ}**: The action space for each agent (up, down, left, right, diagonals, or place_barrier).
- **P**: The transition probability function (deterministic movement and barrier placement).
- **R**: The global reward function (+10 for capture, distance-based sub-rewards).
- **{Ωᵢ}**: The individual observation spaces (local grid visibility).
- **O**: The observation function dictating what each agent perceives.
- **γ**: The discount factor (0.9) prioritizing immediate rewards.

**Belief Tracking**: Agents manage their partial observations by applying a last-seen decay model: fresh sightings (≤2 turns) are reliable, aging sightings (3-4 turns) are approximate, and stale sightings (≥5 turns) are unreliable.

## Agent Strategies

- **Cop**: Executes a deterministic sweep and barrier-wall routine starting at `(0,2)`. The Cop drops 3 barriers down column 2 to split the board, sweeps the middle block with its 3×3 vision (radius 1), and immediately pounces on the Thief upon sight.
- **Thief**: Utilizes a corner-flee strategy, retreating to the farthest corner from the center of the board and safely hunkering down. 
- *Note: Both agents use OpenAI's gpt-4o-mini solely to generate dynamic natural language dialogue based on their actions.*

## Asymmetric Vision

- **Cop Vision**: Radius 1 (sees a 3×3 area).
- **Thief Vision**: Radius 2 (sees a 5×5 area).
- **Rationale**: This grants the evader an information advantage. The Thief can spot the Cop approaching and react defensively, forcing the Cop to rely on an organized, systematic sweep rather than simple pursuit.

## Q-Table Reinforcement Learning

Before the main simulation, the engine runs 500 headless training episodes. To provide a realistic but beatable training opponent, the Cop acts as a 50/50 epsilon-random agent (50% Manhattan heuristic pursuit, 50% random action). The Thief is trained using a Bellman update governed by:
- `learning_rate` = 0.1
- `discount_factor` = 0.9
- `epsilon` = 0.2 (with linear decay)

## Results

Despite the Thief's Q-table training and vision advantage, the Cop's sweeping wall strategy wins consistently (final scores averaged **120 - 30** across the 6 sub-games). 
- The training progress is saved as a plot in `assets/learning_curve.png`.
- A full interactive HTML game replay is generated at `results/replay.html`.

## Project Structure

- `main.py`: Entry point for the simulation.
- `src/cop_thief/sdk/`: MCP SDK and core abstractions.
- `src/cop_thief/services/`: Game logic, RL, planners, observers, and LLM clients.
- `src/cop_thief/shared/`: Configuration loaders and utilities.
- `config/config.json`: Master configuration file.
- `docs/`: Technical specifications, PRD, and planning documents.
- `notebooks/`: Data analysis notebooks (`analysis.ipynb`).
- `assets/`: Result artifacts like `learning_curve.png`.
