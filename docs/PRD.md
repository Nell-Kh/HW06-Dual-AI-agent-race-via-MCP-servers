# Product Requirements Document (PRD)

## 1. Project Overview and the Pursuit Problem
This project implements a multi-agent Cop-and-Thief pursuit game where two autonomous AI agents communicate in natural language over independent MCP servers. The Cop attempts to catch the Thief on a dynamic 5x5 grid by deducing locations and placing barriers, while the Thief attempts to evade the Cop for a maximum of 25 moves. The system requires orchestrating these interactions locally using Anthropic's Claude as the underlying LLM, establishing a Dec-POMDP (Decentralized Partially Observable Markov Decision Process) environment where agents rely on partial observations.

## 2. Full Dec-POMDP Tuple
The pursuit problem is framed as a Dec-POMDP, defined by the tuple `⟨n, S, {Ai}, P, R, {Ωi}, O, γ⟩`:
- **n**: The number of agents (2: Cop and Thief).
- **S**: The state space (locations of both agents and up to 5 barriers on the 5x5 grid).
- **{Ai}**: The set of actions available to each agent (movement in orthogonal/diagonal directions, and barrier placement for the Cop).
- **P**: The state transition function (how the grid updates after each action).
- **R**: The reward function (points awarded according to `config.json` scoring rules based on win/loss states).
- **{Ωi}**: The partial observation space for each agent (local visibility and natural language messages from the opponent).
- **O**: The observation function (translating grid state and opponent actions into the prompt/natural language context for the agent).
- **γ**: The discount factor (used exclusively for the Q-Table Bellman update, not the overall game scoring).

## 3. Functional Requirements
- **Game Engine**: A robust 5x5 grid simulation that tracks entity positions, validates moves (barriers, bounds), and strictly enforces the 25-move limit and 6 sub-game limit.
- **MCP Servers**: Two independent MCP servers running locally on ports 8001 (Cop) and 8002 (Thief). They must expose tools to read state and execute actions, but not host the LLM themselves.
- **LLM Integration**: Integration with Anthropic's Cloud API to generate natural language communications and strategic decisions. Keys must be loaded from `.env` only.
- **Strategy Module**: Implementation of a baseline Manhattan Heuristic and an advanced Q-Table algorithm (updating via Bellman equation).
- **Gmail Reporter**: Automated sending of a structured JSON report (game statistics and metadata) to `rmisegal+uoh26b@gmail.com` at the conclusion of the 6 sub-games.

## 4. Non-Functional Requirements
- **Local Execution**: All components (except the Cloud LLM API) must run strictly on `localhost` without external services like Prefect or ngrok.
- **Package Management**: Exclusive use of `uv` for dependency management and environment creation.
- **Code Quality**: Strict enforcement of `ruff` with 0 errors. All files must be ≤ 150 lines (excluding blanks and comments).
- **Testing**: Minimum 85% test coverage enforced using `pytest --cov`. TDD should be utilized.

## 5. Scoring Rules
Scores are exclusively driven by `config.json` values and accumulated across the 6 sub-games:
- **Cop Win (Thief caught)**: Cop receives 20 points; Thief receives 5 points.
- **Thief Win (25 moves survived)**: Thief receives 10 points; Cop receives 5 points.

## 6. Acceptance Criteria & Definition of Done
- **Definition of Done (DoD)**: A task is done when the code is fully implemented, unit and integration tests pass with ≥ 85% coverage, the file passes `ruff check` with 0 errors, the file is under 150 lines, and all configurations are dynamically loaded from `config.json`.
- **Acceptance Criteria**:
  - The orchestrator successfully runs 6 consecutive sub-games without manual intervention.
  - Agents communicate naturally via prompts routed through the MCP servers on 8001 and 8002.
  - Q-Learning updates execute correctly using the configured learning rate and discount factor.
  - A formatted JSON email report is dispatched seamlessly at the end.

## 7. Out of Scope
- No cloud deployment or hosting for the game engine or servers.
- No inter-group bonus games (single pairing: our Cop vs. our Thief only).
- No role swapping during the 6 sub-games.
