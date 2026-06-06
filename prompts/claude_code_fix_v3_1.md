# Claude Code Fix Protocol: v3.1 Daily Research Cockpit

> Machine-facing prompt. Use English, exact paths, explicit acceptance criteria, and no vague product decisions.

## ROLE

You are Claude Code acting as a careful maintenance engineer for a public, zero-dependency local research dashboard.

## REPOSITORY

Repository: `Dalaoyuan2020/pipeline-board`

This repo is a public tool/player. Real research content must stay outside this repo.

## OBJECTIVE

Apply a focused hardening pass to the existing v3.1 Daily Research Cockpit implementation.

Do not expand scope. Do not redesign the product. Do not add new major features.

Your job is to fix the issues identified in:

```text
docs/review_v3_1_daily_cockpit_2026_06_01.md
```

Priority order:

1. Fix `/api/file` path safety.
2. Add frontend HTML escaping for task/cockpit dynamic fields.
3. Normalize demo naming or update all docs consistently.
4. Update stale v2 wording to v3.1.
5. Remove temporary JavaScript expression `silent&&false`.
6. Run local verification and produce a checklist report.

## NON-NEGOTIABLE CONSTRAINTS

1. Keep the project zero-dependency.
2. Use only Python standard library, HTML, CSS, and plain JavaScript.
3. Do not add Flask, FastAPI, React, Vue, Node, npm, database, or build tools.
4. Keep startup command unchanged:

```bash
python3 src/app.py
```

5. Keep the app local-only by default, bound to `127.0.0.1`.
6. Keep the panel read-only. Do not add write-back API routes.
7. Preserve v2 `.state.json` compatibility.
8. Do not remove the existing state overview or document library.
9. Do not add an Agent role dashboard/tab.
10. Do not put real manuscripts, reviewer letters, datasets, API keys, passwords, or private research content into the public repo.
11. Do not rename existing Chinese documentation unless you also preserve compatibility or update all references.
12. New file names must be English and ASCII-only.

## CURRENT STATUS

v3.1 has already been implemented as a runnable prototype:

- `src/app.py` reads `tasks.json`, `planner/today.json`, and `planner/done_log.json`.
- `/api/tree` returns `projects`, `flow`, `today`, `done_log`, and `profiles`.
- The default page is `Daily Research Cockpit`.
- The project page has `Status Overview`, `Task Pool`, and `Document Library` tabs.
- Demo data, profiles, prompts, and README have been added.

However, the review found several issues that must be fixed before stable usage.

## TASKS

### Task 1: Fix path traversal and prefix-bypass safety

File: `src/app.py`

Current risk:

```python
def safe_under_root(p):
    return os.path.realpath(p).startswith(os.path.realpath(PROJ_ROOT))
```

This is unsafe because sibling paths with the same prefix may pass.

Replace with:

```python
def safe_under_root(p):
    root = os.path.realpath(PROJ_ROOT)
    target = os.path.realpath(p)
    try:
        return os.path.commonpath([root, target]) == root
    except ValueError:
        return False
```

Acceptance:

- Valid project files can still be read through `/api/file`.
- `../` traversal attempts return 404.
- Sibling-prefix paths cannot pass validation.

### Task 2: Add HTML escaping for cockpit/task dynamic fields

File: `src/app.py`

Add a frontend helper in the JavaScript section:

```javascript
function h(s){
  return String(s ?? '')
    .replace(/&/g,'&amp;')
    .replace(/</g,'&lt;')
    .replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;')
    .replace(/'/g,'&#39;')
}
```

Use `h()` for all JSON/user/agent-derived fields inserted into `innerHTML`, including but not limited to:

```text
t.title
t.starter
t.action
t.done_criteria
t.blocker
t.why
t.stage
t.substep
sel.why_today
sel.project_title
sel.project
sel.task_id
p.title_cn
r.note
r.task_id
r.date
T.message
T.recent_wins[]
```

Important:

- Keep `q()` for onclick argument escaping.
- Do not replace the existing Markdown `esc()` logic unless necessary.
- Do not break document rendering.

Acceptance:

- Demo task cards still render normally.
- If a task title contains `<script>alert(1)</script>`, it is displayed as text and not executed.
- If a task field contains quotes or angle brackets, the UI is not broken.

### Task 3: Normalize demo naming or update docs consistently

The review found a mismatch:

Task document mentions:

```text
demo_paper_cockpit
demo_thesis_cockpit
```

Current implementation may use:

```text
paper_demo_cockpit
thesis_demo_cockpit
```

Choose one canonical naming convention and make it consistent everywhere.

Preferred canonical names:

```text
demo_paper_cockpit
demo_thesis_cockpit
```

If you rename, update all references in:

```text
demo/planner/today.json
demo/planner/done_log.json
demo/state/*.state.json
demo/projects/*/tasks.json
README.md
docs/*.md, if they mention demo paths
```

Acceptance:

- Demo mode loads today tasks correctly.
- `today.json` project names match actual project folder names.
- State file names match actual project folder names.
- README/docs do not contradict the actual demo paths.

### Task 4: Update stale v2 wording

File: `src/app.py`

Update docstring and startup log from v2 to v3.1.

Suggested wording:

```text
Research Pipeline Board · v3.1 Daily Research Cockpit
```

Startup print:

```python
print(f"🔬 科研流水线 v3.1 Daily Cockpit: http://localhost:{PORT}")
```

Acceptance:

- No misleading v2 startup message remains.
- README and code wording are consistent.

### Task 5: Remove temporary JavaScript expression

File: `src/app.py`

Replace this type of temporary expression:

```javascript
if(view==='cockpit'){if(!(silent&&false))renderCockpit();return}
```

with clear logic. Prefer:

```javascript
if(view==='cockpit'){
  renderCockpit();
  return;
}
```

Acceptance:

- No `silent&&false` remains.
- Cockpit still refreshes correctly.

### Task 6: Optional small README refinement

File: `README.md`

If needed, change the first description line to mention both dashboard and cockpit:

```text
一个零依赖、本地运行的科研进度面板 + 今日科研驾驶舱。
```

Do not rewrite README completely.

## FILES TO MODIFY

Allowed:

```text
src/app.py
README.md
demo/planner/today.json
demo/planner/done_log.json
demo/state/*.state.json
demo/projects/*/tasks.json
docs/*.md, only if needed for path consistency
```

Optional:

```text
prompts/*.md, only if you need to fix naming references
```

## FILES NOT TO MODIFY

Do not modify unrelated files. Do not delete existing design documents. Do not add new dependencies or config files.

## VERIFICATION COMMANDS

Run at least:

```bash
python3 -m py_compile src/app.py
python3 src/app.py
```

Then manually check in browser:

```text
http://localhost:8771
```

Manual UI checks:

1. Default page is `Daily Research Cockpit`.
2. Today task cards show at most 3 tasks.
3. Each task card shows why/starter/action/done criteria.
4. Project page has `Task Pool` tab.
5. Document Library still opens text files.
6. Missing `today.json` degrades gracefully.
7. HTML injection test is displayed as text, not executed.

## ACCEPTANCE CHECKLIST

Report each item as PASS/FAIL:

```text
[ ] safe_under_root uses commonpath and blocks traversal.
[ ] Frontend dynamic task/cockpit fields are HTML-escaped.
[ ] Demo names are consistent across folders, state, today, done_log, README/docs.
[ ] v2 wording is updated to v3.1 where appropriate.
[ ] No silent&&false remains.
[ ] python3 -m py_compile src/app.py passes.
[ ] python3 src/app.py starts successfully.
[ ] Default page is Daily Research Cockpit.
[ ] Today task cards display correctly.
[ ] Task Pool tab displays tasks by status.
[ ] Document Library still works.
[ ] No third-party dependencies were added.
[ ] No write-back API routes were added.
[ ] No real/private research content was added.
```

## FINAL REPORT FORMAT

After making changes, produce a final report in this format:

```text
Summary:
- ...

Files changed:
- ...

Verification:
- py_compile: PASS/FAIL
- local server start: PASS/FAIL
- browser checks: PASS/FAIL or NOT RUN

Acceptance checklist:
- [x] ...
- [ ] ...

Known remaining issues:
- ...
```

## STOP CONDITIONS

Stop and ask for human review if:

1. Fixing a task requires adding dependencies.
2. Fixing a task requires changing the read-only architecture.
3. Renaming demo folders would conflict with existing Git history in a way you cannot resolve safely.
4. You find real private content in the public demo.

Do not silently bypass any failed requirement.
