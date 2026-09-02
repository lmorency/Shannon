# Shannon skill host surfaces

> Part of the Shannon **SKILL** (`skills/shannon/SKILL.md`). Install via
> `./scripts/shannon skill-install` so each host TUI loads this pack.

Shannon does **not** invent a second orchestrator per product. T1 Code and
T3 Code are **control planes**: they start Claude Code / Codex / Cursor /
Grok Build / OpenCode. Those workers still pick their id **by host process**
and report through the gate. Remote Claude Code and ChatGPT/Codex sessions
run on the desktop that owns `~/.claude` / `~/.codex` — there is no cloud
copy of this skill.

## Who loads `SKILL.md`

| Surface | Canonical id | Skill dirs the installer writes | Harness keyword |
|---------|--------------|-------------------------------|-----------------|
| Claude Code (CLI, macOS, **remote**) | `claude_code` | `.claude/skills`, `~/.claude/skills` | `claude` |
| Codex (CLI, ChatGPT **remote**) | `codex` | `.codex/skills`, `~/.codex/skills` | `codex` |
| ChatGPT (conversation / remote controller) | `chatgpt` | same Codex trees; register as `chatgpt` only if ChatGPT itself attaches | — |
| OpenCode | `opencode` | `.opencode/skills`, `~/.config/opencode/skills`, `~/.opencode/skills` | `opencode` |
| Cursor / `cursor-agent` | `cursor` | `.cursor/skills`, `~/.cursor/skills` | `cursor`, `cursor-agent` |
| Grok Build CLI | `grok_build` | `.grok/skills`, `~/.grok/skills` | `grok` |
| Grok Bot (grok.com / X) | `grok_bot` | no local skill tree; gate identity only | — |
| Oh-My-Pi (`omp`) | `omp` | `.omp/skills`, `~/.omp/agent/skills` | `omp` |
| Pi (pi.dev) | `pi` | `.pi/skills`, `~/.pi/agent/skills` | `pi` |
| T1 Code (T3 in the terminal) | `t1_code` | inherits Claude/Codex/Cursor/Grok/OpenCode/`.agents` | `t1code` |
| T3 Code (desktop / web / **mobile**) | `t3_code` | same inherit set; T3 Claude scan is `~/.claude/skills` then `.claude/skills` | `t3code` |
| macOS Claude Dispatch | `dispatch` | Claude plugin + `~/.claude/skills` (Cowork/Code) | — |
| Cowork (macOS **and iOS**) | `cowork` | Claude plugin + `~/.claude/skills` | — |
| GitHub Copilot agent skills | `vscode` / `cursor` as appropriate | `.github/skills`, `~/.copilot/skills` | — |
| Cross-tool Agent Skills dir | — | `.agents/skills`, `~/.agents/skills`, `.agent/skills` | — |

T1/T3 **do not replace** the worker id. A T3 thread that launched Claude Code
is still `claude_code`. Spawn `t1_code` / `t3_code` only when the control-plane
process itself reports to the gate (coordinator), never as a second docking
owner.

## Remote: Claude Code and ChatGPT

- **Claude Code remote** (Claude iOS/web → desktop Code) is the same
  `claude_code` process. User skills in `~/.claude/skills` and the repo
  `.claude/skills` apply. Aliases: `claude_code_remote`, `claude_remote`.
- **ChatGPT remote** (ChatGPT iOS/web → Codex on the Mac) is the same `codex`
  process. User skills in `~/.codex/skills` apply. Aliases: `codex_remote`.
  Use `chatgpt` / `chatgpt_remote` only when the ChatGPT surface attaches as
  itself.
- Neither remote copies `~/.cursor/skills` or `~/.omp/agent/skills` onto a
  cloud VM. Keep a **project** copy (`.claude/skills`, `.codex/skills`,
  `.agents/skills`) so a checkout-only worker still sees the handrail.

## macOS Dispatch and Cowork on iOS

Dispatch and Cowork load **Claude plugins and skills**, not a Shannon-specific
iOS package (the HUD is Shannon UI; this repo is the CLI). This checkout is a
Claude plugin via `.claude-plugin/plugin.json`:

```bash
# Claude Code / Cowork: add this repo as a local plugin
claude --plugin-dir "$SHANNON_ROOT"
```

Cowork on iPhone dispatches work to the Mac that has Claude Desktop awake.
The Mac must have the skill installed (`~/.claude/skills/shannon` or this
plugin). iOS Cowork does not read `~/.codex` or `~/.omp`.

Aliases: `cowork_ios`, `ios_cowork` → `cowork`; `macos_dispatch`,
`macos_claude_dispatch` → `dispatch`.

## NDJSON / JSONL streams

Remote and TUI hosts that expose token logprobs still use the existing monitor
(JSON Lines / NDJSON). Shannon does **not** invent H from T1/T3 event streams.

```bash
shannon-monitor stdin --format text < stream.jsonl
# C++: ./build/shannon-agent --field logprobs --logprobs < stream.jsonl
```

Each line is one JSON object with a `logprobs` (or `probs`) array. Empty or
missing fields are skipped; they are not treated as collapse.

## Control-plane vs worker

```
T3 / T1 / Cowork iOS / ChatGPT remote / Claude remote
        │  starts / steers
        ▼
  claude_code | codex | cursor | grok_build | opencode | omp | pi
        │  spawn / control / result / kill
        ▼
  Shannon Gate  (/tmp/shannon.sock)  →  pill
```

Do not register T3 as `claude_code`. Do not register Claude Code remote as
`dispatch`. Pick the id of the **process that edits files**.
