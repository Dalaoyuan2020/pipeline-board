# pipeline-board v3 改造方案：Harness 化科研流水线 + 多角色质控

> 目标：在不破坏 `pipeline-board` 当前“零依赖、本地运行、播放器/片库解耦”优势的前提下，把它从一个科研进度面板，升级为一个 **Harness 化科研工作台**：能区分小论文/大论文模板，能显示多角色 Agent 的职责与质控建议，能按阶段设目标门禁，最终支持自进化式科研流程迭代。

版本：v3 规划草案  
日期：2026-05-31  
适用仓库：`Dalaoyuan2020/pipeline-board`  
不包含真实论文内容；真实内容仍放在 `paper-vault`。

---

## 1. 当前面板的判断

当前 `pipeline-board` 已经具备三个很好的底座：

1. **架构干净**：纯 Python 标准库，`python3 src/app.py` 一条命令启动；HTML/CSS/JS 内嵌，无构建步骤。
2. **定位正确**：它不是文件浏览器，而是“流程/状态驱动”的科研进度面板。
3. **播放器/片库解耦**：面板通过 `RP_PROJ_ROOT` 和 `RP_STATE_DIR` 指向外部内容库；公开仓库不含真实论文内容。

但它目前仍然偏“看板 v2”，还不是“科研流水线系统 v3”。主要缺口如下：

| 当前情况 | 问题 | v3 目标 |
|---|---|---|
| `FLOW` 写死在 `src/app.py` | 只有一套流程，难以区分小论文/大论文/专利/项目报告 | 引入 workflow profile，不同项目类型加载不同模板 |
| 只有 4 状态 + 10 子步骤 | 适合小论文 MVP，但不够支撑博论主线 | 增加小论文模板、大论文模板、项目报告模板 |
| 只有状态和文档 | 缺少“目标、质控、风险、下一步” | 每阶段加入 Gate、Metric、Risk、Next Action |
| 没有 Agent 角色 | 不能体现科研专业分工 | 增加多角色 Agent 面板：查新、怀疑者、实验设计、结果分析、期刊策略、模拟审稿等 |
| 文档库能看文件，但没有证据链 | 写作阶段容易变成普通文档聚合 | 引入 Claims-Evidence Map 的状态字段与显示区 |
| 模板设置还是占位 | 不能真正选择模板 | 实装模板/工作流配置页 |
| 只读浏览 | 很稳，但不能形成闭环 | 先只读展示 v3 元数据，后续再加可写模式 |

---

## 2. 产品方向：不是把面板做复杂，而是把它做成“科研 Harness”

这里的 Harness 不是简单 UI，而是一套把科研过程“套住、驱动、校验、复盘”的机制。

v3 的核心公式：

```text
Research Harness = Workflow Profile + Stage Gates + Agent Roles + Evidence Map + Version Log
```

具体含义：

- **Workflow Profile**：不同类型项目使用不同流程模板，例如小论文、大论文、专利、项目报告。
- **Stage Gates**：每个阶段有“能不能进入下一阶段”的检查清单。
- **Agent Roles**：每个阶段有专业角色负责质控，例如 Novelty Scout、Skeptic、Experiment Designer、Reviewer Agent。
- **Evidence Map**：论文里的 claim 要能回到实验结果、文献、图表、数据版本。
- **Version Log**：每次重要推进都留下“为什么改、改了什么、下一步是什么”。

原则：**公开仓库仍然只是播放器，不保存真实论文内容；真实内容、具体审稿意见、论文稿件、实验结果仍在 paper-vault。**

---

## 3. v3 应该保留的边界

为了不把一个好用的小工具做崩，v3 要坚持以下边界：

1. **继续零第三方依赖**：不引入 Flask、FastAPI、React、Vue、数据库。
2. **继续本地运行**：默认 `127.0.0.1:8771`。
3. **继续只读优先**：第一阶段只展示 v3 数据，不急着在界面写回文件。
4. **继续兼容 v2 state.json**：老字段 `current / blocks / substeps / substep_docs / note` 继续可用。
5. **继续内容解耦**：`pipeline-board` 只放模板、demo 和系统代码；`paper-vault` 放真实内容。
6. **Agent 不假装自动科研**：v3 初期的 Agent 是“角色卡 + 质控清单 + Prompt 模板 + 输入输出 artifact”，不是联网自动执行机器人。

---

## 4. v3 数据模型建议

### 4.1 保持 v2 字段不变

老项目继续可用：

```json
{
  "title_cn": "论文标题",
  "summary": "一句话概况",
  "current": "选题立项",
  "blocks": {"选题立项":"doing","实验执行":"todo","成文":"todo","投稿发表":"todo"},
  "substeps": {"Idea":"done","验证创新性":"doing"},
  "substep_docs": {"Idea":"stages/1_idea/standard.md"},
  "note": "当前备注"
}
```

### 4.2 增加 v3 可选字段

v3 state.json 可以增加以下字段；没有也不报错：

```json
{
  "schema_version": "3.0",
  "profile": "paper",
  "title_cn": "示例小论文",
  "summary": "一句话概况",
  "current": "实验执行",
  "blocks": {},
  "substeps": {},
  "substep_docs": {},
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
        {"name": "完成查新矩阵", "status": "done", "evidence": "stages/2_novelty/novelty_report.md"},
        {"name": "明确最小可发表贡献", "status": "doing", "evidence": "stages/3_charter/research_charter.md"}
      ]
    }
  },
  "agents": {
    "Novelty Scout": {
      "stage": "选题立项",
      "status": "active",
      "role": "查新、相似工作对比、创新性风险识别",
      "input": ["idea.md", "seed_papers.bib"],
      "output": ["novelty_report.md", "prior_art_matrix.md"],
      "prompt": "请基于 idea 和种子论文生成 prior art matrix，并判断 Go/Pivot/Drop。"
    },
    "Skeptic": {
      "stage": "选题立项",
      "status": "todo",
      "role": "从最严格审稿人角度攻击研究问题",
      "input": ["research_charter.md"],
      "output": ["skeptic_review.md"],
      "prompt": "请指出该研究最可能被拒稿的 5 个理由，并给出补救策略。"
    }
  },
  "risks": [
    {"level": "high", "stage": "实验执行", "text": "外部验证数据集不足", "owner": "Experiment Designer"}
  ],
  "next_actions": [
    {"priority": "P0", "text": "补充外部验证实验", "stage": "实验执行", "due": ""}
  ],
  "claim_evidence": [
    {
      "claim": "方法在目标场景上优于 baseline",
      "evidence": ["results/main_table.csv", "figures/ablation.png"],
      "confidence": "medium",
      "risk": "仅在单一数据集验证"
    }
  ]
}
```

---

## 5. Workflow Profile 设计

v3 不建议再把 `FLOW` 写死在 `app.py`。建议新增：

```text
profiles/
  paper.json       # 小论文模板
  thesis.json      # 大论文/博士论文模板
  patent.json      # 专利模板，可后做
  report.json      # 项目报告模板，可后做
```

后端逻辑：

```text
1. 启动时读取 profiles/*.json。
2. 每个项目根据 state.profile 决定使用哪个 profile。
3. 如果没有 state.profile，则用文件夹前缀推断：paper_* → paper，thesis*/phd* → thesis。
4. 如果 profile 文件不存在，则回退到内置 DEFAULT_FLOW，保证老项目不坏。
```

---

## 6. 小论文模板 paper.json 建议

小论文保持 4 大状态，但子步骤要比 v2 更科研化：

```json
{
  "key": "paper",
  "name": "小论文模板",
  "description": "适用于 SCI/EI/中文核心/会议论文，从 idea 到投稿修稿。",
  "flow": [
    {
      "key": "选题立项",
      "goal": "确认 idea 是否值得做，并形成 Research Charter。",
      "subs": [
        {"name": "Idea", "tpl": ["一句话问题", "目标对象/场景", "初始假设", "预期贡献"]},
        {"name": "查新与创新性", "tpl": ["种子论文", "Prior Art Matrix", "相似工作威胁等级", "Go/Pivot/Drop"]},
        {"name": "Research Charter", "tpl": ["研究问题", "核心假设", "最小可发表贡献", "风险与 Plan B"]},
        {"name": "设计实验", "tpl": ["数据集", "baseline", "评价指标", "消融", "统计检验", "失败标准"]}
      ],
      "agents": ["Idea Structuring", "Novelty Scout", "Skeptic", "Experiment Designer"],
      "gate": ["查新矩阵完成", "创新点明确", "实验资源可用", "最小可发表贡献成立"]
    },
    {
      "key": "实验执行",
      "goal": "完成可复现实验并判断结果是否支撑论文。",
      "subs": [
        {"name": "数据与代码准备", "tpl": ["数据版本", "代码 commit", "环境文件", "随机种子"]},
        {"name": "跑实验", "tpl": ["主实验", "baseline", "ablation", "robustness", "外部验证"]},
        {"name": "评估结果", "tpl": ["主指标", "显著性", "失败案例", "结果强度", "补实验清单"]}
      ],
      "agents": ["Execution Logger", "Result Analyst", "Reproducibility Checker"],
      "gate": ["实验日志完整", "结果表可追溯", "关键图表生成", "补实验决策明确"]
    },
    {
      "key": "成文",
      "goal": "把结果转化为有证据支撑的论文稿。",
      "subs": [
        {"name": "期刊策略", "tpl": ["候选期刊", "scope fit", "风险", "冲刺/稳妥/保底"]},
        {"name": "Claims-Evidence Map", "tpl": ["claim", "支持证据", "反证/风险", "置信度"]},
        {"name": "写稿", "tpl": ["Title", "Abstract", "Introduction", "Methods", "Results", "Discussion", "Limitations"]},
        {"name": "模拟审稿", "tpl": ["Editor", "Novelty", "Methods", "Statistics", "Harsh Reviewer", "修改计划"]}
      ],
      "agents": ["Journal Strategist", "Manuscript Agent", "Reviewer Agent", "Claim-Evidence Auditor"],
      "gate": ["目标期刊明确", "claim 均有证据", "图表完整", "模拟审稿通过"]
    },
    {
      "key": "投稿发表",
      "goal": "完成投稿、修稿、回应和归档复盘。",
      "subs": [
        {"name": "投稿包", "tpl": ["manuscript", "cover letter", "highlights", "data availability", "ethics", "supplement"]},
        {"name": "投稿", "tpl": ["投稿系统", "推荐/回避审稿人", "提交时间", "状态记录"]},
        {"name": "跟进修回", "tpl": ["decision letter", "逐条回应", "补实验", "修改位置"]},
        {"name": "归档复盘", "tpl": ["接收/拒稿原因", "可复用材料", "下一篇论文启发"]}
      ],
      "agents": ["Submission Manager", "Revision Agent", "Postmortem Agent"],
      "gate": ["投稿包齐全", "AI 使用声明检查", "审稿意见逐条回应", "版本归档"]
    }
  ]
}
```

---

## 7. 大论文模板 thesis.json 建议

大论文不是“小论文放大版”，它需要主线、框架、章节、案例群和答辩闭环。

```json
{
  "key": "thesis",
  "name": "博士/硕士论文模板",
  "description": "适用于博士论文、硕士论文，从主线立项到答辩归档。",
  "flow": [
    {
      "key": "主线立项",
      "goal": "确定博士论文的总问题、总框架和论文群映射。",
      "subs": [
        {"name": "总问题", "tpl": ["研究对象", "核心矛盾", "为什么不是普通应用论文集合"]},
        {"name": "Harness 框架", "tpl": ["Prompt→Context→Harness", "工业 AI 场景", "框架定义", "边界"]},
        {"name": "论文群映射", "tpl": ["每篇小论文对应章节", "各自贡献", "共同主线", "缺口"]},
        {"name": "博士贡献声明", "tpl": ["理论贡献", "方法贡献", "工程贡献", "应用贡献"]}
      ],
      "agents": ["Thesis Architect", "Skeptic", "Contribution Assessor"],
      "gate": ["总问题成立", "Harness 框架能统领论文群", "章节映射完整"]
    },
    {
      "key": "综述与框架",
      "goal": "完成第一章/第二章综述、概念定义和理论框架。",
      "subs": [
        {"name": "文献地图", "tpl": ["Prompt", "Context", "Harness", "AI Agent", "无监督异常检测", "工业视觉"]},
        {"name": "综述初稿", "tpl": ["研究脉络", "代表工作", "不足", "博士切入点"]},
        {"name": "框架章节", "tpl": ["概念定义", "系统结构", "工作流", "评价维度"]},
        {"name": "概念核验", "tpl": ["术语是否自洽", "是否有引用支撑", "是否过度造概念"]}
      ],
      "agents": ["Literature Curator", "Concept Auditor", "Chapter Reviewer"],
      "gate": ["关键文献核验", "概念定义稳定", "综述能导向 Harness 框架"]
    },
    {
      "key": "案例与章节",
      "goal": "把多篇小论文转化为博士论文章节，并强化共同主线。",
      "subs": [
        {"name": "Case 1", "tpl": ["对应小论文", "工业视觉问题", "Harness 要素", "章节贡献"]},
        {"name": "Case 2", "tpl": ["对应小论文", "方法/数据/系统", "与主线关系"]},
        {"name": "Case 3", "tpl": ["对应小论文", "异常检测或数据合成", "与框架关系"]},
        {"name": "跨案例综合", "tpl": ["共性规律", "差异对比", "框架验证", "局限性"]}
      ],
      "agents": ["Case Integrator", "Evidence Auditor", "Thesis Reviewer"],
      "gate": ["每章不是简单贴小论文", "跨案例综合成立", "证据链完整"]
    },
    {
      "key": "统稿答辩",
      "goal": "完成整本论文一致性、格式、预答辩和最终归档。",
      "subs": [
        {"name": "统稿", "tpl": ["术语统一", "图表统一", "章节衔接", "摘要结论"]},
        {"name": "预答辩", "tpl": ["专家问题", "薄弱章节", "修改清单"]},
        {"name": "终稿", "tpl": ["格式检查", "查重", "盲审材料", "数据/代码归档"]},
        {"name": "答辩归档", "tpl": ["答辩记录", "最终版本", "成果清单", "后续论文计划"]}
      ],
      "agents": ["Defense Reviewer", "Format Checker", "Final Auditor"],
      "gate": ["主线一致", "格式达标", "预答辩问题关闭", "归档完成"]
    }
  ]
}
```

---

## 8. 多角色 Agent 设计

v3 的 Agent 先作为“角色卡/质控卡”进入面板，不需要真的自动联网或调用模型。每个 Agent 卡片显示：

```text
角色名
所属阶段
当前状态：todo / active / done / blocked
职责
输入材料
输出材料
建议 Prompt
最近风险
下一步动作
```

建议角色库：

| Agent | 适用阶段 | 职责 |
|---|---|---|
| Idea Structuring | 选题立项 | 把模糊想法结构化为研究问题、假设、贡献候选 |
| Novelty Scout | 选题立项 | 查新、相似工作矩阵、创新性判断 |
| Skeptic | 全阶段 | 按最严格审稿人角度攻击方案 |
| Experiment Designer | 选题立项/实验执行 | 设计主实验、baseline、消融、统计检验 |
| Execution Logger | 实验执行 | 记录数据、代码、参数、环境、日志 |
| Result Analyst | 实验执行 | 判断结果强度、失败原因、补实验建议 |
| Reproducibility Checker | 实验执行 | 检查数据版本、代码 commit、随机种子、环境 |
| Journal Strategist | 成文 | 匹配期刊/会议，评估 scope fit 与风险 |
| Manuscript Agent | 成文 | 生成大纲、段落、图表说明、cover letter |
| Claim-Evidence Auditor | 成文 | 检查每个 claim 是否有证据支撑 |
| Reviewer Agent | 成文/投稿 | 模拟 editor、novelty、methods、statistics、harsh reviewer |
| Revision Agent | 投稿发表 | 拆解审稿意见，生成逐条回复和修稿任务 |
| Thesis Architect | 大论文 | 维护博士论文主线、章节结构、论文群映射 |
| Literature Curator | 大论文 | 维护综述文献地图和概念演化线索 |
| Chapter Reviewer | 大论文 | 检查章节逻辑、术语一致性、贡献闭合 |
| Defense Reviewer | 大论文 | 模拟预答辩/盲审专家问题 |

---

## 9. UI 改造建议

当前 UI 只有两个主 tab：状态总览、文档库。v3 建议扩展为：

```text
📋 状态总览
🧭 阶段门禁
🤖 Agent 角色
🧾 证据链
📂 文档库
⚙ 模板设置
```

### 9.1 状态总览升级

新增内容：

- 项目类型徽章：小论文 / 大论文 / 专利 / 项目报告
- 当前 profile：paper / thesis / patent / report
- 评分卡：创新性、可行性、证据强度、投稿成熟度；大论文则为主线清晰度、综述完整度、章节成熟度、答辩风险。
- 下一步建议卡：读取 `next_actions`。
- 高风险卡：读取 `risks`。

### 9.2 阶段门禁页

按阶段显示 Gate：

```text
阶段目标
通过条件
当前完成度
阻塞项
证据文件
是否允许进入下一阶段
```

### 9.3 Agent 角色页

左侧按阶段分组 Agent；右侧显示某个 Agent 的：

```text
Role
Input
Output
Prompt
Checklist
Risks
Next Action
```

### 9.4 证据链页

显示 `claim_evidence`：

```text
Claim | Evidence | Confidence | Risk | 是否可写入论文
```

这一步不需要解析真实文件，只先显示 state.json 中登记的路径。

### 9.5 模板设置页

原来的“模板·设置”占位变成真实可读页：

```text
当前项目使用模板：paper
可用模板：paper / thesis / patent / report
模板阶段结构预览
每个阶段的 Agent 与 Gate
如何在 state.json 中切换 profile
```

第一版仍然只读，不在网页写入。

---

## 10. 分阶段执行路线图

### M0：冻结当前 v2 基线

目标：确认当前 v2 能稳定运行，并把 v3 改造只作为增量。

任务：

- 保留 `src/app.py` 当前启动方式。
- 保留 README 中的“播放器/片库解耦”说明。
- 保留 v2 state.json 兼容。

验收：

- `python3 src/app.py` 仍可直接启动 demo。
- 不需要安装任何依赖。
- 老项目状态文件仍能正常显示。

---

### M1：Profile 引擎

目标：把硬编码 `FLOW` 变成“内置默认 + profiles/*.json 可覆盖”。

任务：

1. 新增 `profiles/paper.json` 与 `profiles/thesis.json`。
2. 后端增加 `load_profiles()`。
3. 每个项目扫描时根据 `state.profile` 或项目名前缀推断 profile。
4. `/api/tree` 返回：

```json
{
  "projects": [],
  "profiles": {},
  "default_flow": []
}
```

5. 前端渲染某个项目时使用 `project.flow`，而不是全局 `DATA.flow`。

验收：

- paper 项目显示小论文流程。
- thesis/phd 项目显示大论文流程。
- 没有 profile 字段的老 state.json 仍能显示。
- 如果 profile 文件坏了，自动回退默认流程，不崩溃。

---

### M2：v3 状态字段展示

目标：不改变写入逻辑，只把 `metrics / risks / next_actions / gates` 展示出来。

任务：

1. `scan_projects()` 继续原样透传 `state`。
2. 前端增加评分卡组件。
3. 状态总览页增加：
   - Metrics Cards
   - Risks Panel
   - Next Actions Panel
4. 新增 `renderGates(p)` 页面。

验收：

- v2 state 没有这些字段时不报错，显示“未配置”。
- v3 state 有字段时能正确显示。
- 风险颜色：high 红，medium 橙，low 蓝/灰。

---

### M3：小论文/大论文模板落地

目标：真正拥有两套模板。

任务：

1. `profiles/paper.json` 使用第 6 节小论文模板。
2. `profiles/thesis.json` 使用第 7 节大论文模板。
3. README 或功能介绍页说明：
   - 小论文是从 idea 到投稿修稿。
   - 大论文是从主线立项到统稿答辩。
4. Demo 中至少放一个 paper demo 和一个 thesis demo。

验收：

- 左侧类别中，小论文和硕博论文项目进入后流程不同。
- 小论文仍显示 4 大状态。
- 大论文显示“主线立项 → 综述与框架 → 案例与章节 → 统稿答辩”。

---

### M4：Agent 角色面板

目标：把“多角色科研质控”变成看得见的系统能力。

任务：

1. 新增 tab：`🤖 Agent 角色`。
2. 从 `state.agents` 和 `profile.flow[].agents` 合并显示角色。
3. 如果 state 里没有 agent 详情，则用 profile 里的默认角色生成占位卡。
4. 每个 Agent 卡片显示：职责、输入、输出、Prompt、状态、风险。

验收：

- 小论文项目能看到 Novelty Scout、Skeptic、Experiment Designer、Reviewer Agent 等。
- 大论文项目能看到 Thesis Architect、Literature Curator、Chapter Reviewer 等。
- 不需要真实 AI API；只是面板角色化。

---

### M5：证据链页

目标：让面板从“文档浏览”升级为“论文 claim 质控”。

任务：

1. 新增 tab：`🧾 证据链`。
2. 读取 `state.claim_evidence`。
3. 表格显示：Claim、Evidence、Confidence、Risk、Can Write。
4. 如果证据路径对应文件存在，可以做成可点击打开文档库；第一版可先只显示路径。

验收：

- 能一眼看到哪些 claim 证据不足。
- 没有 `claim_evidence` 时提示如何在 state.json 中添加。

---

### M6：自进化机制

目标：让系统不是固定模板，而是可以根据复盘逐步优化流程。

建议新增可选文件：

```text
meta/process_log.json
meta/lessons_learned.json
```

示例：

```json
[
  {
    "date": "2026-05-31",
    "project": "paper_sr_ddpm",
    "stage": "投稿发表",
    "event": "IJABE 改稿卡住",
    "lesson": "投稿阶段需要把审稿意见拆成任务，而不是只写 note。",
    "template_change_suggestion": "投稿发表阶段增加 Revision Task Board。"
  }
]
```

面板显示：

```text
最近流程复盘
常见阻塞原因
建议更新模板
```

验收：

- 面板能显示流程复盘。
- 不自动修改模板，只给建议。
- 用户确认后再人工更新 profile。

---

### M7：可写模式，可后做

目标：从只读面板变成轻量工作台。

建议通过环境变量显式开启：

```bash
export RP_WRITE=1
python3 src/app.py
```

可写功能包括：

- 更新子步骤状态。
- 添加 next_action。
- 添加 risk。
- 添加 agent note。
- 生成 state.json skeleton。

默认仍然只读，避免误改 `paper-vault`。

---

## 11. 最小实现顺序建议

最稳的执行顺序：

```text
第一步：M1 Profile 引擎
第二步：M3 小论文/大论文模板
第三步：M2 Metrics/Gates/Risks/Next Actions 展示
第四步：M4 Agent 角色面板
第五步：M5 证据链页
第六步：M6 自进化复盘
第七步：M7 可写模式
```

不要一上来就做可写、自动生成、联网查新或 LLM API。先把“科研专业性”变成数据结构和可视化。

---

## 12. 推荐的 v3 页面结构

最终用户看到的是：

```text
左侧：项目列表
  - 功能介绍
  - 小论文
  - 硕博论文
  - 专利
  - 项目报告

顶部：项目名 / 类型 / 当前阶段 / profile / 自动刷新

主 Tab：
  📋 状态总览
  🧭 阶段门禁
  🤖 Agent 角色
  🧾 证据链
  📂 文档库
  ⚙ 模板设置
```

---

## 13. 对吕志远当前科研盘子的直接意义

### 对 5 篇小论文

每篇小论文都可以用 `paper` profile 管理：

- SR-DDPM：重点在“投稿发表 / 跟进修回 / Revision Agent”。
- 墒情预测 BiLSTM：重点在“投稿发表 / 跟进修回 / 审稿意见拆解”。
- 群体番茄：重点在“实验执行 / 补 3.4 实验”和“成文 / 译英投稿”。
- RevUnsup：重点在“实验执行 / 跑实验 / 评估结果”。
- 双向变换：重点在“选题立项 / 查新与创新性 / Research Charter”。

### 对博士论文

博士论文使用 `thesis` profile：

- 主线立项：Harness Engineering for Industrial AI 是否能统领所有 case。
- 综述与框架：Prompt→Context→Harness、AI Agent、无监督异常检测三条线是否闭合。
- 案例与章节：每篇小论文如何变成博士论文章节，而不是简单拼盘。
- 统稿答辩：术语统一、贡献闭合、盲审风险、答辩问题。

---

## 14. 本方案的核心结论

`pipeline-board` 不应该变成“大而全 AI 写论文平台”。它最适合成为：

> 一个零依赖、本地运行、内容解耦的 **科研 Harness 播放器**。

它负责把真实科研内容组织成：

```text
项目 → 模板 → 阶段 → 子步骤 → Gate → Agent → Evidence → Next Action
```

这样它既保持轻量，又能逐渐长出科研专业性；既适合个人博士生自用，也适合作为开源科研流程工具发布。
