> 2026-06-01 · 编排-执行-评估三层动态工作流(17 agent: 8检索+8独立评估+1综合)产出
> 8 维度: 工作台/写作投稿/文献管理/科研绘图/数据分析复现/笔记知识管理/科研Agent/学术搜索
> ⚠️ star/URL 部分标注待核实(见第6节)，正式引用前请核对

I have all the research data and verdicts I need to write this report. No additional tools required.

# pipeline-board 科研开源生态调研报告

## 0. 方法说明

**三层分工。** 本报告由编排-执行-评估三层协作产出：编排层(产品负责人)拆出 8 个调研维度并界定 pipeline-board 的零依赖约束；执行层为每个维度做开源检索、提取代表项目、给出 borrow 分析；评估层为每个维度配独立评估员，逐项用 GitHub API / WebFetch 复核 URL 与 star 真实性，输出 confirmed / doubtful / missing 四类 verdict。本报告严格采纳评估层结论：doubtful 项标"待核实"，missing 项补入正文。

**8 个维度覆盖：** (1) 科研工作台开源生态；(2) 论文写作与投稿；(3) 文献管理与参考文献自动化；(4) 科研绘图与可视化；(5) 科研数据分析/可复现；(6) 科研笔记/知识管理；(7) 科研 Agent/AI 辅助科研；(8) 学术搜索/文献发现。

**可信度处理。** 评估员逐项核实结论是：90+ 个项目的 URL 全部真实存在，无幻觉/伪造仓库；star 量级抽样实测基本吻合；执行层对未核实数字诚实标注"待核实"而非编造。评估员也指出部分"待核实"标注过于保守(如 JabRef/Streamlit/dzhng-deep-research 实属可信高星)，以及若干 star 被低估或高估的偏差,这些在第 6 节统一列出。

---

## 1. 总览结论

**生态位空白真实存在。** 跨 8 个维度横扫后,结论高度一致:没有任何一个开源项目同时满足"科研语义 + 进度可视化 + 零部署纯本地"三要素。

- **电子实验记录本(ELN)** —— eLabFTW / SciNote / Chemotion —— 懂科研语义(实验/资源/数据库三类对象、project→experiment→task 层级),但极重:PHP/Ruby + MySQL/MongoDB + Docker,必须起 server。
- **自托管看板** —— Kanboard / Wekan / Focalboard / Taskcafe / Vikunja / Planka —— 交互成熟,但完全不懂科研(无选题/投稿/审稿/绘图概念),且仍需后端。
- **笔记/知识库** —— Logseq / SiYuan / Trilium / Foam / Obsidian+Dataview —— local-first 做得最好,但没有结构化的流程状态机/pipeline 概念。
- **PhD tracker 脚本** —— PhD_Thesis_Tracker / thesis-tracker —— 思路对(进度量化+发表状态机),但是个位数 star 的玩具。

**pipeline-board 差异化定位:** 把"看板的进度可视化 + ELN 的科研状态机(选题→实验→成文→投稿) + local-first 的零部署"三者合一,坚持纯前端/纯标准库单文件、双击 HTML 即用。这对没有运维能力的研究生/独立研究者是最大卖点。当前 v3.2"驾驶舱冲击力 Hero + 数据飞轮可视化"的规划方向,正对应跨维度反复出现的两个最强可吸收范式:**diagram-as-code 的状态机可视化** 与 **同一数据多视图(看板/表格/日历/甘特)**。

---

## 2. 八大维度全景

### 维度 1 · 科研工作台开源生态(workbench)
**该领域在做什么:** 四类生态——ELN(重后端、湿实验室)、通用看板(可改造但无科研语义)、笔记型(local-first)、PhD tracker(小而专)。

| 项目 | URL | star | 作用 |
|---|---|---|---|
| eLabFTW | github.com/elabftw/elabftw | 1.3k | 最流行开源 ELN,experiment/resource/database 三类对象模型 |
| SciNote | github.com/scinote-eln/scinote-web | 301 | project→experiment→task 三层结构 |
| Chemotion ELN | github.com/ComPlat/chemotion_ELN | ~180 | 化学专用 ELN,FAIR 数据原则 |
| Kanboard | github.com/kanboard/kanboard | 9.6k | 极简自托管看板,"刻意做减法"哲学 |
| Wekan | github.com/wekan/wekan | 21k | 成熟看板字段对照表 |
| Taskcafe | github.com/JordanKnott/taskcafe | 5.2k | React 看板前端实现参考 |
| Focalboard | github.com/mattermost/focalboard | 26.2k | 多视图(看板/表格/日历/画廊) ⚠️已停更 |
| Vikunja | github.com/go-vikunja/vikunja | 4.4k | 甘特图视图、单二进制轻量部署 |
| Logseq | github.com/logseq/logseq | 43.2k | local-first 纯文件、块引用双链 |
| Trilium/TriliumNext | github.com/TriliumNext/Trilium | 36.3k | 自定义 attributes 元数据、relation map |
| JabRef | github.com/JabRef/jabref | 4.3k | BibTeX 文献分组/阅读状态 |
| PhD_Thesis_Tracker | github.com/pvti/PhD_Thesis_Tracker | 5 | 进度量化+发表状态机(玩具,仅理念) |
| thesis-tracker | github.com/dsuess/thesis-tracker | ~0 | git hook 自动统计写作字数(玩具,仅理念) |
| Streamlit | github.com/streamlit/streamlit | 数万级 | 反面参照:需起 server,与零依赖相悖 |

**评估员备注:** 质量 high,14 项 URL 全真、star 抽样全吻合。两点时效提示:Focalboard 标准仓库已被官方标记"not maintained"(功能迁至 mattermost-plugin-boards),引用其设计仍有效但应注明已停更;zadam/trilium 已移交社区为 TriliumNext(最新 v0.103.0)。**missing(已补):** Obsidian+Dataview/Kanban 插件(当下最主流 local-first 学术工作流,本维度最大缺口)、Zotero(文献事实标准)、openBIS、Indigo ELN、Planka、AFFiNE(local-first 多视图一体,定位极近)、AnyType。JabRef/Streamlit 的"待核实"标注被评估员判定为多余(实测可信)。

### 维度 2 · 论文写作与投稿
**该领域在做什么:** 写作基座(Quarto/Typst/Manubot)、引文核实/规范化、投稿审稿意见管理与 revision tracker。

| 项目 | URL | star | 作用 |
|---|---|---|---|
| Quarto | github.com/quarto-dev/quarto-cli | 5.7k | 声明式 YAML 项目+单源多格式渲染 |
| Manubot | github.com/manubot/manubot | 472 | 按 DOI/PMID 解析引文并本地缓存 |
| Typst | github.com/typst/typst | 54k | Rust 单二进制、无 TeX 发行版依赖 |
| rebiber | github.com/yuchenlin/rebiber | 3.0k | 离线数据库规范化 .bib(纯 Python 轻量) |
| refchecker | github.com/markrussinovich/refchecker | 377 | 引文真实性核验,反 AI 幻觉假引文 |
| Zettlr | github.com/Zettlr/Zettlr | 13k | 引文一等公民+Pandoc 导出 |
| klb2/review-response-template | github.com/klb2/review-response-template | ~120 | 逐条审稿意见数据模型 |
| GjjvdBurg/LaTeXReviewReplyTemplate | github.com/GjjvdBurg/LaTeXReviewReplyTemplate | 16 | issue=意见/milestone=轮次/PR=改动 工作流 |
| penmaher/WRITE_with_git | github.com/penmaher/WRITE_with_git | 7 | latexdiff+git 着色改动可视化 |
| awesome-scientific-writing | github.com/writing-resources/awesome-scientific-writing | 944 | 写作全链路功能图谱 |
| awesome-LaTeX | github.com/egeerardyn/awesome-LaTeX | 1.6k | LaTeX 选型清单 |

**评估员备注:** 质量异常高,8 个高风险小众项目逐项 WebFetch 全部对得上(含 3/7/16 star 的项目),doubtful 为空,refchecker 正确归属 markrussinovich 而非混淆 amazon-science/RefChecker。**missing(已补):** latexdiff 本体(ftilmann/latexdiff,revision tracker 核心实现,被反复引用却未单列)、tectonic(自包含 Rust LaTeX 引擎,最契合零依赖却缺席)、git-latexdiff、pandoc(jgm/pandoc,整条工具链地基)、Better BibTeX、overleaf CE、GROBID、anystyle。

### 维度 3 · 文献管理 / 参考文献自动化
**该领域在做什么:** 文献库管理、DOI/arXiv→BibTeX 自动化、BibTeX 解析清理、citekey 生成。

| 项目 | URL | star | 作用 |
|---|---|---|---|
| Zotero | github.com/zotero/zotero | 14.3k | 文献事实标准,条目 schema+collection 双轴 |
| Better BibTeX | github.com/retorquere/zotero-better-bibtex | 6.7k | 稳定 citekey 生成公式+自动导出 .bib |
| JabRef | github.com/JabRef/jabref | 4.3k | 单一 .bib 真相源,在线 fetcher |
| Zotero Actions & Tags | github.com/windingwind/zotero-actions-tags | 2.7k | 事件触发→运行脚本 自动化范式 |
| Paperlib | github.com/Future-Scholars/paperlib | 2.2k | 本地驾驶舱+多源 scraper+插件(形态最近) |
| Papis | github.com/papis/papis | 1.7k | 一篇文献=目录+yaml,纯文件系统(范本) |
| bibtex-tidy | github.com/FlamingTempura/bibtex-tidy | 1.1k | 纯前端可跑的 .bib 清理去重 |
| doi2bib(davidagraf) | github.com/davidagraf/doi2bib | 121 | DOI content-negotiation 一次 HTTP 调用 |
| python-bibtexparser | github.com/sciunto-org/python-bibtexparser | 565 | .bib 读写事实标准库(v2 中间件化) |
| arxiv-sanity-lite | github.com/karpathy/arxiv-sanity-lite | 1.6k | 极简单文件本地科研驾驶舱精神范本 |
| doi2bib(mseri) | github.com/mseri/doi2bib | 72 | OCaml CLI,标识符→BibTeX |
| Pybtex | (官方在 GitLab/PyPI) | — | BibTeX 渲染引擎 ⚠️见待核实 |

**评估员备注:** 逐一用 GitHub API 核实全部项目,无编造。三处"待核实"偏保守——mseri/doi2bib(72)、arxiv-sanity-lite(1618)实属可信,应转 confirmed。唯一需保留警示:**Pybtex 的 live-clones/pybtex URL 仅 5 star、是镜像而非官方仓**,官方源现迁至 GitLab/PyPI,落地前必须改用官方源。**missing(已补):** obsidian-zotero-integration、citation-style-language/styles(CSL 样式事实标准,3829 star)、betterbib、citeproc/pandoc-citeproc(渲染引擎)、obsidian-citation-plugin。

### 维度 4 · 科研绘图与可视化
**该领域在做什么:** 绘图底座(matplotlib/seaborn)、期刊级样式、感知均匀/色盲安全 colormap、diagram-as-code 流程图。

| 项目 | URL | star | 作用 |
|---|---|---|---|
| matplotlib | github.com/matplotlib/matplotlib | ~21k | 绘图事实标准底座(理念参考,不引依赖) |
| seaborn | github.com/mwaskom/seaborn | 13.9k | 合理默认值+主题策略 |
| SciencePlots | github.com/garrettj403/SciencePlots | 8.9k | 出版级风格=可切换纯文本 .mplstyle(范式最贴切) |
| UltraPlot(ProPlot 继任) | github.com/Ultraplot/UltraPlot | 百级 | 多面板布局抽象 |
| CMasher | github.com/1313e/CMasher | 488 | 感知均匀+色盲友好色图(内嵌 RGB 数据) |
| colorcet | github.com/holoviz/colorcet | 742 | 感知均匀色图集 |
| cmcrameri | github.com/callumrollo/cmcrameri | 数百(待核实) | Crameri 科学色图(batlow/vik) |
| palettable | github.com/jiffyclub/palettable | ~693 | 纯 Python 零依赖调色板(最契合,可原样照搬模式) |
| PlotNeuralNet | github.com/HarisIqbal88/PlotNeuralNet | 24.8k | TikZ 网络图,diagram-as-code 思路 |
| mermaid | github.com/mermaid-js/mermaid | 88.4k | 文本声明→流程/状态/甘特图(流程图思路最值得借鉴) |
| schemdraw | github.com/cdelker/schemdraw | 1k+(待核实) | 链式 API 自动连线生成状态机图 |
| drawio-desktop | github.com/jgraph/drawio-desktop | 40k+(待核实) | local-first 图编辑器定位参照 |
| rougier/scientific-visualization-book | github.com/rougier/scientific-visualization-book | 1万+(待核实) | 出版级视觉规范知识库(字号/对比/色盲安全) |

**评估员备注:** 13 个核心项目均真实,研究者诚实标注未精确核实的 star。**doubtful:** UltraPlot 实际仅约百级 star(相比 ProPlot ~1.1k 偏小,属新兴)。**missing(已补):** plotly(~16k)、bokeh(~19k)、plotnine、altair、graphviz/pygraphviz(维度点名流程图却漏)、cmocean、**cmap(pyapp-kit/cmap,仅 numpy 依赖,与零依赖哲学最契合,明显该补)**、PGFPlots、matplotlib 内置 colormaps。

### 维度 5 · 科研数据分析 / 可复现
**该领域在做什么:** 数据/pipeline 版本化、实验跟踪、可复现 notebook、可复现出版、统计分析。

| 项目 | URL | star | 作用 |
|---|---|---|---|
| DVC | github.com/iterative/dvc | 15.6k | dvc.yaml 声明式 pipeline DAG+内容哈希复跑 |
| ydata-profiling | github.com/ydataai/ydata-profiling | 13.6k | 一行出自包含 HTML EDA 报告 |
| papermill | github.com/nteract/papermill | 6.4k | notebook 参数化批跑+产物留痕 |
| Aim | github.com/aimhubio/aim | 6.1k | 本地目录存 run+自带 UI 对比(本地优先) |
| Quarto | github.com/quarto-dev/quarto-cli | 5.7k | 可复现报告产出 |
| Jupyter Book | github.com/jupyter-book/jupyter-book | 4.2k | 多 notebook 组织成册 |
| Nextflow | github.com/nextflow-io/nextflow | ~3.4k | channel/process 数据流(重型,反面参照) |
| Snakemake | github.com/snakemake/snakemake | 2.8k | 文件依赖驱动+自动 DAG+只重算过期(核心可复刻) |
| ClearML | github.com/clearml/clearml | 6.7k | 实验+数据+编排一体(界定功能边界) |
| ZenML | github.com/zenml-io/zenml | 5.4k | @step/@pipeline 装饰器式低侵入 DAG |
| Sacred | github.com/IDSIA/sacred | 4.4k | 自动记录 config+种子+源码+环境(FileStorageObserver) |
| pingouin | github.com/raphaelvallat/pingouin | 1.9k | 统计检验带 effect size/CI/功效(可选引擎) |

**评估员备注:** 质量 high,12 项全真,三个原标"待核实"的 star 已核实(ClearML 6.7k/ZenML 5.4k/Sacred 4.4k)。DVC 归属确认为 iterative/dvc(treeverse 是 lakeFS,无关)。**missing(已补):** **MLflow(mlflow/mlflow,该维度实验跟踪事实标准,~18k,明显该作核心对照却完全缺席)**、wandb 客户端、Hydra(配置管理标杆)、Prefect(~17k)、Dagster(~12k)、Airflow、Great Expectations、Optuna(~11k)、statsmodels/SciPy.stats(pingouin 底层依赖,统计层核心)。

### 维度 6 · 科研笔记 / 知识管理
**该领域在做什么:** Zettelkasten/双链、知识图谱、PDF 标注、笔记→论文出口管线。

| 项目 | URL | star | 作用 |
|---|---|---|---|
| SiYuan 思源 | github.com/siyuan-note/siyuan | 44.2k | block 引用+SQLite 给本地 Markdown 建索引 |
| Logseq | github.com/logseq/logseq | 43.2k(API实测) | block 级双链+反链聚合+纯文本即数据库 |
| TriliumNext | github.com/TriliumNext/Trilium | 36.3k | attribute/relation 元数据模型 |
| Foam | github.com/foambubble/foam | 17.2k | [[wikilink]] 解析+broken-link 检测(最小可吸收件) |
| Zotero | github.com/zotero/zotero | 14.3k | PDF 标注↔笔记双向锚点 |
| Zettlr | github.com/Zettlr/Zettlr | 13k | CSL 引文+Pandoc 导出 camera-ready |
| Anytype | github.com/anyproto/anytype-ts | 8.0k | object+relation+type 数据建模 |
| Dendron | github.com/dendronhq/dendron | 7.4k | dot-hierarchy 层级命名 ⚠️维护放缓(2025-11) |
| Better BibTeX | github.com/retorquere/zotero-better-bibtex | 6.7k | @citekey→文献节点 解析约定 |
| Quarto | github.com/quarto-dev/quarto-cli | 5.7k | 可执行笔记→论文,交叉引用 |
| Hypothesis | github.com/hypothesis/h | 3.1k | W3C Web Annotation 标准标注数据模型 |
| KOReader | github.com/koreader/koreader | 27.1k | 高亮导出 Markdown(数据源) |
| Pandoc | github.com/jgm/pandoc | 44.5k | shell out 导出带引文 PDF/docx |

**评估员备注:** 质量 high,14 项全真、技术栈与 borrow 分析专业(纯文本 vs SQLite 索引两条路线、CSL/citeproc 均内行)。**doubtful:** 除 Logseq 经 API 实测(43,159 吻合)外,其余因 API 限流未逐一复核,量级合理但建议对 SiYuan(44.2k)/TriliumNext(36.3k)/Anytype(8.0k) 复核;Dendron 放缓、Athens Research 已实质废弃(只取设计)。**missing(已补):** Org-roam(Emacs Zettelkasten 标杆,核心遗漏)、JabRef、TiddlyWiki(单文件本地优先,与零依赖高度契合)、Joplin(仅 takeaways 提及)、zk/zk-nvim。

### 维度 7 · 科研 Agent / AI 辅助科研
**该领域在做什么:** 通用深度研究 agent、全自动 AI 科学家、文献 RAG/阅读。三梯队收敛到同一流水线骨架。

| 项目 | URL | star | 作用 |
|---|---|---|---|
| STORM/Co-STORM | github.com/stanford-oval/storm | 28.3k | 多视角提问→大纲→分节填充 写作骨架 |
| GPT Researcher | github.com/assafelovic/gpt-researcher | 27.4k | plan→子问题→检索→带引用合成 状态机 |
| dzhng/deep-research | github.com/dzhng/deep-research | ~19k(被低估) | 极简迭代研究循环(<500行,零依赖蓝本) |
| The AI Scientist | github.com/SakanaAI/AI-Scientist | ~14k | idea→实验→分析→写作→评审 全生命周期 lane |
| Open Deep Research | github.com/langchain-ai/open_deep_research | ~11.5k(被低估) | supervisor-researcher 层级编排 |
| PaperQA2 | github.com/Future-House/paper-qa | 8.6k | 可纯本地离线 RAG,带引用可追溯(最契合零依赖) |
| Local Deep Research | github.com/LearningCircuit/local-deep-research | 7.8k | 本地优先+加密+arXiv/PubMed(定位最像) |
| The AI Scientist-v2 | github.com/SakanaAI/AI-Scientist-v2 | ~6.4k | agentic 树搜索(多分支探索看板) |
| Agent Laboratory | github.com/SamuelSchmidgall/AgentLaboratory | ~5.7k | 三阶段+checkpoint 存档/恢复(断点续跑雏形) |
| AI-Researcher | github.com/HKUDS/AI-Researcher | ~5.4k | Level 1/2 双输入档(任务模板) |
| PapersGPT for Zotero | github.com/papersgpt/papersgpt-for-zotero | ~2.4k | 围绕本地文献库做问答 |
| Curie | github.com/Just-Curieous/Curie | ~361 | 实验严谨性显式模块(小众,仅参考) |
| open-coscientist-agents | github.com/conradry/open-coscientist-agents | ~64(已归档) | co-scientist 多 agent 辩论排名(小众) |

**评估员备注:** 这批最扎实,14 项全真、星量诚实。需修正两点:**dzhng/deep-research(~19k)与 Open Deep Research(~11.5k)实为高星明星项目,被标"待核实"导致梯队偏差,应上调进核心梯队;dzhng 的 TS 极简循环(<500行)对零依赖目标尤其契合,价值被低估。** Curie(~361)、open-coscientist(~64,已归档)实际小众,行文"借鉴价值"语气略高估。**missing(已补):** AgentRxiv(与 Agent Laboratory 同源热门)、ResearchAgent/SciAgents、OpenManus 系。

### 维度 8 · 学术搜索 / 文献发现
**该领域在做什么:** 学术 API 取数、文献推荐、citation graph、Connected Papers 类、paper RAG。

| 项目 | URL | star | 作用 |
|---|---|---|---|
| paper-qa(PaperQA2) | github.com/Future-House/paper-qa | 8.6k | 对本地 PDF 仓 RAG 问答(重,仅外部入口) |
| scholarly | github.com/scholarly-python-package/scholarly | 1.9k | Google Scholar 抓取(最脆需代理) |
| arxiv-sanity-lite | github.com/karpathy/arxiv-sanity-lite | 1.6k | 最小单文件 Flask 本地优先 |
| arxiv.py | github.com/lukasschwab/arxiv.py | 1.5k | arXiv API wrapper 取数层 |
| semanticscholar | github.com/danielnsilva/semanticscholar | 460 | S2 Recommendations API(seed→相似论文) |
| pyalex | github.com/J535D165/pyalex | 383 | OpenAlex wrapper(免费无 key,取数首选) |
| LocalCitationNetwork | github.com/LocalCitationNetwork/LocalCitationNetwork.github.io | 138 | 纯前端 JS 局部引用网络(形态唯一同源) |
| citation-graph-builder | github.com/FZJ-IEK3-VSA/citation-graph-builder | 25 | PDF→引用抽取(反面权衡,不要走这条) |
| Citegraph | github.com/Citegraph/citegraph | 22 | 大规模全局图(重,反面) |
| citegraph(oowekyala) | github.com/oowekyala/citegraph | 22 | bibtex→引用图 CLI(可做外部任务脚本) |
| semanticscholar-MCP-Server | github.com/JackKuo666/semanticscholar-MCP-Server | 69 | 把 S2 API 以 MCP 接到 agent 生成侧 |
| Citation Network Explorer | github.com/CitationGecko/citation-network-explorer | 57(2019归档) | seed 扩展式发现范式 |
| openalex-local | github.com/ywatanabe1989/openalex-local | 1(个人项目) | 学术检索=本地 SQLite+FTS5 离线范式 |

**评估员备注:** 14 项 URL 全真,star 实测基本准确(arxiv.py 实为 1.5k)。**doubtful:** openalex-local 仅 1 star,是个人项目(SciTeX 工具链一部分),作架构参考可以但不应当成熟代表;Citation Network Explorer 2019 已归档迁至 gecko-react;三个同名 citegraph 均仅 22 star,影响力很小。**missing(已补):** **Connected Papers(领域最知名 seed→图谱产品,标题点名却未提)**、habanero/crossref-commons(多处提 Crossref 却无客户端)、paperscraper(跨源检索下载)、原版 arxiv-sanity(~5k)、**GROBID(kermitt2/grobid,~3.5k,PDF→引用抽取事实标准)**、anystyle/refextract、txtai/haystack(通用 RAG 框架)。

---

## 3. 跨维度可吸收清单(P0/P1/P2)

> 标注 **【v3.2】** 的项直接服务当前"驾驶舱冲击力 Hero + 数据飞轮可视化"规划。

### P0 — 立即吸收(零依赖、低成本、高收益)

| # | 来源 | 吸收什么 | 落到 pipeline-board 哪里 |
|---|---|---|---|
| P0-1 **【v3.2】** | mermaid(维度4) + PlotNeuralNet 的 diagram-as-code 思路 | 用纯前端自绘一小段 SVG 状态机/流程图(选题→实验→成文→投稿),**或仅产出 mermaid 文本供复制**,不引任何 JS 库 | Hero 区的"数据飞轮可视化"核心——四状态流程图就是天然的状态机图 |
| P0-2 **【v3.2】** | Focalboard + Vikunja(维度1) 的"同一数据多视图" | 同一批论文/实验按状态看是看板、按 deadline 看是日历/甘特、按清单看是表格 | 驾驶舱主视图切换,数据飞轮的多角度呈现 |
| P0-3 | SciencePlots(维度4) 的"风格=纯文本档" + palettable(维度4) 纯 Python 零依赖调色板 | 把看板/图表配色与排版做成 profiles/*.json 同构风格档;建一个 colors 常量表 | 已有 profiles/paper.json、thesis.json,顺势加视觉风格档;Hero 配色 |
| P0-4 **【v3.2】** | CMasher/colorcet/cmcrameri(维度4) 色图数据 | 只内嵌少量感知均匀+色盲安全 RGB 查找表 | 数据飞轮的状态条/进度热度着色,保证"学术正经且色盲安全" |
| P0-5 | SciNote 三层(维度1) + Trilium attributes(维度1) + Anytype object/relation(维度6) | 课题/论文/实验/文献为一等公民,状态/期刊/截止日为结构化属性 | state.json 的对象数据模型 |
| P0-6 | doi2bib content-negotiation(维度3) + pyalex(维度8,OpenAlex 免费无 key) | DOI/arXiv→BibTeX 最小可靠单元:一次 HTTP 调用,无需自建解析 | prompts/ 生成侧的引文导入任务脚本→写回 json→面板只读 |

### P1 — 中期吸收

| # | 来源 | 吸收什么 | 落到哪里 |
|---|---|---|---|
| P1-1 | Snakemake/DVC(维度5) 文件依赖+内容哈希+增量复跑 + Sacred FileStorageObserver | 用纯 Python+文件 mtime 实现"每次 run 一个本地目录,只重算过期阶段" | 任务飞轮的运行单元/断点续跑内核 |
| P1-2 | Agent Laboratory 三阶段+checkpoint(维度7) | "任务断点续跑"机制 | 任务池的状态保存 |
| P1-3 | klb2/review-response + GjjvdBurg 工作流(维度2) | 审稿意见={reviewer,编号,原文,回复,关联改动};意见=卡片、轮次=分组、改动=diff | 本地版投稿 revision tracker 看板,一键导出 response letter |
| P1-4 | refchecker(维度2) + rebiber(维度2,纯 Python 离线) | 每条 reference→存在性+字段一致性校验→标红存疑项;离线词典规范化 .bib | 引文核实模块(反 AI 幻觉,差异化切入点) |
| P1-5 | Foam(维度6) [[wikilink]] 解析+broken-link 检测+反链聚合 | 实现成本最低、收益最直接的笔记互链 | 让实验记录与论文章节互相挂钩 |
| P1-6 | LocalCitationNetwork(维度8,纯前端无后端) | seed→局部引用图→浏览器内 canvas/D3 可视化 | "某项目参考文献关系图"视图,纯前端实现 |

### P2 — 远期/可选

| # | 来源 | 吸收什么 | 落到哪里 |
|---|---|---|---|
| P2-1 | thesis-tracker git hook(维度1) | 从文件/git 自动派生写作进度,减少手动填表 | 写作进度面板:进度自动派生 > 手动填表 |
| P2-2 | dzhng/deep-research <500行极简循环(维度7) | query→搜→评估→再 query 最小循环逻辑(零依赖蓝本) | "为项目推荐相关文献"任务 |
| P2-3 | PaperQA2/Local Deep Research(维度7,可纯本地离线) | 本地 LLM+本地 embedding 的离线 RAG 模式 | 成文/投稿阶段挂"对相关文献提问"外部入口 |
| P2-4 | Pandoc(维度6) + tectonic(维度2) | shell out 到用户本机已装的 pandoc/tectonic 导出带引文 PDF | 笔记→论文出口管线,不打包渲染引擎 |
| P2-5 | openalex-local(维度8) SQLite+FTS5 离线范式 | "学术检索=本地 SQLite,零外部服务"架构思想 | 若需本地文献缓存时的方向 |
| P2-6 | bibtex-tidy(维度3,纯前端可跑 MIT) | .bib 清理/去重逻辑 | 可直接移植 |

---

## 4. 要避开的坑

1. **不内嵌任何重依赖。** matplotlib/seaborn/UltraPlot/schemdraw(维度4)、LangGraph/FastAPI/DSPy/Docker/GPU(维度7)、Nextflow JVM/Quarto Deno/ClearML server(维度5)——引任何一个都会破坏纯前端单文件/PyInstaller 单文件可打包性。**学其理念与状态机设计,不引其依赖。**
2. **不自己做 PDF→引用抽取。** citation-graph-builder(维度8)那条路重且脆(依赖 GROBID 解析)。引用关系一律走 OpenAlex/S2 元数据(pyalex/semanticscholar)。
3. **不追大规模全局图。** Citegraph(维度8)的 940 万顶点全局图服务与 board 的"单项目粒度局部视图"定位相反。坚持轻量局部视图。
4. **取数走"外部脚本→写回 json→面板只读",不进核心。** 所有联网/LLM/RAG 能力(paper-qa、scholarly、MCP server)放在 prompts/ 生成侧,保持播放器/片库解耦——面板永远只读渲染。
5. **刻意做减法。** Kanboard 的"限制功能数量"哲学是产品层最佳参照。对照 ClearML/ZenML 的功能边界,明确 board 要做/不做什么,避免功能膨胀。
6. **不引镜像/废弃源。** Pybtex 用 GitLab/PyPI 官方源而非 live-clones 镜像;Focalboard/Dendron/Athens 已停更,只取设计不作活跃依赖。

## 5. 差异化护城河

1. **三合一生态位空白**(8 维度交叉验证):科研状态机语义 + 进度可视化 + 零部署纯本地,无任何项目同时满足。
2. **零部署对无运维用户的绝对友好**:双击 HTML 即用。所有 ELN 与 Streamlit 派生 dashboard 都需 server,这是对研究生群体的最大卖点(反例定位)。
3. **引文核实=反 AI 幻觉切入点**:refchecker 由 Mark Russinovich 出品即为信号,这是当前最热也最缺工具化的环节,本地对照 CrossRef/OpenAlex 校验即可形成差异化价值。
4. **diagram-as-code 状态机可视化** **【v3.2】**:四状态流程天然是状态机,纯前端自绘 SVG 飞轮图,是冲击力 Hero 的护城河,且零依赖。
5. **进度自动派生而非手动填表**:从文件/git 派生状态,降低研究生维护负担。

## 6. 待核实清单(供人工复核)

**评估员明确标注的 doubtful:**
- **Pybtex** — JSON 给的 live-clones/pybtex URL 仅 5 star、是镜像非官方仓,落地前**必须**改用官方 GitLab/PyPI 源。(维度3)
- **UltraPlot** — 实际仅约百级 star(相比 ProPlot ~1.1k 偏小),属新兴项目,入榜偏前。(维度4)
- **openalex-local** — 仅 1 star,个人项目(SciTeX 工具链一部分),作架构参考可,不应当成熟代表。(维度8)
- **Citation Network Explorer(CitationGecko)** — 真实但 2019 已归档/弃用,迁至 gecko-react,状态应更新。(维度8)
- **三个 citegraph/Citegraph** — 均仅 22 star,真实但影响力很小,与高星项目并列略堆砌。(维度8)

**star/URL 偏差(评估员指出,需上调或复核):**
- JabRef(实测 4.3k)、Streamlit(实测数万级) 的"待核实"标注多余,实属可信。(维度1)
- mseri/doi2bib(72)、arxiv-sanity-lite(1618) 标"待核实"偏保守,实可信。(维度3)
- **dzhng/deep-research(实测 ~19k)、Open Deep Research(实测 ~11.5k)** 被低估,应上调进核心梯队;Curie(~361)、open-coscientist(~64,已归档) 被高估为有借鉴价值,实属小众。(维度7)
- Curie 实测 ~361、open-coscientist 实测 ~64 且已归档。(维度7)
- 维度6 除 Logseq 经 API 实测(43,159)外,SiYuan(44.2k)/TriliumNext(36.3k)/Anytype(8.0k) 因 API 限流未二次确认,建议复核。
- 维度4 未精确核实的 star:cmcrameri、schemdraw、drawio、rougier book(均标"待核实")。
- ClearML(6.7k)/ZenML(5.4k)/Sacred(4.4k) 原"待核实"已被维度5评估员复核确认,可转 confirmed。

**活跃度时效提示:**
- Focalboard 标准仓库已被官方标记"not maintained"(迁至 mattermost-plugin-boards)。
- zadam/trilium → 社区 TriliumNext(v0.103.0)。
- Dendron 维护放缓(最后 push 2025-11);Athens Research 已实质废弃。
- amazon-science/RefChecker 与 markrussinovich/refchecker 是两个不同项目(后者才是引文核验,前者是 LLM 幻觉 benchmark),勿混淆。