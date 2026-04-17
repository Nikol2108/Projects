# SentryAgent AI — Autonomous Debugging Agent

## Overview

Dashboard Overview: <img width="1699" height="837" alt="Dashboard_1" src="https://github.com/user-attachments/assets/bbceb66d-8b85-4c4a-8e66-066a39687ed9" />

<img width="1629" height="912" alt="Dashboard_2" src="https://github.com/user-attachments/assets/d3323c4f-76a4-48e2-a7cc-3f0893d1beb0" />


SentryAgent AI is a prototype autonomous debugging system designed to detect runtime errors in Python applications, analyze failures, and generate validated code fixes using an LLM.

The system implements a **closed-loop self-healing workflow**:

**Execute → Detect → Analyze → Fix → Validate → Restore**

Unlike simple AI-assisted coding tools, SentryAgent focuses on **controlled and verifiable code repair**, ensuring that generated fixes are tested and safe before being applied.

---

## Key Features

* **Automatic Error Detection**
  Runs a Python application and captures runtime failures and crashes.

* **LLM-Based Code Repair**
  Uses an AI model to analyze errors and propose targeted fixes.

* **Test-Driven Validation**
  Every generated fix is validated against predefined tests.

* **Self-Healing Loop**
  Retries fixes automatically until tests pass or attempts are exhausted.

* **Safe Rollback Mechanism**
  Automatically restores the original code if a fix fails.

* **Fix Memory System**
  Logs previous attempts and failures for future context.

* **Context-Aware Debugging**
  Includes related files and historical failures to improve fix quality.

* **Interactive Dashboard (Streamlit)**
  Visual interface for monitoring execution, errors, and fixes.

---

## System Architecture


The system follows a modular architecture:

* **Execution Layer**
  Runs the target Python file and captures output/errors

* **Analysis Layer**
  Extracts crash context (file, line, exception type)

* **AI Reasoning Layer**
  Generates fixes using LLM with strict behavioral rules

* **Validation Layer**
  Verifies fixes using automated tests

* **Safety Layer**
  Backup & restore mechanism to prevent unsafe changes

* **Memory Layer**
  Stores previous attempts and failure patterns


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

## Example Scenario

### Input (Buggy Code)

```python
def calculate_total_price(prices):
    total = 0
    for price in prices:
        total += price
    return total
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

### Output (Fixed Code)

```python
if isinstance(price, (int, float)):
    total += price
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

---

## Author

Nikol
B.A. Information Systems Management
Specialization: Data Analysis & AI Systems

---

## Summary

SentryAgent AI demonstrates how AI agents can move beyond suggestion-based tools into **autonomous, test-validated, and safety-aware systems**.

It highlights:

* Agentic workflows
* AI-driven debugging
* System design thinking
* Practical use of LLMs in engineering environments
