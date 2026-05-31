# pipeline-board v3.1 One-Click Prompt

> 用于 Claude Code (CC) 或其他 cloud code agent 自动执行 v3.1 改造。目标是将现有 `pipeline-board` 从单纯看板升级为**Daily Research Cockpit**，支持低压力任务飞轮、今日 To-do、完成反馈和恢复机制。

---

## 1. 当前问题总结

- 当前面板是可视化看板，显示论文状态、流程和文档，但不能真正推动行动。
- 用户需要：每天只做 1–3 个最小可执行任务；可快速启动；有完成标准和正反馈；长期未动任务自动生成低压力恢复任务。
- 小论文和大论文先独立管理，未来可映射到博士论文总控台。
- Agent 仅用于生成任务和拆解任务，不直接显示在主界面。

---

## 2. v3.1 核心目标

1. 每日 To-do：只显示 1–3 个任务。
2. 任务飞轮：Big Goal → Milestone → Action Task → Starter Task。
3. 正反馈机制：显示最近完成的任务，激励继续推进。
4. 卡住恢复机制：长期未动的任务生成 5–10 分钟低压力恢复任务。
5. 小论文优先投出，实验后台并行，博士论文每周维护。
6. 保持零依赖，保持只读模式，兼容 v2 state.json。

---

## 3. 文件结构改造

```text
profiles/
  paper.json
  thesis.json
prompts/
  daily_planner.md
  revision_task_splitter.md
  recovery_task_generator.md
demo/state/
  demo_paper_v3.1.state.json
  demo_thesis_v3.1.state.json
demo/projects/
  demo_paper_v3.1/
  demo_thesis_v3.1/
```

说明：
- `prompts/` 内存放生成任务的 Agent Prompt。
- `demo/` 目录只存假数据，展示流程。

---

## 4. 任务生成与今日 To-do

1. 读取每个项目的 `tasks.json`，生成任务池。
2. 根据完成情况生成 `today.json`：
   - 默认只选 1–3 个任务。
   - 每个任务包含 Starter Task + Action Task。
   - 每个任务有完成标准、最小启动动作、优先理由。
3. long-term tasks 保留在项目任务池中。

示例 today.json：
```json
{
  "date": "2026-05-31",
  "selected_tasks": [
    {"project":"SR-DDPM","task_id":"rev-r1-002","why_today":"最接近投出","starter":"打开 response.md，写 3 句话"},
    {"project":"thesis_demo","task_id":"thesis-concept-001","why_today":"保持主线","starter":"打开 outline.md，写 100 字"}
  ]
}
```

---

## 5. 任务飞轮原则

- **Big Goal**：整篇论文改稿或实验目标。
- **Milestone**：阶段任务，例如完成 Reviewer 1 的所有意见。
- **Action Task**：可执行的小任务，例如写回应某条意见。
- **Starter Task**：启动任务，例如打开文档或列 5 个修改点。
- 默认首页显示 Action + Starter Task，避免信息压力。

---

## 6. 恢复机制

- 对长期未动任务生成低压力恢复任务。
- 恢复任务可 5–10 分钟完成，不要求完整产出。
- 完成后自动触发任务池更新，生成新的今日 To-do。

---

## 7. Agent 使用规范

- Agent 仅生成任务和拆解任务。
- 输出写入 `tasks.json`、`today.json`、`done_log.json`。
- 面板只读展示这些结果。
- 不在首页显示角色卡片。

推荐 Agent Prompt：
```text
Daily Planner Agent
Revision Agent
Experiment Planner Agent
Paper Writing Agent
Thesis Maintenance Agent
Recovery Agent
```

---

## 8. CC 执行指南

1. 读取 `docs/pipeline-board_v3.1_oneclick_prompt.md`。
2. 按文件结构和任务规则生成或更新以下内容：
   - `profiles/paper.json` / `profiles/thesis.json`
   - demo project 的 `tasks.json` / `state.json`
   - `prompts/` 下的 Agent Prompt 文件
3. 更新前端，使首页显示每日 1–3 个任务，包含 Starter + Action Task。
4. 后端读取项目任务池，生成今日任务和完成记录。
5. 保证现有 v2 项目兼容，不破坏原始流程。
6. 提供 CLI 或 cloud code 一键运行，自动生成 `today.json`。

---

## 9. 验收标准

1. 首页显示今日 1–3 个任务。
2. 每个任务包含 Starter Task + Action Task + 完成标准 + why_today。
3. 长期未动任务生成低压力恢复任务。
4. 项目任务池显示所有任务状态（todo/doing/done/blocked）。
5. 小论文与大论文模板独立显示，未来可映射。
6. 兼容 v2 state.json，不破坏原有项目。
7. 零第三方依赖，纯 Python + HTML/CSS/JS。
8. 面板只读，Agent 可 CLI 或 cloud code 调用生成任务。

---

**用途**：将这个 prompt 给 CC 后，可自动更新仓库，将 `pipeline-board` 调整为 v3.1 Daily Research Cockpit 方向，实现低压力、可启动、可反馈、抗拖延的科研驾驶舱体验。