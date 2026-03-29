import os
import re

def find_imports(start_path='.'):
    imports = set()
    # Regex patterns to catch "import x" and "from x import y"
    import_pattern = re.compile(r'^import\s+([a-zA-Z0-9_]+)')
    from_pattern = re.compile(r'^from\s+([a-zA-Z0-9_]+)')

    for root, dirs, files in os.walk(start_path):
        # Skip virtual environments and hidden folders
        if any(skip in root for skip in ['venv', 'env', '.git', '__pycache__']):
            continue

        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            match_import = import_pattern.match(line)
                            match_from = from_pattern.match(line)

                            if match_import:
                                imports.add(match_import.group(1))
                            if match_from:
                                imports.add(match_from.group(1))
                except Exception:
                    pass

    return sorted(list(imports))

if __name__ == "__main__":
    print("Scanning codebase for imports...")
    modules = find_imports()
    print("\nFound these top-level modules:")
    for mod in modules:
        print(f"- {mod}")