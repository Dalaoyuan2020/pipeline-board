# 科研流水线 · v3 Harness Agent 改造 Prompt

> 用法：把本文交给 coding agent。详细设计见 `docs/面板改造方案_Harness_Agent_v3.md`。本 Prompt 的目标是把现有 `pipeline-board` 从“科研进度面板 v2”增量升级为“科研 Harness 播放器 v3”。

---

## 1. 改造目标

在现有仓库基础上改造，不要推翻重写。保留这些原则：

- 纯 Python 标准库，零第三方依赖。
- 一条命令启动：`python3 src/app.py`。
- 本地运行，默认 `127.0.0.1:8771`。
- 继续通过 `RP_PROJ_ROOT`、`RP_STATE_DIR` 读取外部内容库。
- `pipeline-board` 只做播放器，不放真实论文内容。
- 兼容 v2 的 `.state.json`。
- v3 第一阶段只做只读展示，不做网页写回。

v3 的核心结构：

```text
项目 → Profile 模板 → 阶段 → 子步骤 → Gate 门禁 → Agent 角色 → Evidence 证据链 → Next Action
```

---

## 2. 新增文件

新增：

```text
profiles/paper.json
profiles/thesis.json
```

可选新增 demo：

```text
demo/state/demo_paper_harness.state.json
demo/state/demo_thesis_harness.state.json
demo/projects/demo_paper_harness/
demo/projects/demo_thesis_harness/
```

---

## 3. Profile 模板

### 3.1 paper.json：小论文模板

小论文流程仍是 4 个阶段，但子步骤升级为：

```text
选题立项：Idea / 查新与创新性 / Research Charter / 设计实验
实验执行：数据与代码准备 / 跑实验 / 评估结果
成文：期刊策略 / Claims-Evidence Map / 写稿 / 模拟审稿
投稿发表：投稿包 / 投稿 / 跟进修回 / 归档复盘
```

每个阶段带：

```json
{
  "goal": "阶段目标",
  "subs": [{"name":"子步骤名", "tpl":["模板要点"]}],
  "agents": ["Agent 名称"],
  "gate": ["通过条件"]
}
```

推荐 Agent：

```text
Idea Structuring
Novelty Scout
Skeptic
Experiment Designer
Execution Logger
Result Analyst
Reproducibility Checker
Journal Strategist
Manuscript Agent
Claim-Evidence Auditor
Reviewer Agent
Submission Manager
Revision Agent
Postmortem Agent
```

### 3.2 thesis.json：大论文模板

大论文不是小论文放大版，流程应为：

```text
主线立项：总问题 / Harness 框架 / 论文群映射 / 博士贡献声明
综述与框架：文献地图 / 综述初稿 / 框架章节 / 概念核验
案例与章节：Case 1 / Case 2 / Case 3 / 跨案例综合
统稿答辩：统稿 / 预答辩 / 终稿 / 答辩归档
```

推荐 Agent：

```text
Thesis Architect
Literature Curator
Concept Auditor
Case Integrator
Evidence Auditor
Chapter Reviewer
Defense Reviewer
Format Checker
Final Auditor
```

---

## 4. 后端改造

在 `src/app.py` 中保留现有 `FLOW` 作为默认回退，同时新增 profile 加载。

新增常量：

```python
PROFILE_DIR = os.path.normpath(os.path.join(_HERE, "..", "profiles"))
```

新增函数：

```python
def load_profiles():
    profiles = {}
    if os.path.isdir(PROFILE_DIR):
        for fn in os.listdir(PROFILE_DIR):
            if not fn.endswith(".json"):
                continue
            try:
                obj = json.load(open(os.path.join(PROFILE_DIR, fn), encoding="utf-8"))
                key = obj.get("key") or os.path.splitext(fn)[0]
                profiles[key] = obj
            except Exception:
                pass
    return profiles


def infer_profile(name, state):
    if state.get("profile"):
        return state.get("profile")
    if name.startswith(("thesis", "phd")) or "博论" in name:
        return "thesis"
    if name.startswith("paper_"):
        return "paper"
    return "paper"
```

修改 `scan_projects()`：

- 读取 state 后推断 profile。
- 给每个 project 增加字段：

```json
{
  "profile": "paper",
  "profile_name": "小论文模板",
  "flow": [],
  "metric_labels": {}
}
```

修改 `/api/tree` 返回：

```json
{
  "projects": [],
  "flow": [],
  "profiles": {}
}
```

---

## 5. v3 state.json 可选字段

继续支持 v2 字段：

```text
title_cn / summary / current / blocks / substeps / substep_docs / note
```

新增可选字段：

```json
{
  "schema_version": "3.0",
  "profile": "paper",
  "metrics": {
    "novelty": 82,
    "feasibility": 76,
    "evidence": 68,
    "readiness": 54
  },
  "gates": {
    "选题立项": {
      "goal": "确认 idea 值得进入实验",
      "status": "pass",
      "criteria": [
        {"name":"完成查新矩阵", "status":"done", "evidence":"stages/novelty.md"}
      ]
    }
  },
  "agents": {
    "Novelty Scout": {
      "stage": "选题立项",
      "status": "active",
      "role": "查新、相似工作对比、创新性风险识别",
      "input": ["idea.md"],
      "output": ["novelty_report.md"],
      "prompt": "生成 prior art matrix，并判断 Go/Pivot/Drop。"
    }
  },
  "risks": [
    {"level":"high", "stage":"实验执行", "text":"外部验证数据集不足", "owner":"Experiment Designer"}
  ],
  "next_actions": [
    {"priority":"P0", "text":"补充外部验证实验", "stage":"实验执行", "due":""}
  ],
  "claim_evidence": [
    {"claim":"方法优于 baseline", "evidence":["results/main.csv"], "confidence":"medium", "risk":"单数据集验证", "can_write":false}
  ]
}
```

所有新增字段缺失时必须优雅降级。

---

## 6. 前端改造

### 6.1 主 Tab

把原来的两个 tab 扩展为：

```text
📋 状态总览
🧭 阶段门禁
🤖 Agent 角色
🧾 证据链
📂 文档库
⚙ 模板设置
```

### 6.2 项目级 flow

新增：

```javascript
function flowOf(p){ return p.flow || DATA.flow || []; }
```

所有和流程相关的渲染优先使用 `flowOf(p)`，不要只用全局 `DATA.flow`。

### 6.3 状态总览升级

在总览页增加：

- 当前模板：paper / thesis。
- 评分卡：读取 `state.metrics`。
- 下一步行动：读取 `state.next_actions`。
- 风险卡：读取 `state.risks`。

没有字段时显示“未配置”，不要报错。

### 6.4 阶段门禁页

新增 `renderGates(p)`：

- 优先显示 `state.gates`。
- 如果没有，则显示 profile 中每个阶段的默认 `gate`。
- 每个阶段显示 goal、criteria、status、evidence。

### 6.5 Agent 角色页

新增 `renderAgents(p)`：

- 合并 profile 默认 agents 和 `state.agents` 详情。
- 卡片显示：角色名、阶段、状态、职责、输入、输出、Prompt。
- 没配置详情时显示默认占位说明。

### 6.6 证据链页

新增 `renderEvidence(p)`：

表格显示：

```text
Claim | Evidence | Confidence | Risk | Can Write
```

空数据时提示用户在 state.json 中添加 `claim_evidence`。

### 6.7 模板设置页

新增 `renderTemplateSettings(p)`：

显示：

- 当前 profile。
- 模板名称和说明。
- 阶段结构预览。
- 每个阶段的 agents 和 gate。
- 如何在 state.json 中切换 profile。

第一版只读，不写入文件。

---

## 7. README 更新

在 README 追加一节：

```markdown
## v3 规划：Harness Agent

`pipeline-board` 正在从单一小论文流程面板升级为 Harness 化科研工作台：
- 小论文/大论文 profile 模板
- 阶段门禁 Gate
- 多角色 Agent 质控卡
- Claims-Evidence 证据链
- 自进化流程复盘

详细见：
- docs/面板改造方案_Harness_Agent_v3.md
- docs/系统生成_prompt_v3_Harness_Agent.md
```

---

## 8. 验收标准

完成后必须满足：

1. `python3 src/app.py` 能启动。
2. 浏览器打开 `http://localhost:8771` 不报 JS 错误。
3. v2 state.json 老项目仍显示正常。
4. paper 项目显示小论文流程。
5. thesis/phd 项目显示大论文流程。
6. 状态总览显示 profile、metrics、risks、next_actions。
7. 阶段门禁页能显示默认 gate 和 state.gates。
8. Agent 页能显示默认 Agent 和 state.agents 详情。
9. 证据链页能显示 claim_evidence。
10. 文档库仍可按阶段归类并打开文本文件。
11. 没有新增第三方依赖。

---

## 9. 禁止事项

- 不引入 Flask/FastAPI/React/Vue。
- 不把真实论文内容写进公开仓库。
- 不改变默认启动命令。
- 不强制用户连接云服务。
- 默认不写回 `paper-vault`。
- 不把 Agent 包装成虚假的自动投稿或自动审稿功能；第一版只是角色、Prompt、质控清单和状态展示。

---

## 10. 推荐提交顺序

```text
1. profiles/paper.json、profiles/thesis.json
2. 后端 profile 加载与项目级 flow
3. 前端流程渲染改为项目级 flow
4. 新增阶段门禁 / Agent / 证据链 / 模板设置 tab
5. 总览页增加 metrics / risks / next_actions
6. 新增 v3 demo
7. 更新 README
8. 本地运行验证
```
