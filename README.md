# Agent Memory Template

Keep useful context across coding agents and machines with plain Markdown and
Git. Each project gets a small index and one file per durable fact. Claude Code,
Codex, and other agents can read the same notes through a shared protocol.

[中文说明](README.zh-CN.md) · [Memory protocol](PROTOCOL.md) · [Examples](examples/my-app)

This public template contains only fictional examples. **Create a private copy
for your real memories.** The helpers need no API key, database, or model service.
They use Python 3.9+, Bash, and Git on macOS or Linux.

## Start in five minutes

1. Choose **Use this template → Create a new repository** on GitHub. Select
   **Private** and use a name such as `agent-memory`. Copy its clone URL.
2. Clone **your new repository** to an unused directory:

   ```bash
   git clone YOUR_PRIVATE_REPOSITORY_URL "$HOME/.agents/memory"
   cd "$HOME/.agents/memory"
   ```

   Any location works. The installer uses the checkout's actual absolute path.
   If you already have a memory store, use another location and review migration
   manually; these helpers do not import or replace existing memories.
3. Enable a project and install the protocol for the agents you use. Replace
   `my-app` with the basename of your project directory:

   ```bash
   python3 bin/install.py --project my-app \
     --instructions "$HOME/.codex/AGENTS.md" \
     --instructions "$HOME/.claude/CLAUDE.md" --dry-run

   # Review the target paths, then run the same command without --dry-run.
   python3 bin/install.py --project my-app \
     --instructions "$HOME/.codex/AGENTS.md" \
     --instructions "$HOME/.claude/CLAUDE.md"
   ```

   Omit either instruction file if you do not use that agent. Existing text
   outside the protocol markers is preserved. Re-running updates that block
   without duplicating it. Invalid markers stop the run before any file writes.
4. Finish the agent-specific access setup below, start a **new session** in
   `my-app`, and ask: “Which shared memory store applies to this project?”
   Then try: “Remember that I prefer a concrete example before an abstract
   explanation.” Check `my-app/MEMORY.md` and its linked topic file yourself.

The installer creates an empty index. The examples are documentation only and
are never copied into your active memory.

## What goes where

```text
~/.agents/memory/             # your private copy; location is configurable
  PROTOCOL.md                # common read/write rules
  bin/install.py             # enable stores and update instruction blocks
  bin/sync.sh                # synchronize commits you have reviewed
  examples/my-app/           # fictional examples of all four memory types
  my-app/                    # created only when you enable this project
    MEMORY.md                # one link per fact
    preferred-explanations.md
```

| Type | Useful for |
| --- | --- |
| `user` | Stable preferences and relevant background |
| `feedback` | Corrections and the reason behind them |
| `project` | Product or team context not derivable from the repository |
| `reference` | Pointers to external resources and when they were verified |

Keep source-code explanations in the source, workflows in skills or agent
instructions, and temporary progress in the current task. Remembered facts may
go stale; current instructions and verified evidence take precedence.

## Connect your agents

### Codex

Use the global instruction file in your Codex home, normally
`~/.codex/AGENTS.md`. If you set `CODEX_HOME`, pass the file under that directory.
A non-empty `AGENTS.override.md` takes precedence; install into that file if
you use it. See the [official instruction discovery rules](https://learn.chatgpt.com/docs/agent-configuration/agents-md#how-codex-discovers-guidance).

For CLI `workspace-write` sessions, merge the absolute memory path into your
Codex `config.toml` (normally `~/.codex/config.toml`), preserving existing entries:

```toml
[sandbox_workspace_write]
writable_roots = ["/home/you/.agents/memory"]
```

Use your actual path. Managed or desktop sessions may have their own access
controls; use the supported directory-access flow when needed. The installer
does not change permissions or configuration. See the [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).

### Claude Code

The shared protocol can live in `~/.claude/CLAUDE.md`. Pass your actual user
instruction path if you use a custom configuration directory.

To point Claude's native auto memory at the same store, merge this into the
project's `.claude/settings.local.json`:

```json
{
  "autoMemoryDirectory": "~/.agents/memory/my-app"
}
```

Use your actual store path and preserve other settings. Keep this personal
configuration out of source control. Workspace trust and managed permissions
still apply. See [Claude Code memory documentation](https://code.claude.com/docs/en/memory#storage-location).

### Other agents, nested projects, and worktrees

Pass another agent's documented user-level instruction file with
`--instructions`, or paste the marked block from `PROTOCOL.md` into its user
rules after replacing `{{MEMORY_ROOT}}`. The agent needs file access to the
store. This is a prompt convention, not a native integration for every agent.

The protocol looks for a store matching the working directory's basename, then
each ancestor's basename. A nested repository can therefore share an enabled
workspace store. Two unrelated projects with the same basename would share
memory: choose distinct local names or write an explicit mapping in your user
instructions. Worktrees with different directory names also need an explicit
mapping to the original store; the protocol does not infer Git identities.

To enable another store: `python3 bin/install.py --project another-app`.
Re-run the instruction installation after moving this checkout or editing the
protocol. Cloud runners need their own clone, instruction setup, and file access.

## Sync between machines

Use the same private repository on each machine and install the protocol there.
Before a session, with a clean working tree:

```bash
bash bin/sync.sh pull
```

After a session, review new and changed files before committing:

```bash
git status --short
git diff
# Also read new files: git diff does not show untracked content.
git add my-app/MEMORY.md my-app/preferred-explanations.md
git diff --cached
git commit -m "memory: update explanation preference"
bash bin/sync.sh push
```

`sync.sh` defaults to `status`. It never stages or commits files, includes no
machine identity in commit messages, and never force-pushes. Pulls are fast-forward
only; dirty trees, missing upstreams, and diverged branches return errors.
`push` pulls first and stops if that fails. Review divergence with Git and
resolve it explicitly, for example with `git pull --rebase` after inspecting
both sides. No automatic hooks are installed; sync may wait for Git authentication.

Run the script from anywhere, or set `AGENT_MEMORY_DIR` to another memory
checkout. Concurrent sync commands use a local lock. If one was forcibly killed,
confirm no sync is running before removing the lock directory reported by
`git rev-parse --git-path agent-memory-sync.lock`.

Git does not coordinate agents editing the same file. Keep changes focused and
review conflicts before syncing. A private repository limits access but does
not encrypt notes; never store credentials or material you are not allowed to
share with the repository's readers and configured agents.

## Maintain or remove

- Review stale facts and broken index links periodically. Keep the index short.
- To disconnect an agent, remove its `AGENT-MEMORY-PROTOCOL` block and any memory
  directory or permission setting you added. Keep or archive the notes separately.
- To contribute, use fictional data and reserved example URLs. Run
  `python3 tests/smoke.py`; it uses temporary homes and local Git repositories,
  with no network or agent calls.

MIT licensed. The license covers the template; it does not grant access to anyone's
personal memory store.
