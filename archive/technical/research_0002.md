# Research 0002 — awesome-copilot: Skills Layout, Plugin Install, and Global Use

Date: 2026-03-21
Reference: https://github.com/github/awesome-copilot

---

## Q1 — Why are skills at the top-level `skills/` and NOT under `.github/`?

### Short answer
`awesome-copilot` is a **plugin marketplace repository**, not a project repository.
Top-level placement is intentional and specific to the marketplace role.

### Explanation

GitHub's official documentation (docs.github.com/en/copilot/concepts/agents/about-agent-skills)
defines two supported skill locations:

| Location | Purpose |
|---|---|
| `.github/skills/` or `.claude/skills/` | **Project skills** — scoped to one repository |
| `~/.copilot/skills/` or `~/.claude/skills/` | **Personal skills** — shared across all projects on a machine |

`awesome-copilot` sits outside both categories: its `skills/` directory is at repo root
because the repo is consumed via the **plugin marketplace system**, not directly cloned
by users. The Copilot CLI's plugin installer pulls individual skill folders out of the
repo and places them in `~/.copilot/skills/`, making them personal/global.

In other words: the top-level `skills/` is the layout Copilot's marketplace tooling expects
to resolve packages from `github/awesome-copilot`. It is NOT the layout you use for your
own project or personal skills.

**For your own repo** the conventional location remains `.github/skills/`. This is the
standard project-skill path and is what the current `the-archive` workspace already uses
(`.github/skills/toc-first-search/`).

---

## Q2 — What are users expected to do after `git clone`?

### Short answer
**Nothing** — users are NOT expected to clone `awesome-copilot`.
The intended workflow is plugin installation from the CLI, not a git clone.

### Intended workflow (from README)

Step 1 (modern CLI — `awesome-copilot` marketplace is pre-registered):
```bash
copilot plugin install <plugin-name>@awesome-copilot
```

Step 2 (older CLI or custom setup — register marketplace first):
```bash
copilot plugin marketplace add github/awesome-copilot
copilot plugin install <plugin-name>@awesome-copilot
```

The plugin installer downloads the named plugin folder (which is a bundle of an
agent + skill(s)) into the user's local Copilot data directory.

### What `copilot plugin install` actually does
- Fetches the named plugin's files from the registered marketplace GitHub repo
- Writes the skill folder to `~/.copilot/skills/<skill-name>/`
- The skill is then automatically available in every project session

---

## Q3 — Is there a way to install skills once and use everywhere?

### Short answer
**Yes.** Two mechanisms exist:

### Mechanism A — `copilot plugin install` (recommended for public/community skills)

Use `copilot plugin install` from a registered marketplace (e.g., `github/awesome-copilot`).
This installs to `~/.copilot/skills/`, making the skill **global** across all projects
on the machine.

```bash
# Example: install the 'cli-mastery' skill globally
copilot plugin install cli-mastery@awesome-copilot
```

### Mechanism B — Manual placement in `~/.copilot/skills/` (recommended for private/custom skills)

For skills not in any public marketplace (like the `toc-first-search` + `archive-tools`
skill in this workspace), the equivalent approach is:

1. Copy (or symlink) the skill folder to `~/.copilot/skills/<skill-name>/`
2. The skill is picked up by Copilot CLI in every future session — no per-project setup required.

This is the "install once, use everywhere" equivalent for private/custom skills.

---

## Implications for `the-archive` / `archive-tools`

### Current state (correct for project-level use)
- `.github/skills/toc-first-search/` — correct project skill path
- `.github/mcp/archive-tools/server.py` — MCP server for the active tools
- `.vscode/mcp.json` — VS Code Copilot MCP registration (project-scoped)

### Recommended deployment path for global use

| Target | Action |
|---|---|
| Copilot CLI (global) | Ship an `install.ps1` / `install.sh` that copies skill to `~/.copilot/skills/toc-first-search/` |
| VS Code Copilot (all projects) | Copy skill to `~/.copilot/skills/` AND register MCP server in VS Code's user-level settings `~/.vscode/.../mcp.json` |
| Public sharing via marketplace | Restructure repo to match `awesome-copilot` contribution guide and submit a PR |

### Key insight
The `.github/skills/` location is NOT a limitation — it is the right place for a project skill.
The "install once" experience is unlocked by publishing to `~/.copilot/skills/` (personal skills),
not by moving files out of `.github/`. The `awesome-copilot` top-level layout is a
marketplace convention, not a general recommendation.

---

## Correction to previous research (research_0001.md)

`research_0001.md` concluded that Copilot CLI had no `/plugin install` equivalent.
That was incorrect. The `copilot plugin install` command exists and is documented
in the `awesome-copilot` README and Copilot CLI documentation. The previous search
did not reach the `awesome-copilot` README.

**Updated conclusion:**
- `copilot plugin install <name>@awesome-copilot` → installs a community plugin globally
- `~/.copilot/skills/` → personal skills directory for custom/private install-once skills
- Both mechanisms achieve the "deploy once, use everywhere" goal

---

## References
- github/awesome-copilot README (consulted 2026-03-21)
- docs.github.com/en/copilot/concepts/agents/about-agent-skills (consulted 2026-03-21)
- docs.github.com/en/copilot/concepts/agents/copilot-cli/about-copilot-cli (consulted 2026-03-21)
