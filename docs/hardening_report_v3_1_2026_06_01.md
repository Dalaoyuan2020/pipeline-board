# v3.1 Daily Cockpit 加固报告（Hardening Pass）

> 2026-06-01 · 依据 `docs/review_v3_1_daily_cockpit_2026_06_01.md` 的审查意见执行
> 范围：仅 src/app.py + demo + docs + README，未碰其他文件。面板保持只读、零依赖。

## 1. 改动摘要（Summary of changes）

### 🔴 必修（2 项）
1. **路径越界判断加固** `src/app.py safe_under_root()`
   - `startswith()` 前缀判断 → `os.path.commonpath([root,target])==root`，并 try/except ValueError。
   - 防住 `/x/projects` 与 `/x/projects_bak` 同前缀绕过。
2. **前端 HTML 转义防注入** `src/app.py`
   - 新增 `h()` 转义函数（& < > " ' 五字符）。
   - `taskCard / poolCard / renderCockpit / renderTaskPool` 所有动态字段（title/starter/action/done_criteria/blocker/why/why_today/project_title/stage/substep/priority/status/done_log/recent_wins/blocked 等）全部用 `h()` 包裹。
   - 同时把这几个函数内部的字符串构造局部变量从 `h` 改名为 `o`，避免与全局 `h()` 转义函数冲突。
   - `q()`（onclick 参数转义）与 `h()`（HTML 内容转义）职责分离、不互替。

### 🟡 建议（已采纳）
3. demo 命名对齐：**采用方案 B**（保留 `paper_demo_cockpit`/`thesis_demo_cockpit`，校正任务书路径表述）。
   - ⚠️ 未采纳审查的"方案 A 改名 demo_paper_cockpit"——因为 `demo_` 前缀会让 `product_line()` 归到"其他"且 profile 失效。方案 B 保前缀正确、profile 生效，更安全。
4. v2 文案 → v3.1：文件头注释 + 启动日志 `🔬 科研流水线 v3.1 Daily Cockpit`。
5. 清理死代码：`if(!(silent&&false))renderCockpit()` → `renderCockpit()`。
6. `task_counts` 增加 `dropped` 统计。
7. README 开头纳入"今日科研驾驶舱"定位 + 说明 profiles 是 task planning profiles（非 workflow 替换器）。

## 2. 验收清单报告（Checklist）

| # | 项 | 结果 | 验证方式 |
|---|---|---|---|
| 必修1 | 路径越界用 commonpath | ✅ | 单测：合法=True / ../=False / 同前缀_bak=False |
| 必修2 | HTML 转义 h() 防 XSS | ✅ | 注入 `<img src=x onerror=alert(1)>` → 转义为 `&lt;img...` 文本，不执行 |
| 必修3 | demo 命名一致 | ✅ | 方案B：实现与任务书表述已对齐，profile 仍生效 |
| 1 | python3 src/app.py 启动 | ✅ | HTTP 200 |
| 2 | 零依赖 | ✅ | 非标准库 import = 无 |
| 3 | 默认进今日驾驶舱 | ✅ | view 默认 cockpit |
| 4 | 今日最多 3 任务 | ✅ | selected_tasks=2(≤3) |
| 5 | 任务卡 why_today/starter/action/done_criteria | ✅ | 四字段齐全 |
| 6 | 最近完成/正反馈 | ✅ | recent_wins+done_log 展示 |
| 7 | 无 today.json 优雅降级 | ✅ | 真实库 configured=false 不报错 |
| 8 | 项目任务池 | ✅ | 2 项目有 tasks，含状态计数 |
| 9 | v2 state.json 兼容 | ✅ | 真实 10 项目正常加载 |
| 10 | 文档库不破坏 | ✅ | renderDocs/renderOneDoc 未动 |
| 11 | 不新增 Agent 主 tab | ✅ | 无 agent 主 tab |
| 12 | demo 无真实内容/密钥 | ✅ | XSS 测试后已还原，无残留 |
| 13 | README 指向 v3.1 | ✅ | 已含 v3.1 章节+定位 |
| 附 | task_counts 含 dropped | ✅ | API 返回含 dropped |
| 附 | profile 绑定 | ✅ | paper/thesis 各正确绑定 |

## 3. 验证步骤与结果（Verification）
- 语法：`python3 -m ast` 通过；提取 JS 用 `node --check` 通过。
- 路径越界单测：合法 True / `../` False / 同前缀 `_bak` False。
- XSS 注入测试：临时注入 `<img onerror>`/`<script>` 到 demo title/starter → `h()` 转义为纯文本 → 测试后已还原 demo（确认无残留）。
- 功能 API：/api/tree 五字段齐全、今日 2 任务四字段全、任务池 2 项目、profile 绑定、task_counts 含 dropped。
- 兼容：真实内容库（10 个 v2 项目、无 planner）→ 优雅降级 configured=false、项目正常。

## 4. Review 就绪声明
以上 13 条验收 + 3 项必修 + 附加项全部 ✅。改动限定在 src/app.py + demo + docs + README，面板只读、零依赖未破坏。**分支可进入 review。**
