#!/usr/bin/env bash
# Synchronize reviewed commits without creating commits or rewriting history.
set -euo pipefail

root="${AGENT_MEMORY_DIR:-$(cd -- "$(dirname -- "$0")/.." && pwd -P)}"
cd -- "$root"
if [[ ! -e .git ]]; then
  echo 'sync: memory root must be a Git checkout' >&2
  exit 1
fi

action="${1:-status}"
case "$action" in
  status) exec git status --short --branch ;;
  pull|push) ;;
  *) echo 'usage: sync.sh [status|pull|push]' >&2; exit 2 ;;
esac

lock="$(git rev-parse --git-path agent-memory-sync.lock)"
if ! mkdir -- "$lock" 2>/dev/null; then
  echo 'sync: another sync is running; inspect the lock if an earlier sync was interrupted' >&2
  exit 1
fi
trap 'rmdir -- "$lock"' EXIT

if [[ -n "$(git status --porcelain)" ]]; then
  echo 'sync: review and commit or stash local changes before syncing' >&2
  exit 1
fi
git symbolic-ref --quiet HEAD >/dev/null
git rev-parse --verify '@{upstream}' >/dev/null
git -c pull.rebase=false pull --ff-only
if [[ "$action" == push ]]; then
  git push
fi
