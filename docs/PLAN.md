# Architecture and Implementation Plan (PLAN)

## 1. Component Diagram

```mermaid
graph TD;
    subgraph "Orchestrator Node"
        O[Orchestrator<br/>(Game Loop)]
        GE[Game Engine<br/>(Grid & Rules)]
        LLM[LLM Client<br/>(Anthropic API)]
        
        O -->|Manages State| GE
        O -->|Queries Prompts| LLM
    end

    subgraph "Cop Server (Port 8001)"
        CS[Cop MCP Server<br/>(Exposes Tools)]
    end

    subgraph "Thief Server (Port 8002)"
        TS[Thief MCP Server<br/>(Exposes Tools)]
    end

    O -->|Action/Observation via MCP| CS
    O -->|Action/Observation via MCP| TS
    CS -.->|Returns Tool Data| O
    TS -.->|Returns Tool Data| O
```

**Note:** The LLM client lives strictly *inside* the Orchestrator. The MCP servers are lightweight and only expose tool capabilities (actions and state observations). 

## 2. SDK Single Entry Point Design
To ensure all business logic is clean and accessible via a single interface, we use an SDK layer pattern.
- The `src/cop_thief/sdk/sdk.py` acts as the single unified facade.
- External entry points (`main.py`, testing frameworks, CLI) interact only with the `CopThiefSDK` class.
- The SDK routes calls to the underlying `GameEngine`, `Orchestrator`, `ConfigLoader`, and `GmailReporter`.

## 3. The 8 Development Phases
1. **Phase 0:** Repo & tooling setup (Completed)
2. **Phase 1:** Documentation & Config implementation (Current)
3. **Phase 2:** Config Loader + Security (Secrets management, strictly no hardcoding)
4. **Phase 3:** Core Game Engine (5x5 grid, movement validation, limits, barrier logic, and score tracking)
5. **Phase 4:** Strategy Module (Manhattan Heuristic baseline, transitioning to Tabular Q-Learning)
6. **Phase 5:** LLM Client + MCP Servers (Anthropic client, robust local API Gatekeeper, Cop and Thief MCP servers)
7. **Phase 6:** Orchestrator + Game Runner (Coordinating the 6 sub-games, mapping tools, prompt routing)
8. **Phase 7:** Gmail Reporter + JSON Output (Auto-emailing structured JSON payload at game completion)
9. **Phase 8:** Research, Analysis, Final Polish (Jupyter Notebooks, visual graphs, 85% coverage verify, ruff enforce)

## 4. Key Architectural Decisions & Rationale
- **Decoupled LLM Logic**: The LLM queries are processed by the orchestrator rather than within the MCP servers. This ensures the MCP servers remain stateless execution nodes, drastically improving testability and adhering to best security practices.
- **Config-Driven Operations**: Every constant (scores, sizes, ports, tokens, limits) is fetched from `config.json`. This completely eliminates hardcoding and ensures zero friction when hyperparameters change.
- **Strict Size/Lint Rules**: Keeping files ≤ 150 lines forces extreme modularity and strict Single Responsibility Principle (SRP). `ruff` prevents anti-patterns before they commit.
