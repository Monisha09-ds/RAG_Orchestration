#####------------------#####
import os
import argparse
from pathlib import Path
import pathspec

# --- Styling ---
HEADER_LINE = "*" * 100
FILE_SEPARATOR = "\n\n"

# --- Default patterns to ignore ---
DEFAULT_IGNORE_PATTERNS = [
    ".git/",
    ".venv/",
    "venv/",
    "__pycache__/",
    "*.pyc",
    ".env",
    ".env.*",
    "uv.lock",
    "poetry.lock",
    "Pipfile.lock",
    "package-lock.json",
    "yarn.lock",
    ".gitignore",
    "LICENSE",
    "license",
    ".vscode/",
    ".idea/",
    "*.csv",
    "*.txt",
    "*.json",
    "*.db",
    "*.sqlite",
    "*.sql",
    "*.xlsx",
    "*.parquet",
    "data/",
    "final_data/",
    "dummy folder for test/",
    "docs/",
    "users.csv",
]


def get_gitignore_spec(directory: Path, output_filename: str) -> pathspec.PathSpec:
    gitignore_file = directory / ".gitignore"
    project_patterns = []

    if gitignore_file.is_file():
        with open(gitignore_file, "r", encoding="utf-8") as f:
            project_patterns = f.readlines()

    all_patterns = DEFAULT_IGNORE_PATTERNS + [output_filename] + project_patterns
    return pathspec.PathSpec.from_lines("gitwildmatch", all_patterns)


# =====================================================================
# Write grouped output (folder-wise)
# =====================================================================
def write_grouped_output(grouped_files: dict, output_dir: Path):
    # <<< NEW: Always start clean >>>
    output_dir.mkdir(parents=True, exist_ok=True)
    for old_file in output_dir.glob("*.txt"):
        try:
            old_file.unlink()
            print(f"  [–] Removed old file: {old_file}")
        except Exception as e:
            print(f"  [!] Could not remove {old_file}: {e}")
    # <<< END NEW >>>

    for group_name, files in grouped_files.items():
        out_path = output_dir / f"{group_name}.txt"

        with open(out_path, "w", encoding="utf-8") as outfile:
            for rel_path, content in files:
                outfile.write(f"{HEADER_LINE}\n")
                outfile.write(f"File: {rel_path}\n")
                outfile.write(f"{HEADER_LINE}\n\n")
                outfile.write(content)
                outfile.write(FILE_SEPARATOR)

        print(f"  [✓] Saved → {out_path}")


def process_directory(root_dir: str, output_dir: str, spec: pathspec.PathSpec):
    root_path = Path(root_dir).resolve()
    output_dir = Path(output_dir).resolve()

    print(f"\nProcessing directory: {root_path}")
    print(f"Output folder: {output_dir}\n")

    grouped_files = {"root_files": []}  # Top-level loose files

    for dirpath, dirnames, filenames in os.walk(root_path, topdown=True):
        current_path = Path(dirpath)

        # Filter ignored directories
        dirnames[:] = [
            d for d in dirnames
            if not spec.match_file(str((current_path / d).relative_to(root_path)).replace("\\", "/") + "/")
        ]

        for filename in filenames:
            file_path = current_path / filename
            rel_path = file_path.relative_to(root_path)
            rel_path_str = str(rel_path).replace("\\", "/")

            if spec.match_file(rel_path_str):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as infile:
                    content = infile.read()

                parts = rel_path_str.split("/")
                group_name = parts[0] if len(parts) > 1 else "root_files"

                if group_name not in grouped_files:
                    grouped_files[group_name] = []

                grouped_files[group_name].append((rel_path_str, content))
                print(f"  [+] Added to '{group_name}': {rel_path_str}")

            except Exception as e:
                print(f"  [!] Error reading {rel_path_str}: {e}")

    write_grouped_output(grouped_files, output_dir)

    print("\nDone! Folder-wise extraction complete.")


def main():
    parser = argparse.ArgumentParser(
        description="Generate folder-wise codebase summaries.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "-d",
        "--directory",
        help="Root directory to scan (if not provided, script prompts)"
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output folder (if not provided, script prompts)"
    )

    args = parser.parse_args()

    # Interactive mode fallback
    if args.directory:
        root_directory = Path(args.directory)
    else:
        user_input_dir = input("Enter the root directory to scan: ").strip()
        root_directory = Path(user_input_dir)

    if args.output:
        output_directory = args.output
    else:
        user_input_out = input("Enter the output folder name: ").strip()
        output_directory = user_input_out

    if not root_directory.is_dir():
        print(f"Error: Directory not found at {root_directory}")
        return

    spec = get_gitignore_spec(root_directory, "dummy_output_file.txt")
    process_directory(str(root_directory), output_directory, spec)


if __name__ == "__main__":
    main()