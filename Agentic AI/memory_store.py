import json
from pathlib import Path
from datetime import datetime

# File where we store the memory
MEMORY_PATH = Path("fix_memory.json")


def load_memory() -> list[dict]:
    """
    Load all memory entries from the file.
    If the file does not exist – return an empty list.
    """
    if not MEMORY_PATH.exists():
        return []

    try:
        with open(MEMORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_memory(entries: list[dict]) -> None:
    """
    Save all memory entries into the JSON file.
    """
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def append_memory(entry: dict) -> None:
    """
    Add a new fix attempt to memory.
    """
    memory = load_memory()
    memory.append(entry)
    save_memory(memory)


def build_memory_entry(
    error_type: str,
    error_message: str,
    target_file: str,
    attempt: int,
    fix_summary: str,
    tests_passed: bool,
    validation_issues: list[str] | None = None,
) -> dict:
    """
    Create a structured memory entry.
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "error_type": error_type,
        "error_message": error_message,
        "target_file": target_file,
        "attempt": attempt,
        "fix_summary": fix_summary,
        "tests_passed": tests_passed,
        "validation_issues": validation_issues or [],
    }


def get_similar_failures(error_type: str, target_file: str, limit: int = 3) -> list[dict]:
    """
    Find similar past failures from memory.
    """
    memory = load_memory()

    matches = [
        item for item in memory
        if item.get("error_type") == error_type
        or item.get("target_file") == target_file
    ]

    return matches[-limit:]