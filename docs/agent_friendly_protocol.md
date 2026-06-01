# Agent-Friendly Protocol for pipeline-board

> Purpose: make this repository easier for AI coding agents, automation tools, and humans to read and modify safely.

## 1. Naming convention

Use English, ASCII-only, kebab-case or snake_case file names for all new files.

Recommended:

```text
docs/review_v3_1_daily_cockpit_2026_06_01.md
docs/agent_friendly_protocol.md
prompts/claude_code_fix_v3_1.md
profiles/paper.json
profiles/thesis.json
demo/planner/today.json
```

Avoid for new files:

```text
docs/方向图_从看板到科研驾驶舱.md
docs/CC_一键执行任务书_Daily_Cockpit_v3_1.md
```

Existing Chinese file names may be kept for backward compatibility, but new canonical files should use English file names.

## 2. Human-facing vs machine-facing documents

Use two document layers.

### Human-facing documents

- File names: English.
- Content language: Chinese is preferred if the document is mainly for the project owner or human collaborators.
- Goal: explain direction, reasoning, product intent, review conclusions, and usage notes.

Examples:

```text
docs/review_v3_1_daily_cockpit_2026_06_01.md
docs/product_direction_daily_cockpit.md
```

### Machine-facing prompts and protocols

- File names: English.
- Content language: English.
- Format: explicit, structured, imperative.
- Goal: let Claude Code / AI coding agents execute changes reliably.

Examples:

```text
prompts/claude_code_fix_v3_1.md
prompts/daily_planner.md
prompts/revision_task_splitter.md
```

## 3. Prompt style for coding agents

Machine prompts should be written like a protocol, not like an essay.

Required sections:

```text
ROLE
REPOSITORY
OBJECTIVE
NON-NEGOTIABLE CONSTRAINTS
CURRENT STATUS
TASKS
FILES TO MODIFY
FILES NOT TO MODIFY
ACCEPTANCE CHECKLIST
VERIFICATION COMMANDS
FINAL REPORT FORMAT
```

Rules:

1. Use English for machine prompts.
2. Use exact file paths.
3. Use numbered tasks.
4. State what must not be changed.
5. State expected outputs and validation steps.
6. Avoid vague words like "improve", "optimize", or "make better" unless paired with measurable criteria.
7. Do not ask the agent to decide the product direction unless that is the explicit task.
8. Ask the agent to produce a final checklist report.

## 4. Data and code boundaries

The repository is a public player/tool. Real research content belongs outside this repo.

Keep in public repo:

```text
src/app.py
demo/ fake data
profiles/ generic profile data
prompts/ reusable prompts
docs/ design and review documents
```

Do not put in public repo:

```text
real manuscripts
real reviewer letters
private datasets
passwords
API keys
institutional secrets
paper-vault content
```

## 5. Agent execution contract

For Claude Code or any code agent:

1. Read the relevant prompt first.
2. Do not rewrite the whole project unless explicitly asked.
3. Keep the project zero-dependency.
4. Keep `python3 src/app.py` as the only startup command.
5. Keep the panel read-only unless a future prompt explicitly enables write mode.
6. Preserve v2 `.state.json` compatibility.
7. After modification, run basic checks and report results.
8. Never silently ignore failed checklist items.

## 6. Recommended repository policy

From now on:

- New docs: English file names.
- New machine prompts: English content.
- New human summaries: Chinese content allowed, English file names required.
- New JSON schemas: English field names.
- New demo folder names: English only.
- New commit messages: English preferred.

## 7. Why this matters

Chinese content is good for human understanding, especially for the project owner. English file names and English machine prompts are better for tooling, shell commands, GitHub search, AI coding agents, and cross-platform compatibility.

This protocol keeps both sides efficient:

```text
Chinese for human cognition.
English for machine execution.
English file names for repository stability.
```
