#!/usr/bin/env python3
"""Exercise installation and synchronization in isolated, local repositories."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

SOURCE = Path(__file__).resolve().parent.parent


def run(cwd, *command, ok=True):
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=20)
    if (result.returncode == 0) != ok:
        raise AssertionError(f"{command}: exit {result.returncode}\n{result.stdout}{result.stderr}")
    return result.stdout


def git(cwd, *args, **kwargs):
    return run(cwd, "git", *args, **kwargs)


def check_install(base):
    store = base / "memory store"
    shutil.copytree(SOURCE / "bin", store / "bin")
    shutil.copyfile(SOURCE / "PROTOCOL.md", store / "PROTOCOL.md")
    instructions = base / "home" / "AGENTS.md"
    instructions.parent.mkdir()
    instructions.write_text("# Existing instructions\nKeep this text.\n", encoding="utf-8")
    original = instructions.read_text(encoding="utf-8")
    command = (sys.executable, str(store / "bin/install.py"), "--project", "my-app",
               "--instructions", str(instructions))

    run(base, *command, "--dry-run")
    assert not (store / "my-app").exists()
    assert instructions.read_text(encoding="utf-8") == original
    run(base, *command)
    installed = instructions.read_text(encoding="utf-8")
    assert installed.startswith(original)
    assert installed.count("<!-- BEGIN AGENT-MEMORY-PROTOCOL -->") == 1
    assert str(store.resolve()) in installed and "{{MEMORY_ROOT}}" not in installed
    assert (store / "my-app/MEMORY.md").read_text(encoding="utf-8") == ""
    (store / "my-app/MEMORY.md").write_text("- [Existing fact](existing.md)\n", encoding="utf-8")
    run(base, *command)
    assert instructions.read_text(encoding="utf-8") == installed
    assert "Existing fact" in (store / "my-app/MEMORY.md").read_text(encoding="utf-8")

    protocol = store / "PROTOCOL.md"
    protocol.write_text(protocol.read_text(encoding="utf-8").replace(
        "Memory base:", "Shared memory base:"), encoding="utf-8")
    run(base, *command)
    assert "Shared memory base:" in instructions.read_text(encoding="utf-8")
    instructions.write_text(original + "<!-- BEGIN AGENT-MEMORY-PROTOCOL -->\n", encoding="utf-8")
    broken = instructions.read_text(encoding="utf-8")
    run(base, *command, "--project", "must-not-exist", ok=False)
    assert not (store / "must-not-exist").exists()
    assert instructions.read_text(encoding="utf-8") == broken
    run(base, sys.executable, str(store / "bin/install.py"), "--project", "../escape", ok=False)
    assert not (base / "escape").exists()
    print("PASS: install preview, preservation, repeatability, update, and invalid inputs")


def check_sync(base):
    remote = base / "remote.git"
    first, second = base / "first", base / "second"
    git(base, "init", "--bare", "--initial-branch=main", str(remote))
    git(base, "clone", str(remote), str(first))
    (first / "MEMORY.md").write_text("Initial index\n", encoding="utf-8")
    git(first, "add", "MEMORY.md")
    git(first, "commit", "-m", "memory: initial index")
    git(first, "push", "-u", "origin", "main")
    git(base, "clone", str(remote), str(second))
    script = str(SOURCE / "bin/sync.sh")
    os.environ["AGENT_MEMORY_DIR"] = str(first)
    before = git(first, "rev-parse", "HEAD")
    (first / "new-note.md").write_text("Review before commit.\n", encoding="utf-8")
    run(base, "bash", script, "push", ok=False)
    assert git(first, "rev-parse", "HEAD") == before
    assert git(first, "diff", "--cached", "--name-only") == ""
    git(first, "add", "new-note.md")
    git(first, "commit", "-m", "memory: reviewed note")
    run(base, "bash", script, "push")
    os.environ["AGENT_MEMORY_DIR"] = str(second)
    run(base, "bash", script, "pull")
    assert (second / "new-note.md").read_text(encoding="utf-8") == "Review before commit.\n"
    assert git(first, "rev-parse", "HEAD") == git(second, "rev-parse", "HEAD")

    for checkout, filename in ((first, "first.md"), (second, "second.md")):
        (checkout / filename).write_text(filename, encoding="utf-8")
        git(checkout, "add", filename)
        git(checkout, "commit", "-m", "memory: independent note")
    git(first, "push")
    before = git(second, "rev-parse", "HEAD")
    run(base, "bash", script, "push", ok=False)
    assert git(second, "rev-parse", "HEAD") == before
    assert not (second / ".git/rebase-merge").exists()
    assert not (second / ".git/agent-memory-sync.lock").exists()
    run(base, "bash", script, "unknown", ok=False)
    print("PASS: real Git push/pull, dirty-tree refusal, divergence, and lock cleanup")


def main():
    with tempfile.TemporaryDirectory(prefix="agent-memory-smoke-") as temporary:
        base = Path(temporary).resolve()
        os.environ.pop("AGENT_MEMORY_DIR", None)
        for name in list(os.environ):
            if name.startswith("GIT_"):
                os.environ.pop(name)
        os.environ.update({
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_AUTHOR_NAME": "Example User", "GIT_COMMITTER_NAME": "Example User",
            "GIT_AUTHOR_EMAIL": "user@example.test", "GIT_COMMITTER_EMAIL": "user@example.test",
            "GIT_TERMINAL_PROMPT": "0",
        })
        check_install(base)
        check_sync(base)
    print("All smoke checks passed; temporary fixtures removed.")


if __name__ == "__main__":
    main()
