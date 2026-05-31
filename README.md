# 🔬 科研流水线 · Research Pipeline Board

一个**零依赖、本地运行**的科研进度面板：把论文 / 专利 / 学位论文从「想法 → 实验 → 成文 → 投稿」的全流程，做成一眼看清状态的看板。一条命令 `python3 src/app.py` 启动，浏览器访问 `localhost:8771`。

> 设计理念：**流程 / 状态驱动**，不是文件浏览器。进入一个项目先看它"在流程哪一步"，文件是末端内容。

## v3.1：Daily Research Cockpit

`pipeline-board` 正在从科研状态看板升级为注意力友好的科研驾驶舱：
- 今日 1–3 个任务（打开第一眼就知道"今天从哪个最小动作开始"）
- 任务飞轮：大目标 → 小动作 → 启动任务（完成"最小启动"也算推进）
- 最近完成与正反馈
- 长期未动项目的低压力恢复任务
- 每个项目有自己的任务池 `projects/<项目>/tasks.json`
- 今日任务来自 `planner/today.json`，完成记录 `planner/done_log.json`
- Agent / Prompt 只用于**生成**任务（见 `prompts/`），面板保持**只读展示**

详细见：
- `docs/方向图_从看板到科研驾驶舱.md`
- `docs/CC_一键执行任务书_Daily_Cockpit_v3_1.md`

## 特性
- 三级下钻：4 状态（选题立项→实验执行→成文→投稿发表）→ 子步骤 → 标准文档
- 文档库：归纳整理版（按阶段自动归类源文件 + 未归类兜底）/ 原始素材 / 模板设置
- 日间 / 夜间主题，每 5 秒自动刷新，自定义滚动条
- 纯 Python 标准库，零第三方依赖，可 PyInstaller 打包

## 快速开始（零配置，看 demo）
```bash
python3 src/app.py      # 直接跑，读 demo/ 里的示例项目
```
打开 http://localhost:8771 即可看到示例论文的进度面板。

## 接入你自己的内容
面板与内容**完全解耦**（像播放器与片库）。把环境变量指向你的内容库即可：
```bash
export RP_PROJ_ROOT="$HOME/你的内容库/projects"   # 每个项目一个文件夹
export RP_STATE_DIR="$HOME/你的内容库/state"       # 每项目一个 <名>.state.json
python3 src/app.py
```
或复制 `run_local.sh.example` 为 `run_local.sh` 改路径后 `bash run_local.sh`。

## 数据模型
- 项目 = 一个文件夹；文件夹名前缀定类别（paper_=小论文 / thesis_/phd_=硕博论文 / patent=专利 / projectbook_/report_=项目报告）
- 每项目一个 `<名>.state.json`：title_cn / summary / current / blocks(4状态) / substeps(子步骤) / substep_docs / note
- 源文件放进项目下的阶段文件夹（如 `选题立项/`）会被自动归类

## 许可
MIT
