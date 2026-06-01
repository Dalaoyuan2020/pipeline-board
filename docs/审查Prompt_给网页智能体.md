# 审查 Prompt · 驱动网页智能体审查 pipeline-board v3.1

> 用法：把下面【===】之间整段，发给一个能联网/能读 GitHub 的智能体（ChatGPT 联网版 / Gemini / Claude 网页版等）。
> 仓库是公开的，无需授权即可读。

---

```
你是一名资深代码审查员 + 产品审查员。请联网打开并通读这个公开 GitHub 仓库，对它的 v3.1 改造做一次严格审查。

仓库：https://github.com/Dalaoyuan2020/pipeline-board

## 它是什么
pipeline-board 是一个【零依赖、纯 Python 标准库、本地运行】的科研进度面板，一条命令 `python3 src/app.py` 启动。v3.1 把它从"科研状态看板"升级为"Daily Research Cockpit（今日科研驾驶舱）"——打开第一眼就告诉用户今天只做 1–3 件事、怎么启动、做到什么算完成。

## 必读文件
1. `docs/CC_一键执行任务书_Daily_Cockpit_v3_1.md` —— 这是本次改造的【验收准则/任务书】，审查请以它为标准
2. `src/app.py` —— 唯一主程序（后端 http.server + 内嵌 HTML/CSS/JS 前端）
3. `demo/` —— 自带 demo 假数据（projects/ + state/ + planner/today.json + done_log.json）
4. `profiles/paper.json`、`profiles/thesis.json` —— 按类别的任务策略
5. `prompts/` —— 3 个任务生成 prompt
6. `README.md`

## 请逐项审查并给结论（对照任务书第 10 节验收清单）
A. **边界合规**：是否真零依赖（只用 Python 标准库，无 Flask/FastAPI/React/Node/数据库）？是否保持 `python3 src/app.py` 一条命令启动？是否保持 v2 的 .state.json 兼容？面板是否只读（不在网页写回内容库）？
B. **功能落地**（不是只写文档）：
   - 首页是否默认进入"今日驾驶舱"，最多显示 3 个今日任务？
   - 每个今日任务卡是否包含 why_today / starter / action / done_criteria 四个字段？
   - `/api/tree` 是否返回 projects / flow / today / done_log（+ profiles）？
   - 项目页是否新增"任务池"tab，展示 todo/doing/done/blocked？
   - 没有 today.json 时是否优雅降级（不报错）？
C. **代码质量**：路径配置（环境变量 RP_PROJ_ROOT/RP_STATE_DIR/RP_PLANNER_DIR）是否合理？JSON 读取是否有异常兜底（坏文件不崩服务）？有无路径越界风险（/api/file）？前端 onclick 参数是否转义？有无明显 bug / 边界漏洞。
D. **安全**：公开仓库里是否混入了真实密钥、密码、或真实论文内容（应该只有 demo 假数据）？
E. **反过度工程**：有没有违背"零依赖/只读/不做 Agent 展示页主角"的地方？

## 输出要求
- 🔴 必须修的问题（带文件名/大致位置 + 为什么 + 怎么改）
- 🟡 建议改的
- 🟢 做对的（简短）
- 对照任务书第 10 节 13 条验收清单，逐条打 ✅/❌ 并说明
- 一句话总评：这次 v3.1 改造是否达标、能否投入自用
只读审查，不要帮我改代码，给出可执行的审查意见即可。
```

---
*2026-06-01 · 给网页智能体的审查 prompt*
