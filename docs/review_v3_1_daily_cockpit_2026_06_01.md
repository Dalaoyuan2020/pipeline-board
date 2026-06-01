# v3.1 Daily Research Cockpit 严格审查报告

> Human-facing review document. 文件名使用英文，内容使用中文，便于人读；后续给 AI Agent 执行的 Prompt 使用英文。

审查日期：2026-06-01  
审查对象：`Dalaoyuan2020/pipeline-board`  
审查基准：`docs/CC_一键执行任务书_Daily_Cockpit_v3_1.md` 第 10 节验收清单  
审查方式：只读审查，不直接修改代码。

---

## 0. 一句话总评

v3.1 主体功能已经落地，已经可以让用户在本地打开查看 Daily Research Cockpit 效果；但在接入真实内容库或开源推广前，必须先修复两个问题：

1. `/api/file` 路径越界判断不够严谨。
2. 前端任务字段未统一 HTML 转义，存在 UI 注入/XSS 风险。

修完这两个问题后，项目可以进入“自用可用、继续打磨”的状态。

---

## 1. 已完成的关键能力

### 1.1 数据层已落地

`src/app.py` 已经加入：

- `CONTENT_ROOT`
- `PLANNER_DIR`
- `PROFILES_DIR`
- `read_json()`
- 每项目 `tasks.json` 读取
- `planner/today.json` 读取
- `planner/done_log.json` 读取
- `profiles/*.json` 读取

`/api/tree` 已返回：

```json
{
  "projects": [],
  "flow": [],
  "today": {},
  "done_log": [],
  "profiles": {}
}
```

这说明 v3.1 不再只是文档，后端数据结构已经真正进入代码。

### 1.2 前端 Daily Cockpit 已落地

前端已新增：

- `🚀 今日驾驶舱`
- 默认进入 cockpit view
- `renderCockpit()`
- 今日任务卡片
- 最近完成 / 正反馈
- 当前卡住
- 项目任务概览

任务卡已经显示：

- project
- role
- priority
- energy
- status
- title
- why_today / why
- starter
- action
- done_criteria
- blocker

### 1.3 项目任务池已落地

项目页 tab 已扩展为：

```text
📋 状态总览
✅ 任务池
📂 文档库
```

`renderTaskPool()` 已按以下状态显示任务：

- doing
- todo
- blocked
- done

每张任务池卡片能显示：

- priority
- energy
- status
- stage / substep
- title
- starter
- done_criteria
- blocker

### 1.4 Demo 数据已落地

仓库中已包含：

```text
demo/planner/today.json
demo/planner/done_log.json
demo/projects/paper_demo_cockpit/tasks.json
demo/projects/thesis_demo_cockpit/tasks.json
demo/state/paper_demo_cockpit.state.json
demo/state/thesis_demo_cockpit.state.json
```

其中 paper demo 覆盖：

- revision
- writing
- experiment
- blocked

thesis demo 覆盖：

- 综述维护
- 框架定义
- 章节切分

### 1.5 Prompt 库已落地

已包含：

```text
prompts/daily_planner.md
prompts/revision_task_splitter.md
prompts/recovery_task_generator.md
```

这三份 prompt 的定位正确：面板保持只读，Agent/LLM 只负责生成结构化任务文件。

---

## 2. 🔴 必须修

### 2.1 修复 `/api/file` 路径越界判断

当前风险：

```python
def safe_under_root(p):
    return os.path.realpath(p).startswith(os.path.realpath(PROJ_ROOT))
```

问题：

`startswith()` 判断路径前缀不够严谨。例如：

```text
/x/projects
/x/projects_bak
```

第二个路径也可能通过字符串前缀判断。

必须改为：

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

- `/api/file?path=<合法项目文件>` 正常读取。
- `../` 越界路径不能读取。
- 与 `PROJ_ROOT` 同前缀但不在根目录下的路径不能读取。

---

### 2.2 前端任务字段必须统一 HTML 转义

当前风险：

`taskCard()`、`poolCard()`、`renderCockpit()`、`renderTaskPool()` 中大量字段直接拼接进 `innerHTML`。

风险字段包括：

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
```

这些数据未来可能来自 Agent 生成的 JSON。如果 JSON 中出现 HTML 标签或事件属性，页面可能被注入。

必须新增前端转义函数：

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

所有动态插入 HTML 的任务字段必须使用 `h()`。

注意：

- `q()` 只用于 onclick 参数转义。
- `h()` 用于 HTML 内容转义。
- 两者不能互相替代。

验收：

在 demo task 的 title/starter/action 中临时加入：

```html
<img src=x onerror=alert(1)>
```

页面应显示文本本身，而不是执行 HTML。

---

### 2.3 统一 demo 命名，避免 Agent 混乱

任务书中建议路径是：

```text
demo/projects/demo_paper_cockpit/tasks.json
demo/projects/demo_thesis_cockpit/tasks.json
```

当前实际路径是：

```text
demo/projects/paper_demo_cockpit/tasks.json
demo/projects/thesis_demo_cockpit/tasks.json
```

二者内部引用目前一致，因此不会立即导致运行失败；但会让后续 Claude Code / Agent 按文档找路径时混乱。

推荐二选一：

方案 A，推荐：统一实际目录为任务书路径。

```text
paper_demo_cockpit  → demo_paper_cockpit
thesis_demo_cockpit → demo_thesis_cockpit
```

同时更新：

```text
demo/state/*.state.json
demo/planner/today.json
README.md
docs/CC_一键执行任务书_Daily_Cockpit_v3_1.md
```

方案 B：保留当前目录名，修改任务书，使任务书与实现一致。

推荐方案 A，因为任务书是验收基准。

---

## 3. 🟡 建议改

### 3.1 更新 v2 文案为 v3.1

当前 `src/app.py` 文件头和启动日志仍出现 v2 文案。

建议改成：

```text
Research Pipeline Board · v3.1 Daily Research Cockpit
```

启动日志建议改成：

```python
print(f"🔬 科研流水线 v3.1 Daily Cockpit: http://localhost:{PORT}")
```

### 3.2 清理临时代码 `silent&&false`

当前前端中有：

```javascript
if(view==='cockpit'){if(!(silent&&false))renderCockpit();return}
```

建议改为更清楚的写法：

```javascript
if(view==='cockpit'){
  renderCockpit();
  return;
}
```

如果不希望静默刷新时重绘 cockpit，则用：

```javascript
if(view==='cockpit'){
  if(!silent) renderCockpit();
  return;
}
```

### 3.3 task_counts 建议加入 dropped

当前任务状态规范中包含：

```text
todo / doing / done / blocked / dropped
```

但 `task_counts` 只统计：

```text
todo / doing / done / blocked
```

建议加入 `dropped`，避免未来统计丢失。

### 3.4 README 开头应纳入 v3.1 定位

README 已有 v3.1 章节，但开头仍主要描述“科研进度面板”。建议改成：

```text
一个零依赖、本地运行的科研进度面板 + 今日科研驾驶舱。
```

### 3.5 说明 profiles 是 planner profile，不是 workflow profile

当前 profiles 更像任务规划策略：

- paper：偏向尽快投出 / 重投
- thesis：偏向保持主线不断线

建议 README 或 docs 中明确说明：v3.1 profiles 是 task planning profiles，不是完整流程替换器。

---

## 4. 🟢 做对的

1. 保持零依赖，未引入 Flask/FastAPI/React/Vue/Node/数据库。
2. 保持 `python3 src/app.py` 一条命令启动。
3. 保持本地运行。
4. 保持面板只读，未新增写接口。
5. 保持 v2 `.state.json` 兼容。
6. 未把 Agent 做成首页主角。
7. Daily Cockpit 默认入口已实现。
8. 今日任务最多 3 个已实现。
9. 最近完成与正反馈已实现。
10. 项目任务池已实现。
11. demo 数据覆盖 paper 与 thesis。
12. prompts 方向正确。
13. README 已指向 v3.1 文档。

---

## 5. 对照任务书第 10 节验收清单

| # | 验收项 | 结果 | 说明 |
|---:|---|---|---|
| 1 | `python3 src/app.py` 能启动 | ✅ | 基于代码判断，入口仍存在。 |
| 2 | 无第三方依赖 | ✅ | 仅使用 Python 标准库。 |
| 3 | demo 模式下默认进入“今日驾驶舱” | ✅ | 默认 view 为 cockpit。 |
| 4 | 首页最多显示 3 个今日任务 | ✅ | `selected_tasks[:3]` 已实现。 |
| 5 | 每个今日任务显示 why_today、starter、action、done_criteria | ✅ | 任务卡已显示核心字段。 |
| 6 | 首页显示最近完成或正反馈 | ✅ | recent_wins 与 done_log 已展示。 |
| 7 | 没有 today.json 时优雅降级，不报错 | ✅ | configured=false 空态已实现。 |
| 8 | 每个项目可以显示 tasks.json 中的任务池 | ✅ | tasks.json 扫描与任务池 tab 已实现。 |
| 9 | v2 state.json 老项目仍能显示流程和文档库 | ✅ | 原状态总览与文档库逻辑保留。 |
| 10 | 文档库原有功能不破坏 | ✅ | 原 renderDocs/renderOneDoc 仍保留。 |
| 11 | 不新增 Agent 角色主 tab | ✅ | 主 tab 没有 Agent 展示页。 |
| 12 | 不把真实论文内容写进公开 demo | ✅ | 未发现真实论文内容或密钥。 |
| 13 | README 指向 v3.1 文档 | ✅ | 已指向方向图与任务书。 |

---

## 6. 安全结论

公开内容安全性基本通过：未发现真实论文、真实审稿意见、真实数据、密钥、密码、API key。

代码安全性需要修复：

```text
/api/file path traversal guard
HTML escaping for task data
```

这两项必须在接真实 `paper-vault` 前完成。

---

## 7. 下一步建议

下一步不要再做大改架构。请 Claude Code 做一个小而严谨的 hardening pass：

1. 修复 `safe_under_root()`。
2. 增加前端 `h()` HTML 转义函数。
3. 所有任务卡动态字段使用 `h()`。
4. 统一 demo 命名。
5. 更新 v2 文案为 v3.1。
6. 清理 `silent&&false`。
7. 补充 `dropped` 任务统计。
8. 运行基础检查并输出报告。

---

## 8. 最终判断

当前版本：

```text
自用预览：可以
接入真实 paper-vault：先修安全问题
开源推广：修完安全问题和命名一致性后再发布
```

一句话：

> v3.1 的方向和主体实现已经正确，下一轮重点不是加功能，而是做安全、命名和可维护性收口。
