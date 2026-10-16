#!/usr/bin/env python3
"""Enable a project store and install the protocol into explicit instruction files."""

import argparse
from pathlib import Path
import re
import sys

BEGIN = "<!-- BEGIN AGENT-MEMORY-PROTOCOL -->"
END = "<!-- END AGENT-MEMORY-PROTOCOL -->"
ROOT = Path(__file__).resolve().parent.parent


def replace_block(current, block):
    if BEGIN not in current and END not in current:
        separator = "" if not current else "\n" if current.endswith("\n") else "\n\n"
        return current + separator + block + "\n"
    if current.count(BEGIN) != 1 or current.count(END) != 1:
        raise ValueError("protocol markers are incomplete or duplicated")
    start, end = current.index(BEGIN), current.index(END)
    if end < start:
        raise ValueError("protocol markers are out of order")
    return current[:start] + block + current[end + len(END):]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", help="project directory basename, such as my-app")
    parser.add_argument("--instructions", type=Path, action="append", default=[],
                        help="user-level instruction file; may be repeated")
    parser.add_argument("--dry-run", action="store_true", help="preview without writing")
    args = parser.parse_args()
    if not args.project and not args.instructions:
        parser.error("provide --project, --instructions, or both")

    planned = {}
    if args.project:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", args.project):
            raise ValueError("project must be a basename using letters, digits, dots, _ or -")
        project = ROOT / args.project
        if project.is_symlink() or project.exists() and not project.is_dir():
            raise ValueError("project store must be a regular directory")
        index = project / "MEMORY.md"
        if project.exists() and not index.is_file():
            raise ValueError("existing directory has no MEMORY.md; choose a project store")
        if index.is_symlink():
            raise ValueError("project index must not be a symlink")
        if not index.exists():
            planned[index] = ""

    source = (ROOT / "PROTOCOL.md").read_text(encoding="utf-8")
    if source.count(BEGIN) != 1 or source.count(END) != 1 or source.index(END) < source.index(BEGIN):
        raise ValueError("PROTOCOL.md must contain exactly one ordered marker pair")
    block = source[source.index(BEGIN):source.index(END) + len(END)]
    if any(char in str(ROOT) for char in "`\n\r"):
        raise ValueError("memory path must not contain backticks or line breaks")
    block = block.replace("{{MEMORY_ROOT}}", str(ROOT))

    for argument in args.instructions:
        target = argument.expanduser().absolute()
        if target.is_symlink():
            raise ValueError("instruction file is a symlink; pass its real target explicitly")
        if target.resolve().is_relative_to(ROOT):
            raise ValueError("instruction files must be outside the memory checkout")
        current = target.read_text(encoding="utf-8") if target.exists() else ""
        updated = replace_block(current, block)
        if updated != current:
            planned[target] = updated

    for path, content in planned.items():
        print(f"{'Would write' if args.dry_run else 'Writing'} {path}")
        if not args.dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if not planned:
        print("Already up to date.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError) as error:
        print(f"install: {error}", file=sys.stderr)
        sys.exit(1)
