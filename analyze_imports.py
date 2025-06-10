import os
import re
import sys

# Standard library modules for Python 3.10+
try:
    stdlib_modules = sys.stdlib_module_names
except AttributeError:
    # Fallback for older Python versions (less accurate)
    # This is a simplified list, a more comprehensive one might be needed for < 3.10
    stdlib_modules = frozenset([
        'abc', 'argparse', 'asyncio', 'base64', 'collections', 'contextlib',
        'datetime', 'decimal', 'email', 'enum', 'functools', 'hashlib', 'http',
        'importlib', 'io', 'json', 'logging', 'math', 'multiprocessing', 'operator',
        'os', 'pathlib', 'pdb', 'pickle', 'platform', 'queue', 'random', 're',
        'secrets', 'select', 'shutil', 'signal', 'socket', 'sqlite3', 'ssl',
        'stat', 'string', 'struct', 'subprocess', 'sys', 'tarfile', 'tempfile',
        'textwrap', 'threading', 'time', 'traceback', 'typing', 'unittest', 'urllib',
        'uuid', 'warnings', 'weakref', 'webbrowser', 'xml', 'zipfile', 'zlib'
    ])
    print("Warning: sys.stdlib_module_names not available. Using a fallback list of standard modules (may be incomplete).")


def get_project_modules(files):
    project_modules = set()
    for file_path in files:
        if file_path.endswith(".py"):
            # Convert file path to module path (e.g., agents/coding/agent.py -> agents.coding.agent)
            module_path = file_path.replace(".py", "").replace("/", ".")
            project_modules.add(module_path)
            # Add parent packages as well (e.g., agents.coding, agents)
            parts = module_path.split('.')
            for i in range(1, len(parts)):
                project_modules.add('.'.join(parts[:i]))
    return project_modules

def get_third_party_libs(requirements_file):
    libs = {} # Stores mapping from import name to package name
    try:
        with open(requirements_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    match = re.match(r"([a-zA-Z0-9_-]+)", line)
                    if match:
                        package_name = match.group(1)
                        # Common import name mappings
                        if package_name.lower() == 'pyyaml':
                            libs['yaml'] = package_name
                        elif package_name.lower() == 'python-dotenv':
                            libs['dotenv'] = package_name
                        elif package_name.lower() == 'speechrecognition':
                             libs['speech_recognition'] = package_name
                        # Add more mappings if needed, otherwise assume import name is similar to package name
                        else:
                            libs[package_name.lower().replace('-', '_')] = package_name
    except FileNotFoundError:
        print(f"Error: {requirements_file} not found.")
    return libs


def analyze_imports(files, project_modules, third_party_libs_map):
    missing_deps = {} # Imports not found anywhere
    inconsistent_deps = {} # Found in requirements but commented out, or vice-versa
    unknown_imports = {} # Could not categorize (e.g. relative import errors)

    # More robust import pattern:
    # Catches:
    # import x
    # import x.y
    # from x import y
    # from x.y import z
    # from . import x
    # from .x import y
    # from .. import x
    # from ..x import y
    import_pattern = re.compile(
        r"^\s*(?:from\s+([.\w]+)\s+import\s+(?:\([\w\s,]+\)|\*|[\w, ]+)|import\s+([.\w]+))",
        re.MULTILINE
    )


    for file_path in files:
        if not file_path.endswith(".py"):
            continue
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

        current_file_package_parts = file_path.replace(".py", "").split("/")[:-1]

        for match in import_pattern.finditer(content):
            imported_module_str = match.group(1) or match.group(2)
            if not imported_module_str:
                continue

            root_module_to_check = ""
            is_relative = False

            if imported_module_str.startswith("."):
                is_relative = True
                num_dots = 0
                while imported_module_str[num_dots] == '.':
                    num_dots += 1

                relative_path_part = imported_module_str[num_dots:]

                if num_dots == 1: # from . import foo OR from .bar import foo
                    if not relative_path_part: # from . import foo
                        # This implies importing a module from the current package.
                        # The actual module being imported is specified in the "import part" (e.g. from . import actual_module)
                        # The regex captures the "from" part. For simplicity, we'll assume this is a valid project internal import.
                        continue # Skip further checks for "from . import ..."
                    else: # from .bar import foo
                        root_module_to_check = relative_path_part.split(".")[0]
                        # This will be checked against project modules.

                elif num_dots > 1: # from ..bar import foo or from .. import foo
                    if len(current_file_package_parts) < (num_dots -1):
                        if file_path not in unknown_imports: unknown_imports[file_path] = set()
                        unknown_imports[file_path].add(f"{imported_module_str} (relative import goes too high)")
                        continue

                    # Trying to construct the absolute path for checking, but the root is what matters for classification
                    # Example: agents/coding/agent.py -> from ..base_agent import X -> core.base_agent
                    # current_file_package_parts = ['agents', 'coding']
                    # num_dots = 2. Path becomes agents.base_agent.
                    # We are interested in 'agents' as the root for classification against project structure.
                    if relative_path_part:
                        root_module_to_check = relative_path_part.split(".")[0]
                    else: # from .. import X (imports module X from parent package)
                        # This is complex to map to a single root module without knowing X
                        # For now, we'll assume these are valid project internal imports if they don't error out.
                        continue
                else: # Should not happen if starts with "."
                    continue

                # For relative imports, the root_module_to_check is part of the project.
                # We'll assume it's a project module and skip other checks.
                # A more thorough check would construct the full absolute path and check against project_modules set.
                if root_module_to_check in project_modules or any(pm.startswith(root_module_to_check) for pm in project_modules):
                    continue
                # If not found, it might be an error in relative import logic or a missing module.

            else: # Absolute import
                root_module_to_check = imported_module_str.split(".")[0]

            if not root_module_to_check:
                continue

            # Normalize for comparison
            root_module_lower = root_module_to_check.lower()

            if root_module_lower in stdlib_modules:
                continue  # Standard library
            if root_module_lower in project_modules: # Check against root of project modules (e.g. 'agents' for 'agents.coding.agent')
                continue  # Project module
            if root_module_lower in third_party_libs_map: # Check if the import is a known third-party lib key
                continue  # Third-party library in requirements.txt

            # Check if it's a submodule of a listed third-party lib (e.g. google.cloud for google-cloud-storage)
            # This is a simplification. A more robust way is to get top_level.txt from installed packages.
            is_submodule_of_known_lib = False
            for lib_import_name in third_party_libs_map.keys():
                if root_module_lower.startswith(lib_import_name) or root_module_lower == lib_import_name:
                    is_submodule_of_known_lib = True
                    break
            if is_submodule_of_known_lib:
                continue

            # If we reach here, it's missing or unknown
            if file_path not in missing_deps:
                missing_deps[file_path] = set()
            missing_deps[file_path].add(root_module_to_check)


    if missing_deps:
        print("\n--- Missing or Inconsistent Dependencies ---")
        print("The following modules are imported but not found in standard libraries, project modules, or requirements.txt:")
        for file, modules in missing_deps.items():
            print(f"File: {file}")
            for module in modules:
                print(f"  - '{module}'")

    if inconsistent_deps:
        print("\n--- Inconsistent Dependencies (vs requirements.txt) ---")
        for file, modules in inconsistent_deps.items():
            print(f"File: {file}")
            for module_info in modules:
                print(f"  - '{module_info['module']}' (found as '{module_info['found_as']}' in requirements.txt - {module_info['status']})")

    if unknown_imports:
        print("\n--- Unknown or Potentially Problematic Imports ---")
        for file, modules in unknown_imports.items():
            print(f"File: {file}")
            for module in modules:
                print(f"  - Could not categorize: '{module}'")

    if not missing_deps and not inconsistent_deps and not unknown_imports:
        print("\nAll imports appear to be consistent and accounted for.")


if __name__ == "__main__":
    all_repo_files = []
    for root, dirs, files in os.walk("."):
        # Exclude virtual environment and .vscode directories
        dirs[:] = [d for d in dirs if 'dmac_env' not in d and '.vscode' not in d]
        for file in files:
            full_path = os.path.join(root, file)
            all_repo_files.append(full_path.replace("\\", "/").lstrip("./"))

    python_files = [f for f in all_repo_files if f.endswith(".py")]

    project_modules = get_project_modules(all_repo_files) # Pass all files to correctly map module structure

    third_party_libs_map = get_third_party_libs("requirements.txt")

    if not third_party_libs_map and os.path.exists("requirements.txt"):
        print("Warning: requirements.txt is empty or could not be parsed correctly (no libraries found).")
    elif not os.path.exists("requirements.txt"):
        print("Error: requirements.txt not found.")

    analyze_imports(python_files, project_modules, third_party_libs_map)
