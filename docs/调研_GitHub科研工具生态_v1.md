> 2026-06-01 · 动态工作流(5 agent 并行联网调研)产出 · 给 pipeline-board 吸收用
> ⚠️ star/URL 部分标注待核实，正式引用前请核对

# pipeline-board 科研开源生态调研报告

## 1. 一句话结论

科研开源生态当前呈"三流派割裂"格局——知识管理流(academic-obsidian/Logseq 强文献互链但无流程看板)、企业课题管理流(Study Tracker 有单一事实来源但重、不个人友好)、通用看板流(Focalboard 已停维,证明纯通用 Kanban 缺科研语义会被抛弃);同时 AI 科研 Agent 全自动流水线井喷(GPT Researcher/STORM/AI Scientist 各 1-3 万 star),但它们都是"端到端跑完一篇论文",几乎没有"Agent 只生成结构化任务、本地面板只读消费"的轻量驾驶舱。**pipeline-board 的差异化定位正落在这三流派的交集空白处:本地优先零依赖(参考 Kanri 单 .json)+ 科研专属可回流状态机(参考 Leantime"想法→实验→成文→投稿")+ 论文/实验/审稿意见实体建模(参考 academic-obsidian + van den Burg GitHub Issues 改稿法),并以"注意力友好的今日飞轮"为冲击力主线。**

## 2. 最值得关注的竞品 Top 7

| 项目 | URL | star | 它强在哪 | 我们能学什么 | 我们已有的优势 |
|---|---|---|---|---|---|
| Leantime | github.com/Leantime/leantime | ~10k | 把"注意力友好"做成产品主线,显式 Built with ADHD in mind;跑通想法→Lean Canvas→目标(常驻可见)→执行→复盘状态流 | 整条状态流照搬并科研垂直化;"目标始终在视线内"的注意力设计 | 我们更轻(零依赖本地),且状态机是科研专属可回流(投稿被拒→改投),非通用目标 |
| Super Productivity | github.com/super-productivity/super-productivity | ~19.8k | Focus Mode 启动计时即收缩成"只剩当前这一件";金句"ADHD brains lose what they cannot see";每日 metrics 动量面板 | Focus Mode 单焦点交互直接抄;外部信号自动拉进任务流的飞轮机制 | 我们是科研垂直语义,且"Agent 生成+面板只读"解耦,不做全功能 PM |
| AppFlowy | github.com/AppFlowy-IO/AppFlowy | ~50k+(待核实) | 同一份结构化数据按 status 字段自动分组,Grid↔Kanban↔Calendar 多视图切换(database-view 架构) | "一份数据多视图"是流程状态驱动的标准做法,直接采用 | 我们的状态机是科研流程(可回流),且本地 JSON 零部署 |
| Kanri | github.com/kanriapp/kanri | ~1.9k | 单 .json 文件存全部看板=零延迟+数据主权;"do one thing well"极简哲学 | 本地优先工程范本:存储/导入导出(Trello/GitHub Project) | 我们叠加了科研状态流+今日飞轮,不只是空白 Kanban |
| GPT Researcher | github.com/assafelovic/gpt-researcher | ~27k | planner/executor 分离:planner 只产出"研究问题清单"这份结构化数据,executor 才消费 | 印证"Agent 只生成、面板只读"解耦正确;splitter 先列子问题/里程碑再二次拆 task 更稳 | 我们的结构化产物落地为可 diff 的本地 tasks.json,被 agent 反复读写 |
| van den Burg GitHub Issues 改稿法 | gertjanvandenburg.com/blog/github_paper_revision | N/A(方法论) | 一条审稿意见=一个 issue,label=章节,milestone=投稿轮次;JOSS"审稿即 issue"佐证 | ★直击痛点的现成数据模型,论文项目应内建 | 我们把它做成本地看板卡(原文/已改/回复 reviewer 三态),不依赖 GitHub |
| RefChecker | github.com/markrussinovich/refchecker | ~377 | 三段式引文核实流水线(确定性预过滤→LLM深度网搜→再核实),输出 LIKELY/UNCERTAIN/UNLIKELY 三档 | 引文核验做成可重跑任务卡,每条引用一个状态徽章;对接 S2/CrossRef/OpenAlex | 我们把它落成 tasks.json 里的结构化 todo,契合"一切落成可执行任务" |

补充值得留意:**ADHD-Focus**(~60 star,理念密度高)、**HabitTrove**(~2k 待核实,heatmap+streak)、**Manubot**(~472,论文当软件项目管)、**AI-Research-SKILLs**(~9.1k,research-state.yaml 持久工作区)。

## 3. 可吸收清单(按优先级)

### P0 — 直接服务 v3.2"驾驶舱冲击力 + 数据飞轮",优先做

- **★ Super Productivity Focus Mode → 单一焦点首屏**:启动即隐藏其余任务列表,只剩当前这一件。落到 v3.2 驾驶舱首屏默认只显示"现在做什么",全列表需主动展开。(冲击力主线)
- **★ HabitTrove heatmap + streak → 动量飞轮可视化**:GitHub 贡献格子式热力图 + 连击计数器。落到 v3.2"连续推进天数/每日投入热力图",把坚持变成看得见的资产。(飞轮主线)
- **★ ADHD-Focus 小额高频脉冲 → 完成即正反馈**:避免一次性大奖,每次勾选完成给即时微反馈(动效/计数+1/解锁)。落到 v3.2 任务完成交互。(飞轮主线)
- **★ van den Burg / JOSS issue 改稿模型 → 论文项目数据模型**:一条审稿意见=一张卡,label=章节,milestone=投稿轮次,卡上固定三态字段(原文/已改/给 reviewer 的回复)。落到论文项目核心数据结构。

### P1 — 强化核心理念与 prompt 层,近期做

- **Leantime"想法→画布→目标→执行→复盘"→ 科研垂直状态流**:把通用目标换成"想法→实验→成文→投稿",目标/截稿日永远可见。落到 board 状态机定义。
- **AppFlowy database-view → 一份数据多视图**:同一 tasks.json 按 status 字段自动分组成看板列,支持 Kanban/Calendar 切换。落到面板渲染层。
- **STORM Perspective-Guided + GPT Researcher 两段式 → splitter/daily_planner prompt 升级**:生成任务前先让 Agent 列"审稿人/导师/答辩委员三视角关心点",再据此拆任务;先列里程碑/子问题再拆 action,比一步到位稳。落到 revision_task_splitter、daily_planner prompt。
- **tududi"不跟你对着干"+ now/next/later → 低压力恢复基调**:Today/Upcoming/Someday 时间分层,接得住断点重启。落到 v3.2 设计哲学 + 时间分层视图。
- **RefChecker + BibGuard + doi2bib → citation_check 独立 prompt**:"生成→核实→修复建议→人工确认"可重跑任务流,每条引用一个状态徽章。落到投稿/成文阶段一个 prompt,拆成结构化 todo 写进 tasks.json。

### P2 — 锦上添花,有余力再做

- **AI Scientist seed_ideas.json → few-shot 种子示例**:在 profiles/paper.json、thesis.json 放 2-3 条标杆 task 当 few-shot,统一 starter/action 粒度(尤其 starter 的"5-10 分钟最小动作"最易跑偏)。
- **AutoResearchClaw PROCEED/REFINE/PIVOT + HKUDS 评估维度 → 任务决策标签**:recovery_task_generator 给长期未动项目打"推进/调参/转向"标签;splitter 让 Agent 自评后过滤低质任务再落盘。
- **AI-Research-SKILLs research-state.yaml → 项目级 state 文件**:每个 projects/<项目> 放一个 state 文件给 Agent 读,生成任务时"带上下文"而非每次从零拆。
- **Paperlib scraper 插件化 + RefChecker 阶段化 → 可插拔采集/阶段节点**:不同来源(arXiv/无 DOI 会议/产线)各写一个采集器,但需克制,别变单体重构。
- **reviewer2 多阶段 LLM 链 → 审稿意见自动拆卡**:把收到的 reviewer comments 喂进 LLM 链,自动拆成逐条结构化任务卡(半自动化,人工确认)。
- **Elsevier-Tracker → 投稿状态看板列**:先做手动状态机(With Editor/Under Review/Major Revision/Accepted),多篇论文横向排,不硬接各家投稿系统。

## 4. 要避开的坑(反过度工程,呼应零依赖/只读原则)

1. **不做企业级重量集成**:Study Tracker(Java17+Spring Boot+PostgreSQL+OpenSearch+ELN/SharePoint/S3 集成)是"机构单一事实来源",重且不个人友好。我们坚持本地 JSON,不上数据库、不接外部系统。
2. **不做纯通用 Kanban**:Focalboard 已停维,证明无科研语义的通用看板会被抛弃。我们必须在看板之上叠加科研专属状态流+论文/实验/审稿语义才有立足点。
3. **不硬接各家投稿系统的爬虫**:Elsevier-Tracker 式爬虫脆弱易坏。投稿状态先做手动状态机看板,够用即止。
4. **不做端到端全自动科研流水线**:AI Scientist/AutoResearchClaw/AI-Researcher 都要 Docker 沙箱、GPU、多 Agent 辩论——重、贵、黑盒。我们只做"Agent 生成结构化任务、面板只读消费",把自动化留在 prompt 层而非系统层。
5. **不锁进黑盒数据库**:别学 Zotero SQLite 式存储。优先 Manubot/Papis 的 Git+明文(Markdown/YAML),可 diff、可被 agent 读写。
6. **不堆视图密度**:别学 Marvin 做成 50+ 策略的全功能 PM。WeekToDo 式"一屏看完、不滚动"的克制信息密度更对——让"今天聚焦"成为默认视图而非可选项。
7. **scraper/阶段插件化要克制**:插件化是好架构(Paperlib),但别为了"通用"过早抽象成单体框架,先硬编码够用的几个来源。

## 5. 差异化护城河(该坚持、别被带偏)

1. **本地优先零依赖 + 数据主权**:单 .json/明文文件存全部状态(参考 Kanri),零延迟、可 diff、可被 agent 直接读写。这是相对 Leantime(PHP+MySQL)、AppFlowy(Rust 部署)的根本轻量优势,别为了功能放弃零依赖。
2. **科研专属可回流状态机**:不是通用目标看板,而是"想法→实验→成文→投稿",且支持投稿被拒→改投→再投的**回流**(单向通用 Kanban 做不到)。这是相对所有通用工具的语义护城河。
3. **Agent 生成 / 面板只读的解耦**:tasks.json 作为唯一结构化中间产物,Agent 只写、面板只读——这一模式已被 GPT Researcher(planner/executor)、AI-Research-SKILLs(research-state.yaml)印证正确,是我们能蹭 AI 科研 Agent 红利又不背全自动流水线包袱的关键。坚持不动摇。
4. **审稿意见结构化为任务卡(三态)**:把 van den Burg/JOSS 的 issue 改稿范式做成本地原生的"一条意见=一张卡 + 原文/已改/回复三态",直击三篇论文修改投稿的真实痛点,且不依赖 GitHub。这是论文垂直场景里别人没做成产品的空白。
5. **注意力友好的今日飞轮**:Focus Mode 单焦点 + heatmap/streak 动量 + 小额高频正反馈 + 低压力断点恢复,四件套组合服务"科研常被打断"的真实节律。理念金句已被市场验证("ADHD brains lose what they cannot see"),我们把它垂直到科研驾驶舱,这是冲击力来源,别退化成又一个待办清单。