# CC 一键执行任务书：pipeline-board v3.1 Daily Research Cockpit

> 这是给 Claude Code / Cloud Code / Coding Agent 使用的**最高优先级执行说明**。如果本仓库内其他 v3 文档强调 Agent 面板、Gate 面板或 Evidence 面板，请把它们视为长期蓝图；本任务书才是 v3.1 MVP 的执行准则。

目标：把当前 `pipeline-board` 从“科研状态看板”增量升级为“Daily Research Cockpit”：每天打开后，优先告诉用户**今天只做哪 1–3 件事、怎么启动、做到什么算完成、最近已经完成了什么**。

---

## 0. 核心判断

当前系统已经能回答：

```text
这个项目现在在哪个阶段？
有哪些文档？
每个阶段有哪些子步骤？
```

v3.1 必须优先回答：

```text
今天只需要推进哪一小步？
这个任务怎么启动？
做到什么程度就算完成？
如果一个项目很久没动，怎样用低压力方式重新启动？
最近已经完成了哪些任务，如何形成正反馈？
```

因此：

```text
To-do 优先于 Agent
行动优先于信息
启动任务优先于大目标
首页优先于复杂功能页
正反馈优先于压力提醒
```

---

## 1. 不可破坏的边界

必须保留：

1. 纯 Python 标准库，零第三方依赖。
2. 一条命令启动：`python3 src/app.py`。
3. 本地运行，默认端口 `8771`。
4. 继续通过环境变量读取外部内容库：
   - `RP_PROJ_ROOT` 指向内容库的 `projects/`
   - `RP_STATE_DIR` 指向内容库的 `state/`
5. 公开仓库只放系统、模板、demo、prompt，不能放真实论文内容。
6. v2 的 `.state.json` 必须继续兼容。
7. 第一阶段只读展示，不在网页里写回真实内容库。
8. 不引入 Flask / FastAPI / React / Vue / Node / 数据库。
9. 不把 Agent 做成首页主角，不做“Agent 展示秀”。Agent 只作为任务生成 prompt 或外部 CLI 工作流。

---

## 2. 当前系统事实

当前 `src/app.py` 是一个单文件应用：

- Python `http.server` 提供本地服务。
- `FLOW` 写死在 `app.py` 中。
- `scan_projects()` 扫描 `PROJ_ROOT`。
- `load_state(name)` 读取 `STATE_DIR/<项目名>.state.json`。
- `/api/tree` 返回 `{projects, flow}`。
- 前端内嵌在 `HTML` 字符串中。
- 当前前端主要有两个 tab：
  - `📋 状态总览`
  - `📂 文档库`

改造方式必须是**增量改造**，不要重写成新框架。

---

## 3. v3.1 新增数据层

### 3.1 内容根目录推断

因为真实内容库结构通常是：

```text
paper-vault/
  state/
  projects/
  thesis/
  planner/
```

而 demo 结构是：

```text
demo/
  state/
  projects/
  planner/
```

请在后端新增：

```python
CONTENT_ROOT = os.path.dirname(os.path.realpath(STATE_DIR))
PLANNER_DIR = os.path.expanduser(os.environ.get("RP_PLANNER_DIR", os.path.join(CONTENT_ROOT, "planner")))
```

说明：

- 用户可用 `RP_PLANNER_DIR` 覆盖。
- 默认从 `STATE_DIR` 的父目录找到 `planner/`。
- 如果 `planner/` 不存在，系统仍然正常运行，只显示“暂无今日任务”。

### 3.2 项目任务池：`projects/<project>/tasks.json`

每个项目可以有自己的长期任务池：

```text
projects/<project_name>/tasks.json
```

Schema：

```json
{
  "project": "demo_paper",
  "updated_at": "2026-05-31",
  "tasks": [
    {
      "id": "rev-r1-002",
      "title": "完成某条审稿意见的回应草稿",
      "stage": "投稿发表",
      "substep": "跟进修回",
      "type": "revision",
      "status": "todo",
      "priority": "P0",
      "energy": "low",
      "size": "small",
      "role": "main",
      "starter": "打开 response.md，写下 3 句话，不要求完美。",
      "action": "写出该意见的回应草稿。",
      "done_criteria": "该意见有回应、有修改位置、有下一步判断。",
      "why": "该任务最接近投稿/重投产出。",
      "blocker": "不确定是否需要补实验。",
      "source": "manual_or_agent",
      "created_at": "2026-05-31",
      "updated_at": "2026-05-31"
    }
  ]
}
```

字段要求：

- `id`：必需，项目内唯一。
- `title`：必需。
- `status`：`todo / doing / done / blocked / dropped`，缺省为 `todo`。
- `priority`：`P0 / P1 / P2 / P3`，缺省 `P2`。
- `starter`：强烈建议有。没有时前端显示“暂无启动动作”。
- `done_criteria`：强烈建议有。没有时前端显示“暂无完成标准”。
- `energy`：`low / medium / high`，用于注意力友好排序。

### 3.3 今日任务：`planner/today.json`

全局今日任务由外部 Agent / CLI / 人工确认后写入，面板只读：

```json
{
  "date": "2026-05-31",
  "mode": "low_pressure",
  "message": "今天只推进 1–3 件事。完成启动动作也算推进。",
  "selected_tasks": [
    {
      "project": "demo_paper",
      "task_id": "rev-r1-002",
      "role": "main",
      "why_today": "最接近投出，且可以拆成一个低阻力动作。"
    },
    {
      "project": "demo_thesis",
      "task_id": "thesis-concept-001",
      "role": "fallback",
      "why_today": "保持大论文主线不断线。"
    }
  ],
  "recent_wins": [
    "已完成一个改稿任务拆解。",
    "已整理一个补实验清单。"
  ]
}
```

显示规则：

- 首页最多显示 3 个 selected_tasks。
- 如果超过 3 个，只显示前 3 个，并提示“其余任务已隐藏，避免过载”。
- role 建议：`main / secondary / fallback / experiment / thesis`。
- `why_today` 必须展示。

### 3.4 完成记录：`planner/done_log.json`

用于正反馈：

```json
[
  {
    "date": "2026-05-31",
    "project": "demo_paper",
    "task_id": "rev-r1-002",
    "result": "done",
    "note": "完成回应草稿第一版。"
  }
]
```

前端只展示最近 3–5 条，不做复杂统计。

---

## 4. 后端实现任务

### 4.1 新增安全 JSON 读取函数

新增：

```python
def read_json(path, default):
    try:
        if os.path.isfile(path):
            return json.load(open(path, encoding="utf-8"))
    except Exception:
        pass
    return default
```

### 4.2 扫描项目时读取 tasks.json

在 `scan_projects()` 中，每个项目增加：

```python
tasks_obj = read_json(os.path.join(pdir, "tasks.json"), {"tasks": []})
tasks = tasks_obj.get("tasks", []) if isinstance(tasks_obj, dict) else []
```

为 project 增加字段：

```python
"tasks": tasks,
"task_counts": {
  "todo": n,
  "doing": n,
  "done": n,
  "blocked": n
}
```

注意：

- 没有 tasks.json 时，`tasks=[]`。
- tasks.json 坏了不能导致服务崩溃。
- 不要读取项目外路径。

### 4.3 读取 today.json 和 done_log.json

新增：

```python
def load_today(projects):
    today = read_json(os.path.join(PLANNER_DIR, "today.json"), {})
    # 若没有 today.json，返回 fallback 结构
    # 不写文件，只返回提示。
    return normalize_today(today, projects)


def load_done_log():
    log = read_json(os.path.join(PLANNER_DIR, "done_log.json"), [])
    return log if isinstance(log, list) else []
```

`normalize_today(today, projects)` 的行为：

- 如果 today 为空：
  - 返回 `{configured:false, message:"暂无今日任务。可在 planner/today.json 中添加。", selected_tasks:[], recent_wins:[]}`。
- 如果 today 有 selected_tasks：
  - 根据 project + task_id 从项目任务池中补全任务详情。
  - 找不到任务时仍显示占位，不报错。

### 4.4 修改 `/api/tree`

从：

```python
{"projects": scan_projects(), "flow": FLOW}
```

改为：

```python
projects = scan_projects()
self._s(200, json.dumps({
  "projects": projects,
  "flow": FLOW,
  "today": load_today(projects),
  "done_log": load_done_log()[-20:]
}, ensure_ascii=False))
```

---

## 5. 前端实现任务

### 5.1 首页新增 Daily Cockpit

当前默认页是 README。v3.1 要新增一个默认入口：

```text
🚀 今日驾驶舱
```

左侧栏顶部顺序建议：

```text
🚀 今日驾驶舱
📖 功能介绍
项目列表...
```

启动后默认显示今日驾驶舱，而不是 README。

### 5.2 新增全局状态变量

前端新增：

```javascript
let mode='cockpit'; // cockpit / readme / project
```

也可以复用现有 `cur=null` 逻辑，但要能区分 cockpit 与 readme。

### 5.3 新增 renderCockpit()

首页结构：

```text
标题：今日科研驾驶舱
副标题：今天只推进 1–3 件事。完成启动任务也算推进。

主任务区：
  - role = main 的任务
次任务区：
  - role = secondary / experiment / thesis
保底任务区：
  - role = fallback
最近完成：
  - today.recent_wins + done_log 最近记录
当前卡住：
  - 从项目 tasks 中找 blocked 或长期未动提示
项目任务概览：
  - 每类项目 todo/doing/blocked 统计
```

### 5.4 今日任务卡片字段

每张任务卡必须显示：

```text
项目名
任务标题
为什么今天做 why_today / why
最小启动 starter
实际动作 action
完成标准 done_criteria
优先级 priority
能量 energy
状态 status
```

低压力文案：

```text
完成“最小启动”也算推进。
不要求完美，先让任务重新动起来。
```

### 5.5 新增项目任务池 tab

项目详情 tab 从：

```text
📋 状态总览
📂 文档库
```

扩展为：

```text
📋 状态总览
✅ 任务池
📂 文档库
```

`✅ 任务池` 页面显示：

- todo
- doing
- blocked
- done 最近项

每个任务展示 starter、done_criteria、blocker。

### 5.6 不做 Agent 主界面

不要新增“Agent 角色”主 tab。v3.1 可以在 README 或 prompt 文档中说明 Agent 是外部生成器，但主 UI 不展示 Agent 角色卡。

---

## 6. Demo 数据要求

公开 demo 只能用假数据。

> ⚠️ 命名修订（2026-06-01 加固）：项目名必须用 `paper_*` / `thesis_*` 前缀，否则 `product_line()` 会把它归到"其他"且 profile 失效。故 demo 项目实际命名为 `paper_demo_cockpit` / `thesis_demo_cockpit`（不是 `demo_paper_*`），下表已按实现校正。

新增或复用 demo 项目：

```text
demo/projects/paper_demo_cockpit/tasks.json
demo/projects/thesis_demo_cockpit/tasks.json
demo/state/paper_demo_cockpit.state.json
demo/state/thesis_demo_cockpit.state.json
demo/planner/today.json
demo/planner/done_log.json
```

### 6.1 paper_demo_cockpit/tasks.json

至少包含 4 个任务：

1. 一个 `revision` 类型 P0 主任务。
2. 一个 `writing` 类型 P1 任务。
3. 一个 `experiment` 类型任务。
4. 一个 `blocked` 任务。

每个任务必须有：

```text
title / starter / action / done_criteria / why / status / priority / energy
```

### 6.2 thesis_demo_cockpit/tasks.json

至少包含 3 个任务：

1. 综述维护任务。
2. 框架定义任务。
3. 章节结构任务。

### 6.3 demo/planner/today.json

选 2 个任务：

```text
1 个 paper main task
1 个 thesis fallback task
```

---

## 7. Prompt 库要求

新增：

```text
prompts/daily_planner.md
prompts/revision_task_splitter.md
prompts/recovery_task_generator.md
```

### 7.1 daily_planner.md

用途：从所有项目 tasks.json 和 done_log 生成候选 today.json。

必须强调：

- 今日任务最多 3 个。
- 优先选择最接近投出/重投的任务。
- 同时考虑需要提前启动的实验任务。
- 每周保留 1–2 次大论文维护任务。
- 每个任务必须有 starter。
- 输出 JSON，不要输出散文。

### 7.2 revision_task_splitter.md

用途：把审稿意见拆成任务池。

必须输出：

```text
Milestone
Action Task
Starter Task
done_criteria
blocker
priority
```

### 7.3 recovery_task_generator.md

用途：长期未动项目生成低压力恢复任务。

要求：

- 任务 5–10 分钟可完成。
- 不批评用户。
- 不要求完整产出。
- 只帮助重新接触项目。

---

## 8. README 更新

README 新增 v3.1 简短说明：

```markdown
## v3.1：Daily Research Cockpit

`pipeline-board` 正在从科研状态看板升级为注意力友好的科研驾驶舱：
- 今日 1–3 个任务
- 任务飞轮：大目标 → 小动作 → 启动任务
- 最近完成与正反馈
- 长期未动项目的低压力恢复任务
- Agent/Prompt 只用于生成任务，面板保持只读展示

详细见：
- docs/方向图_从看板到科研驾驶舱.md
- docs/CC_一键执行任务书_Daily_Cockpit_v3_1.md
```

不要删除原 README 内容。

---

## 9. 开发顺序

请严格按顺序做：

### Step 1：数据读取

- 增加 `PLANNER_DIR`。
- 增加 `read_json()`。
- 读取每项目 `tasks.json`。
- 读取 `planner/today.json`。
- 读取 `planner/done_log.json`。
- `/api/tree` 返回 today 和 done_log。

验收：访问 `/api/tree` 能看到 `today`、`done_log`、每个 project 的 `tasks`。

### Step 2：Daily Cockpit 首页

- 新增 `🚀 今日驾驶舱`。
- 默认显示 cockpit。
- 渲染今日任务卡。
- 显示 recent_wins / done_log。

验收：打开首页第一眼能看到 1–3 个今日任务。

### Step 3：项目任务池页

- 新增项目 tab：`✅ 任务池`。
- 显示 todo/doing/blocked/done。
- 每个任务显示 starter 和 done_criteria。

验收：进入 demo paper 项目能看到任务池。

### Step 4：Demo 数据

- 新增 demo paper / thesis tasks。
- 新增 demo planner today 和 done_log。

验收：零配置启动即可看到 cockpit 效果。

### Step 5：Prompt 库

- 新增 3 个 prompt 文件。
- Prompt 只生成 JSON，不写真实仓库。

验收：用户可复制 prompt 给外部 Agent 生成 today.json/tasks.json。

### Step 6：README 更新

- 加 v3.1 说明。
- 保留原功能介绍。

---

## 10. 验收清单

完成后必须满足：

- [ ] `python3 src/app.py` 能启动。
- [ ] 无第三方依赖。
- [ ] demo 模式下默认进入“今日驾驶舱”。
- [ ] 首页最多显示 3 个今日任务。
- [ ] 每个今日任务显示：why_today、starter、action、done_criteria。
- [ ] 首页显示最近完成或正反馈。
- [ ] 没有 today.json 时优雅降级，不报错。
- [ ] 每个项目可以显示 tasks.json 中的任务池。
- [ ] v2 state.json 老项目仍能显示流程和文档库。
- [ ] 文档库原有功能不破坏。
- [ ] 不新增 Agent 角色主 tab。
- [ ] 不把真实论文内容写进公开 demo。
- [ ] README 指向 v3.1 文档。

---

## 11. 反跑偏规则

如果实现过程中想做以下事情，请先停止：

```text
做 Agent 展示页
做复杂多用户系统
接数据库
接外部 API
做网页编辑写回
做自动投稿/自动审稿
把论文真实内容放进 demo
把每日任务显示成 10 个以上
```

v3.1 的成功标准只有一个：

> 用户打开面板后，不是看到一堆信息，而是立刻知道今天从哪个最小动作开始。

---

## 12. 最终产品体验

目标体验：

```text
我打开 pipeline-board。
它告诉我：今天只做 2 件事。
每件事都有最小启动动作。
完成启动动作也算推进。
它提醒我最近已经完成过一些任务。
它不让我被整篇论文压垮，而是让我重新启动科研飞轮。
```
