import ast
from pathlib import Path


def extract_local_imports(file_path: str | Path) -> list[str]:
    """
    Extract imported module names from a Python file.
    """
    path = Path(file_path)
    if not path.exists():
        return []

    try:
        code = path.read_text(encoding="utf-8")
        tree = ast.parse(code)
    except Exception:
        return []

    imported_modules = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_modules.append(node.module)

    return imported_modules


def resolve_local_module_to_file(module_name: str, project_root: str | Path = ".") -> Path | None:
    """
    Convert a module name like 'utils.helpers' into a local file path like './utils/helpers.py'.
    Return the file path only if it exists.
    """
    root = Path(project_root)
    candidate = root / f"{module_name.replace('.', '/')}.py"

    if candidate.exists():
        return candidate

    return None


def collect_related_files(target_file: str | Path, project_root: str | Path = ".") -> dict[str, str]:
    """
    Collect the target file and its directly imported local files.
    Returns a dictionary:
        {file_path_string: file_content}
    """
    target_path = Path(target_file)
    related_files = {}

    if target_path.exists():
        related_files[str(target_path)] = target_path.read_text(encoding="utf-8")

    imported_modules = extract_local_imports(target_path)

    for module_name in imported_modules:
        module_file = resolve_local_module_to_file(module_name, project_root)
        if module_file and module_file.exists():
            try:
                related_files[str(module_file)] = module_file.read_text(encoding="utf-8")
            except Exception:
                pass

    return related_files