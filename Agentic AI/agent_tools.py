"""
agent_tools.py — SentryAgent AI Backend Utilities
Handles file I/O, subprocess execution, error log management,
and test running for the autonomous self-healing pipeline.
"""

import sys
import subprocess
import datetime
import re
import ast
from pathlib import Path

# ─── Constants ────────────────────────────────────────────────────────────────

ERROR_LOG_PATH = Path("error_log.txt")
APP_PATH = Path("app.py")
TEST_PATH = Path("test_app.py")


# ─── File I/O ─────────────────────────────────────────────────────────────────

def read_file(filepath: str | Path) -> str:
    """Read a file safely, returning empty string if it doesn't exist."""
    path = Path(filepath)
    if not path.exists():
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(filepath: str | Path, content: str) -> None:
    """Write content to a file, creating parent directories if needed."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def append_file(filepath: str | Path, content: str) -> None:
    """Append a timestamped log entry to a file, preserving full history."""
    path = Path(filepath)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    separator = "═" * 60
    header = f"\n\n{separator}\n  LOG ENTRY  ·  {timestamp}\n{separator}\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(header + content.strip() + "\n")


def backup_file(filepath: str | Path) -> Path | None:
    """Create a backup copy of a file and return the backup path."""
    path = Path(filepath)
    if not path.exists():
        return None

    backup_path = path.with_suffix(path.suffix + ".bak")
    content = read_file(path)
    write_file(backup_path, content)
    return backup_path


def restore_backup(filepath: str | Path) -> bool:
    """Restore a file from its .bak backup if it exists."""
    path = Path(filepath)
    backup_path = path.with_suffix(path.suffix + ".bak")

    if not backup_path.exists():
        return False

    backup_content = read_file(backup_path)
    write_file(path, backup_content)
    return True


# ─── Error Log ────────────────────────────────────────────────────────────────

def get_error_log() -> str:
    """Return full contents of the error log."""
    return read_file(ERROR_LOG_PATH)


def count_log_entries() -> int:
    """Count how many distinct crash entries exist in the error log."""
    content = read_file(ERROR_LOG_PATH)
    return content.count("LOG ENTRY")


def get_last_log_entry() -> str:
    """Extract only the most recent log entry."""
    content = read_file(ERROR_LOG_PATH)
    if not content.strip():
        return ""
    parts = content.split("═" * 60)
    entries = [p.strip() for p in parts if p.strip()]
    return entries[-1] if entries else content


# ─── App Execution ────────────────────────────────────────────────────────────

def run_app(app_path: str | Path = APP_PATH) -> tuple[bool, str]:
    """
    Execute the given Python file using the current interpreter.
    Returns (has_error: bool, output_or_error: str).
    """
    path = Path(app_path)

    try:
        result = subprocess.run(
            [sys.executable, str(path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        error_output = f"TimeoutExpired: execution of {path.name} exceeded 30 seconds"
        append_file(ERROR_LOG_PATH, error_output)
        return True, error_output
    except Exception as e:
        error_output = f"Error running {path.name}: {e}"
        append_file(ERROR_LOG_PATH, error_output)
        return True, error_output

    if result.returncode != 0:
        error_output = result.stderr or result.stdout or "Unknown error (non-zero exit)"
        append_file(ERROR_LOG_PATH, error_output)
        return True, error_output

    return False, result.stdout or "App ran successfully with no output."


# ─── Test Runner ──────────────────────────────────────────────────────────────

def infer_test_path(target_file: str | Path) -> Path:
    """
    Infer a pytest filename from a target source file.
    Example:
      app.py -> test_app.py
      pricing.py -> test_pricing.py
    """
    path = Path(target_file)
    return path.with_name(f"test_{path.stem}.py")


def run_tests(test_path: str | Path) -> tuple[bool, str]:
    """
    Run pytest on the given test file using the current Python interpreter.
    Returns (passed: bool, output: str).
    """
    path = Path(test_path)

    if not path.exists():
        return False, f"❌ {path.name} not found. Run the agent first."

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(path), "-v", "--tb=short", "--no-header"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        passed = result.returncode == 0
        full_output = (result.stdout + "\n" + result.stderr).strip()
        return passed, full_output
    except subprocess.TimeoutExpired:
        return False, f"❌ Test suite {path.name} timed out after 60 seconds."
    except Exception as e:
        return False, f"❌ Error running tests for {path.name}: {e}"


# ─── Traceback Analysis ───────────────────────────────────────────────────────

def extract_crash_context(error_text: str) -> dict:
    """
    Dynamically parse a Python traceback to extract:
      - file: the crashing source file name
      - line_number: the line that caused the crash
      - function: the function that raised the error
      - error_type: exception class (e.g. KeyError, TypeError)
      - error_message: the human-readable exception message

    Returns a dict with these keys (all may be None if parsing fails).
    """
    context = {
        "file": None,
        "line_number": None,
        "function": None,
        "error_type": None,
        "error_message": None,
    }

    file_matches = re.findall(r'File "([^"]+)", line (\d+), in (\S+)', error_text)
    if file_matches:
        last_file, last_line, last_func = file_matches[-1]
        context["file"] = last_file
        context["line_number"] = int(last_line)
        context["function"] = last_func

    exception_match = re.search(
        r'^(\w+(?:\.\w+)*Error|\w+Exception|\w+Error): (.+)$',
        error_text,
        re.MULTILINE
    )
    if exception_match:
        context["error_type"] = exception_match.group(1)
        context["error_message"] = exception_match.group(2).strip()

    return context


def parse_ai_response(full_text: str) -> tuple[str, str]:
    """
    Robustly split an AI response into (explanation, code).
    Handles cases where the AI omits the CODE:/EXPLANATION: tags.
    Strips markdown fences and trailing AI commentary.
    """
    FORBIDDEN_PREFIXES = (
        "In this", "Ensure", "Note:", "Here is", "I have",
        "This solution", "This code", "Please ", "The above",
    )

    if "CODE:" in full_text:
        explanation = full_text.split("CODE:")[0].replace("EXPLANATION:", "").strip()
        raw_code = full_text.split("CODE:")[1].strip()
    elif "```python" in full_text:
        explanation = full_text.split("```python")[0].strip() or "Automated fix generated."
        raw_code = full_text.split("```python")[1].split("```")[0].strip()
    else:
        explanation = "Automated fix generated."
        raw_code = full_text

    clean_code = raw_code.replace("```python", "").replace("```", "").strip()

    lines = clean_code.splitlines()
    filtered_lines = [
        line for line in lines
        if not any(line.strip().startswith(p) for p in FORBIDDEN_PREFIXES)
    ]

    return explanation, "\n".join(filtered_lines).strip()


# ─── Validation ───────────────────────────────────────────────────────

def validate_python_syntax(code: str) -> tuple[bool, str]:
    """
    Validate that generated code is syntactically correct Python.
    Returns (is_valid, message).
    """
    try:
        ast.parse(code)
        return True, "Syntax is valid."
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"


def extract_top_level_definitions(code: str) -> dict[str, set[str]]:
    """
    Extract top-level function names, class names, and imports from code.
    """
    tree = ast.parse(code)

    functions = set()
    classes = set()
    imports = set()

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            functions.add(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.add(node.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports.add(module)

    return {
        "functions": functions,
        "classes": classes,
        "imports": imports,
    }


def validate_required_symbols(original_code: str, new_code: str) -> tuple[bool, str]:
    """
    Ensure important top-level symbols from the original code still exist.
    Prevents the model from deleting core functions/classes.
    """
    try:
        original_defs = extract_top_level_definitions(original_code)
        new_defs = extract_top_level_definitions(new_code)
    except Exception as e:
        return False, f"Definition extraction failed: {e}"

    missing_functions = original_defs["functions"] - new_defs["functions"]
    missing_classes = original_defs["classes"] - new_defs["classes"]

    if missing_functions or missing_classes:
        return (
            False,
            f"Missing symbols detected. "
            f"Functions: {sorted(missing_functions)} | Classes: {sorted(missing_classes)}"
        )

    return True, "Required symbols preserved."


def validate_fix_candidate(original_code: str, new_code: str) -> tuple[bool, list[str]]:
    """
    Combined validation gate for generated fixes.
    """
    issues = []

    syntax_ok, syntax_msg = validate_python_syntax(new_code)
    if not syntax_ok:
        issues.append(syntax_msg)

    symbols_ok, symbols_msg = validate_required_symbols(original_code, new_code)
    if not symbols_ok:
        issues.append(symbols_msg)

    if not new_code.strip():
        issues.append("Generated code is empty.")

    return len(issues) == 0, issues