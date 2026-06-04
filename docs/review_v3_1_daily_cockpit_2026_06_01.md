# v3.1 Daily Research Cockpit 严格审查报告

> Human-facing review document. 文件名使用英文，内容使用中文，便于人读；后续给 AI Agent 执行的 Prompt 使用英文。

审查日期：2026-06-01  
审查对象：`Dalaoyuan2020/pipeline-board`  
审查标准：`docs/CC_一键执行任务书_Daily_Cockpit_v3_1.md` 第 10 节验收清单  
结论：**v3.1 主体功能已经落地，基本达到可本地打开自用的程度；但开源稳定前必须修安全与健壮性问题。**

---

## 1. 总评

这次改造已经从“v2 看板 + v3.1 文档”推进到“v3.1 Daily Research Cockpit 可运行雏形”。

已经落地：

- 后端读取 `tasks.json`、`planner/today.json`、`planner/done_log.json`。
- `/api/tree` 返回 `projects / flow / today / done_log / profiles`。
- 首页默认进入“今日驾驶舱”。
- 首页最多展示 1–3 个今日任务。
- 今日任务卡显示 `why_today / starter / action / done_criteria`。
- 项目页新增 `✅ 任务池` tab。
- demo 数据、profiles、prompts、README 均已补齐。

但必须修：

1. `/api/file` 的路径越界判断不严。
2. 前端动态内容未统一 HTML 转义，存在本地 UI 注入 / XSS 风险。
3. demo 文件夹命名与任务书存在不一致，建议统一。

---

## 2. 🔴 必须修

### 2.1 修复 `/api/file` 路径越界判断

位置：`src/app.py`

当前逻辑类似：

```python
def safe_under_root(p):
    return os.path.realpath(p).startswith(os.path.realpath(PROJ_ROOT))
```

问题：

如果 `PROJ_ROOT=/x/projects`，路径 `/x/projects_bak/secret.txt` 也会通过 `startswith('/x/projects')` 判断。虽然本工具默认只监听 `127.0.0.1`，但作为公开工具仍应修正。

要求改为：

```python
def safe_under_root(p):
    root = os.path.realpath(PROJ_ROOT)
    target = os.path.realpath(p)
    try:
        return os.path.commonpath([root, target]) == root
    except ValueError:
        return False
```

验收：

- `/api/file?path=<正常项目文件>` 正常读取。
- `../` 越界路径返回 404。
- 类似 sibling prefix 的路径不能误通过。

---

### 2.2 修复前端动态 HTML 未转义问题

位置：`src/app.py` 内嵌前端 JS：`taskCard()`、`poolCard()`、`renderCockpit()`、`renderTaskPool()`。

问题：

当前任务字段如 `title / starter / action / done_criteria / blocker / why_today` 直接拼进 `innerHTML`。以后这些字段可能由 Agent 生成，如果出现 HTML 标签或事件属性，会污染页面甚至执行脚本。

要求增加 HTML 转义函数：

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

所有用户/JSON/Agent 生成字段进入 `innerHTML` 前必须使用 `h()`，包括但不限于：

```text
t.title
t.starter
t.action
t.done_criteria
t.blocker
t.why
sel.why_today
sel.project_title
sel.project
p.title_cn
r.note
r.task_id
```

注意：

- `q()` 只用于 onclick 参数转义，不等于 HTML 转义。
- `md()` 内部已有 `esc()`，不要破坏原 Markdown 渲染。

验收：

- demo 正常显示。
- 在 `tasks.json` 中临时写入 `<script>alert(1)</script>`，页面应显示文本，不执行脚本。

---

### 2.3 统一 demo 命名

任务书中写的是：

```text
demo/projects/demo_paper_cockpit/tasks.json
demo/projects/demo_thesis_cockpit/tasks.json
demo/state/demo_paper_cockpit.state.json
demo/state/demo_thesis_cockpit.state.json
```

当前实现使用的是：

```text
paper_demo_cockpit
thesis_demo_cockpit
```

当前功能可能能跑，因为 `today.json` 与实际文件名内部一致；但这会让后续 Claude Code / Agent 按任务书找文件时混乱。

建议采用任务书命名，即：

```text
demo_paper_cockpit
demo_thesis_cockpit
```

同时更新：

- `demo/planner/today.json`
- `demo/planner/done_log.json`
- `demo/state/*.state.json`
- `demo/projects/*/tasks.json`
- README 或相关 docs 中的 demo 路径说明

---

## 3. 🟡 建议改

### 3.1 更新 v2 文案

`src/app.py` 文件头和启动日志仍有 v2 文案。建议统一为：

```text
Research Pipeline Board · v3.1 Daily Research Cockpit
```

启动日志建议：

```python
print(f"🔬 科研流水线 v3.1 Daily Cockpit: http://localhost:{PORT}")
```

---

### 3.2 清理临时代码表达式

当前 JS 中存在类似：

```javascript
if(view==='cockpit'){if(!(silent&&false))renderCockpit();return}
```

建议改为更清楚的：

```javascript
if(view==='cockpit'){
  renderCockpit();
  return;
}
```

或者如果希望静默刷新时不打断滚动，则明确写：

```javascript
if(view==='cockpit'){
  if(!silent) renderCockpit();
  return;
}
```

不要保留 `silent&&false` 这种临时代码。

---

### 3.3 长期未动恢复目前主要依赖 prompt

当前首页能显示 `blocked` 任务，但还没有根据 `updated_at` 自动识别长期未动项目。MVP 可以接受，因为 `prompts/recovery_task_generator.md` 已提供恢复任务生成能力。

后续建议：

- 如果某项目所有任务 `updated_at` 超过 N 天无变化，在首页提示“可生成低压力恢复任务”。
- 不要批评用户，不显示羞耻式提醒。

---

### 3.4 README 可进一步前置 v3.1 定位

README 已经加入 v3.1 说明，但开头仍偏“科研进度面板”。建议第一句话改为：

```text
一个零依赖、本地运行的科研进度面板 + 今日科研驾驶舱。
```

---

## 4. 🟢 做对的

- 仍保持纯 Python 标准库，未引入 Flask / React / Node / 数据库。
- 仍保持 `python3 src/app.py` 一条命令启动。
- 仍默认监听 `127.0.0.1`。
- 保持 v2 `.state.json` 兼容。
- 面板仍是只读展示，没有网页写回真实内容库。
- 首页 Daily Cockpit 已落地。
- 任务池 tab 已落地。
- `today.json / done_log.json / tasks.json` 数据层已落地。
- prompt 库已落地。
- 没有把 Agent 角色页做成主界面。
- demo 内容看起来是公开假数据，未发现真实密钥/密码/真实论文内容。

---

## 5. 对照任务书第 10 节验收清单

| # | 验收项 | 结果 | 说明 |
|---:|---|---|---|
| 1 | `python3 src/app.py` 能启动 | ✅ 代码层看可启动 | 未本地执行，仅基于源码判断。 |
| 2 | 无第三方依赖 | ✅ | 只使用 Python 标准库。 |
| 3 | demo 模式下默认进入“今日驾驶舱” | ✅ | 前端默认 `view='cockpit'`。 |
| 4 | 首页最多显示 3 个今日任务 | ✅ | 后端 `selected_tasks[:3]`。 |
| 5 | 每个今日任务显示 `why_today / starter / action / done_criteria` | ✅ | `taskCard()` 已显示。 |
| 6 | 首页显示最近完成或正反馈 | ✅ | `recent_wins` + `done_log`。 |
| 7 | 没有 `today.json` 时优雅降级，不报错 | ✅ | `configured:false` 空态。 |
| 8 | 每个项目可以显示 `tasks.json` 中的任务池 | ✅ | 后端扫描 + 前端任务池 tab。 |
| 9 | v2 state.json 老项目仍能显示流程和文档库 | ✅ | 原 state / flow / docs 逻辑保留。 |
| 10 | 文档库原有功能不破坏 | ✅ 基本通过 | 建议本地再点开验证。 |
| 11 | 不新增 Agent 角色主 tab | ✅ | 主 tab 为状态总览 / 任务池 / 文档库。 |
| 12 | 不把真实论文内容写进公开 demo | ✅ 未发现 | 仍建议提交前继续 grep secrets。 |
| 13 | README 指向 v3.1 文档 | ✅ | 已指向方向图与任务书。 |

---

## 6. 最终结论

一句话：

> **v3.1 已经达到可本地打开自用的雏形，但在继续开源推广或接真实 paper-vault 前，必须先修路径安全和 HTML 转义。**

建议下一步只做“小修补”，不要再扩大功能范围：

```text
1. Fix safe_under_root.
2. Add frontend HTML escaping.
3. Normalize demo folder names or update docs consistently.
4. Update v2 wording to v3.1.
5. Clean temporary JS expression.
6. Run local verification on Mac Mini.
```
