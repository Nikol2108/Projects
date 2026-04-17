import os
import sys
import subprocess
import json
from openai import OpenAI
from dotenv import load_dotenv
from agent_tools import (
    infer_test_path,
    read_file,
    write_file,
    run_tests,
    extract_crash_context,
    backup_file,
    restore_backup,
    validate_fix_candidate,
)
from memory_store import (
    append_memory,
    build_memory_entry,
    get_similar_failures,
)
from context_builder import collect_related_files


# --- Configuration ---

load_dotenv()
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY not found in environment variables. Add it to your .env file.")

client = OpenAI(api_key=api_key)

with open("agent_config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

entry_file = config.get("entry_file", "app.py")
rules_path = config.get("rules_path", "rules.json")
max_attempts = config.get("max_attempts", 3)
timeout = config.get("timeout", 30)

def load_rules(rules_path):
    try:
        with open(rules_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return "\n".join(data.get("rules", []))
    except Exception:
        return ""

def looks_like_python_code(text: str) -> bool:
    stripped = text.strip()
    return bool(stripped) and any(
        token in stripped for token in ["def ", "class ", "import ", "__name__"]
    )

def sentry_agent_run():
    print("🤖 AutoFix Agent: Monitoring...")

    attempt = 0
    last_test_output = ""

    while attempt < max_attempts:
        print(f"\n🔁 Attempt {attempt + 1}/{max_attempts}")

        context = {
            "file": None,
            "line_number": None,
            "function": None,
            "error_type": None,
            "error_message": None,
        }
        similar_failures = []

        try:
            process = subprocess.run(
                [sys.executable, entry_file],
                capture_output=True,
                text=True,
                timeout=timeout
            )

        except subprocess.TimeoutExpired as e:
            print("⏱️ App execution timed out!")

            process = None
            error_content = f"TimeoutExpired: execution exceeded {timeout} seconds"

        # ── Case 1: App runs successfully ─────────────────────────────
        if process is not None and process.returncode == 0:
            print("⚠️ App ran successfully, checking tests only...")

            target_file = entry_file
            test_path = infer_test_path(target_file)

            print("🧪 Running verification tests...")
            passed, results = run_tests(test_path)

            if passed:
                print("✅ Tests passed! No fix needed.")
                return
            else:
                print("❌ App runs, but tests failed. Retrying with test feedback...")
                print(results)

                error_content = "Application runs successfully, but tests are failing."
                last_test_output = results
                target_file = entry_file
                test_path = infer_test_path(target_file)

                context = {
                    "file": target_file,
                    "line_number": None,
                    "function": "test_verification",
                    "error_type": "TestFailure",
                    "error_message": "Application runs successfully, but tests are failing.",
                }
                similar_failures = get_similar_failures(
                    error_type=context.get("error_type") or "UnknownError",
                    target_file=target_file,
                )


        # ── Case 2: App crashed ───────────────────────────────────────
        else:
            if process is None:
                last_error = error_content
                target_file = entry_file
                test_path = infer_test_path(target_file)
                print(f"💥 Crash Detected: {last_error}")
                print(f"📂 Target file detected: {target_file}")

                context = {
                    "file": target_file,
                    "line_number": None,
                    "function": "app_execution",
                    "error_type": "TimeoutExpired",
                    "error_message": error_content,
                }
                similar_failures = get_similar_failures(
                    error_type=context.get("error_type") or "UnknownError",
                    target_file=target_file,
                )

            else:
                error_content = process.stderr or process.stdout or "Unknown error"
                last_error = error_content.splitlines()[-1] if error_content else "Unknown error"

                print(f"💥 Crash Detected: {last_error}")

                context = extract_crash_context(error_content)
                target_file = context["file"] or entry_file
                test_path = infer_test_path(target_file)
                print(f"📂 Target file detected: {target_file}")

                similar_failures = get_similar_failures(
                    error_type=context.get("error_type") or "UnknownError",
                    target_file=target_file,
                )

        app_code = read_file(target_file)
        rules_text = load_rules(rules_path)

        related_files = collect_related_files(target_file)
        related_files_text = "\n\n".join(
            f"FILE: {path}\n{code}" for path, code in related_files.items()
        )

        prompt = f"""
        You are SentryAgent AI. Fix the following Python bug.

        Follow these coding rules strictly:
        {rules_text}

        Error Message:
        {error_content}

        Previous Test Failures (if any):
        {last_test_output}
        
        Primary Target File:
        {target_file}

        Similar Past Failures:
        {json.dumps(similar_failures, indent=2, ensure_ascii=False)}

        Current Code:
        {app_code}
        
        Related Local Files:
        {related_files_text}

        Return ONLY the corrected python code. No explanations.
        """

        print("🧠 GPT-4o is thinking...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            fixed_code = response.choices[0].message.content
            if not fixed_code:
                raise ValueError("Empty response from model")

            fixed_code = fixed_code.replace("```python", "").replace("```", "").strip()

        except Exception as e:
            print(f"❌ Failed to parse AI response: {e}")
            return

        if not fixed_code:
            print("❌ No valid fix generated. Skipping write.")
            return

        if not looks_like_python_code(fixed_code):
            print("❌ Model response does not look like valid Python code. Skipping write.")
            return

        is_valid_fix, validation_issues = validate_fix_candidate(app_code, fixed_code)
        if not is_valid_fix:
            print("❌ Generated fix failed validation:")
            for issue in validation_issues:
                print(f"   - {issue}")

            memory_entry = build_memory_entry(
                error_type=context.get("error_type") or "UnknownError",
                error_message=context.get("error_message") or error_content,
                target_file=target_file,
                attempt=attempt + 1,
                fix_summary="Generated fix failed validation.",
                tests_passed=False,
                validation_issues=validation_issues,
            )
            append_memory(memory_entry)

            last_test_output = "\n".join(validation_issues)
            attempt += 1
            continue

        backup_path = backup_file(target_file)
        if backup_path:
            print(f"💾 Backup created: {backup_path}")
        else:
            print(f"⚠️ No backup created for {target_file} (file may not exist yet).")

        write_file(target_file, fixed_code)
        print(f"🛠️ Fix applied to {target_file}!")

        print("🧪 Running verification tests...")
        passed, results = run_tests(test_path)

        if passed:
            print("✅ Tests passed! Issue resolved.")

            memory_entry = build_memory_entry(
                error_type=context.get("error_type") or "UnknownError",
                error_message=context.get("error_message") or error_content,
                target_file=target_file,
                attempt=attempt + 1,
                fix_summary="Generated fix passed validation and tests.",
                tests_passed=True,
            )
            append_memory(memory_entry)
            return
        else:
            print("❌ Tests failed, restoring backup...")
            print(results)

            restored = restore_backup(target_file)
            if restored:
                print(f"↩️ Backup restored for {target_file}")
            else:
                print(f"⚠️ No backup found for {target_file}, could not restore.")

            memory_entry = build_memory_entry(
                error_type=context.get("error_type") or "UnknownError",
                error_message=context.get("error_message") or error_content,
                target_file=target_file,
                attempt=attempt + 1,
                fix_summary="Generated fix failed tests and backup was restored.",
                tests_passed=False,
                validation_issues=[results],
            )
            append_memory(memory_entry)

            last_test_output = results

        attempt += 1

    print("🚨 Max attempts reached. Could not fix the issue.")


if __name__ == "__main__":
    sentry_agent_run()
