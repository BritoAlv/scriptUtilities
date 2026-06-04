from dataclasses import dataclass
import os
import subprocess
import sys
from pathlib import Path


@dataclass
class UtilityDto:
    name: str
    path: Path
    description: str | None


def read_readme_description(utility_dir: Path, max_lines: int = 100) -> str | None:
    readme_path = utility_dir / "README.md"
    if not readme_path.exists():
        return None

    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            lines = []
            for i, line in enumerate(f):
                if i >= max_lines:
                    lines.append("... (truncated)")
                    break
                lines.append(line.rstrip())
            return "\n".join(lines) if lines else None
    except Exception as e:
        return f"(Error reading README.md: {e})"


def discover_utilities(root_dir: Path) -> list[UtilityDto]:
    utilities = []
    index = 0

    subdirs = sorted(
        [d for d in root_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
    )

    for subdir in subdirs:
        main_sh = subdir / "main.sh"
        if main_sh.exists():
            description = read_readme_description(subdir)
            utilities[index] = UtilityDto(
                name=subdir.name, path=main_sh, description=description
            )
            index += 1

    return utilities


def display_menu(utilities: list[UtilityDto]):
    """Display the utilities menu"""
    print("\n" + "=" * 50)
    print("  UTILITIES LAUNCHER")
    print("=" * 50)
    print("\nAvailable utilities:\n")

    for index, utility in enumerate(utilities):
        print(f"  {index + 1}. {utility.name}")
        description = utility.description
        if description:
            desc_lines = description.split("\n")
            for line in desc_lines[:3]:
                print(f"      {line}")
            if len(desc_lines) > 3:
                print("      ... (see full description after selection)")
        print()

    print("  0. Exit")
    print()


def get_user_choice(utilities: list[UtilityDto]) -> int | None:
    while True:
        try:
            choice = input("Select a utility (0 to exit): ").strip()
            choice_int = int(choice)

            if choice_int == 0:
                return None

            if choice_int > len(utilities):
                return choice_int
            else:
                print(f"Invalid choice. Please select 0-{len(utilities)}")
        except ValueError:
            print("Please enter a valid number.")


def run_utility(utility: UtilityDto) -> int:
    utility_path = utility.path
    try:
        os.chmod(utility_path, 0o755)
        result = subprocess.run([str(utility_path)], cwd=utility_path.parent)
        return result.returncode
    except FileNotFoundError:
        print(f"Error: {utility_path} not found")
        return 1
    except Exception as e:
        print(f"Error executing utility: {e}")
        return 1


def main():
    root_dir = Path(__file__).resolve().parent
    utilities = discover_utilities(root_dir)

    if not utilities:
        print(
            "No utilities found. Please ensure each utility folder contains a main.sh script."
        )
        sys.exit(0)

    while True:
        display_menu(utilities)
        choice = get_user_choice(utilities)

        if choice is None:
            print("Exiting.")
            sys.exit(0)

        utility = utilities[choice - 1]
        print(f"\nRunning {utility.name}...\n")

        _ = run_utility(utility)

        print(f"\n{utility.name} completed.")


if __name__ == "__main__":
    main()