# SentryAgent AI — Autonomous Debugging Agent
**Autonomous Self-Healing Pipeline for Production Python Applications**


## Overview

SentryAgent AI is a prototype autonomous debugging system designed to detect runtime errors in Python applications, analyze failures, and generate validated code fixes using an LLM.

The system implements a **closed-loop self-healing workflow**:

**Execute → Detect → Analyze → Fix → Validate → Restore**

Unlike simple AI-assisted coding tools, SentryAgent focuses on **controlled and verifiable code repair**, ensuring that generated fixes are tested and safe before being applied.
SentryAgent AI transforms debugging from a *reactive, manual process* into an *autonomous, self-correcting system*.

When your application crashes:

```
┌─────────────────────────────────────────────────────────┐
│  1. DETECT                                              │
│  Real-time error captured from stderr/stdout            │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  2. ANALYZE                                             │
│  AST parsing extracts: file, line, function, error type │
│  Memory store checks for similar past failures          │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  3. CONTEXT GATHER                                      │
│  Collects related modules, imports, test files          │
│  Builds full execution context for AI reasoning         │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  4. FIX GENERATION                                      │
│  GPT-4o synthesizes fix based on error + rules + tests  │
│  Syntax validation via AST                              │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  5. BACKUP & APPLY                                      │
│  Original code backed up, fix applied to source         │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  6. VALIDATE & ROLLBACK                                 │
│  Pytest suite runs; if pass → SUCCESS                   │
│  If fail → backup restored automatically                │
└─────────────────────────────────────────────────────────┘
```

**Result:** Incidents resolved in **seconds to minutes**, with full auditability and rollback protection.

---

## Key Features

### 🧠 Intelligent Crash Analysis
- **Dynamic traceback parsing** using regex + AST to extract file, line number, function name, and exception type
- **Context enrichment** pulls related modules and local dependencies
- **Memory-aware detection** queries fix history to avoid repeated failed approaches

### 🔧 AI-Powered Code Synthesis
- **GPT-4o integration** with enterprise rule enforcement (no hardcoded values, preserve existing functions, etc.)
- **Deterministic generation** via structured prompts and validation gates
- **Syntax validation** ensures generated code parses before any file write

### 🛡️ Safety & Rollback
- **Atomic backup-restore pattern** creates `.bak` before each attempt
- **Symbol preservation checks** via AST confirm no critical functions/classes are deleted
- **Pytest integration** validates fixes against test suite before committing

### 📝 Memory & Learning
- **JSON-based fix memory** stores every attempt: error type, fix strategy, test results
- **Pattern matching** retrieves similar past failures to guide future fixes
- **Audit trail** enables root cause analysis and team learning

### 🎛️ Enterprise Dashboard
- **Streamlit-based command center** with real-time fix monitoring
- **Log streaming** shows agent decision-making process
- **Manual override** allows human intervention at any step
- **One-click execution** for rapid incident response

---

## System Architecture

The system is built on a modular, layered architecture designed for stability, safety, and rapid recovery:

* **Execution Layer (subprocess):** Responsibly spawns and monitors the target application within a controlled environment, capturing all stdout and stderr streams for real-time error detection.

* **Analysis Layer (Regex & AST):** Performs dynamic traceback parsing to isolate the exact crash location (file, line, function) and exception type.

* **AI Reasoning Layer (GPT-4o):** Acts as the "Self-Healing Engine," synthesizing code patches guided by a strict set of behavioral rules and system constraints.

* **Context Layer (context_builder.py):** Automatically resolves local imports and dependency chains, providing the LLM with a comprehensive view of the surrounding code environment.

* **Validation Layer (Pytest & AST):** A multi-stage gatekeeper that performs syntax checks and runs automated test suites to ensure the fix is functionally correct before deployment.

* **Safety Layer (Atomic Backup/Restore):** Protects the production codebase by creating .bak snapshots and performing automatic rollbacks if any validation stage fails.

* **Memory Layer (JSON-based Store):** Maintains a persistent history of failures and repair strategies, enabling pattern matching to avoid redundant or ineffective fix attempts.


<img width="5000" height="7000" alt="System Sequence Diagram" src="https://github.com/user-attachments/assets/917188bc-5da8-4d5c-9919-f148679db1ea" />
Click on the image for full size

---

## How It Works

1. The agent runs the target Python file
2. If a crash or failure occurs, it extracts the error context
3. Relevant code and history are collected
4. A structured prompt is sent to the LLM
5. The model generates a proposed fix
6. The fix is validated using tests
7. If tests pass → fix is accepted
8. If tests fail → rollback and retry


<img width="4000" height="300" width="1000" alt="Statistical Test Selection-2026-04-17-170623" src="https://github.com/user-attachments/assets/ff1d8351-75ee-46cb-9b11-cce21733ba89" />
Click on the image for full size

---

## Streamlit Dashboard
The SentryAgent AI includes a high-level command center built with Streamlit, designed for real-time monitoring and manual intervention:

* **Live Incident Monitoring:** View active crashes, tracebacks, and AI-generated fix candidates in a clean, professional UI.

* **One-Click Repair:** Manually trigger the self-healing cycle or apply recommended fixes with a single button.

* **Integrated Log Streaming:** Access the chronological history of system errors and agent decisions without leaving the dashboard.

* **Fix Analytics:** Review historical data from fix_memory.json to analyze recovery success rates and recurring patterns.

* **Mentor Mode (Guardian Logic):** A specialized mode designed to prevent accidental production changes and support junior developers. In this mode, the agent acts as a "Senior Reviewer" explaining its reasoning before any code is applied and requiring explicit human sign-off for critical symbols.


Dashboard Overview: <img width="1699" height="837" alt="Dashboard_1" src="https://github.com/user-attachments/assets/bbceb66d-8b85-4c4a-8e66-066a39687ed9" />

<img width="1629" height="912" alt="Dashboard_2" src="https://github.com/user-attachments/assets/d3323c4f-76a4-48e2-a7cc-3f0893d1beb0" />

## Example Scenario

### Input (Buggy Code)

```python
def calculate_total_price(prices):
    total = 0
    for price in prices:
        total += price    # Fails when price is a string
    return total

orders = [10.5, 20.0, "oops", 5.0]
print(f"Total price: {calculate_total_price(orders)}")
```

### Problem

Mixed data types cause a runtime error:

```
TypeError: unsupported operand type(s)
``` 

### Expected Behavior (Defined Policy)

* Sum only numeric values
* Ignore invalid types (e.g., strings, None)
* Return 0 if no valid numbers exist

### Agent Detects
```
💥 Crash Detected: TypeError: unsupported operand type(s) for +: 'int' and 'str'
📂 Target file: app.py
📍 Line 5, function: calculate_total_price
🧠 Looking for similar past failures...
```

### Agent Generates Fix
```python
def calculate_total_price(prices):
    total = 0
    for price in prices:
        if isinstance(price, (int, float)):
            total += price
    return total

orders = [10.5, 20.0, "oops", 5.0]
print(f"Total price: {calculate_total_price(orders)}")
```

---

## Project Structure

```
.
├── app.py                 # Buggy version for demonstration
├── test_app.py            # Tests for correct behavior
├── main.py                # Core autonomous agent logic
├── agent_tools.py         # Utilities (execution, validation, logging)
├── memory_store.py        # Fix attempt memory system
├── context_builder.py     # Collects related files for context
├── dashboard.py           # Streamlit UI
├── rules.json             # Coding rules for LLM
├── agent_config.json      # Runtime configuration
├── fix_memory.json        # Logged fix attempts
└── error_log.txt          # Error history
```

---

## Installation & Setup

```bash

pip install -r requirements.txt
```

Create a `.env` file:

```
API_KEY=your_api_key
```

---

## Usage

### Run the agent (CLI)

```bash
python main.py
```

### Run the dashboard

```bash
streamlit run dashboard.py
```

### Run tests

```bash
pytest test_app.py -v
```

---

## Design Decisions

### Why Test-Based Validation?

LLM-generated fixes are not trusted blindly.
Every fix must pass tests to be accepted.

---

### Why Rollback?

To ensure system safety, failed fixes are reverted automatically.

---

### Why Memory?

Previous failures are stored and reused to improve future debugging attempts.

---

### Why Minimal Fix Strategy?

The agent is instructed to:

* preserve structure
* avoid rewriting working logic
* apply the smallest safe change

---

## Limitations

* Designed for controlled debugging scenarios (not full production systems)
* Focused on Python code
* Relies on quality of tests for validation
* LLM may require multiple attempts to converge

---

## Future Improvements

* Unify CLI and dashboard into a shared engine
* Improve validation beyond syntax and tests
* Support additional error types (KeyError, IndexError, etc.)
* Expand multi-file reasoning capabilities
* Add semantic diff visualization
* Predictive failure prevention: Integration with logs to predict and fix potential crashes before they occur in production.

---

## Author

Nikol
B.A. Information Systems Management
Specialization: Data Analysis & AI Systems

---

## License

SentryAgent AI is released under the **MIT License**

---

## Summary

SentryAgent AI demonstrates how AI agents can move beyond suggestion-based tools into **autonomous, test-validated, and safety-aware systems**.

It highlights:

* Agentic workflows
* AI-driven debugging
* System design thinking
* Practical use of LLMs in engineering environments
