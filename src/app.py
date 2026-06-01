#!/usr/bin/env python3
"""
科研流水线 Research Pipeline Board · v3.1 Daily Research Cockpit
- 流程/状态驱动. 状态总览(总览面板) → 点状态 → 进入该状态面板(子项+模板) ; 文档库
- 零依赖纯标准库, 一条命令 python3 app.py
- 数据源: text_workshop/projects/ + paper_workbench/data/*.state.json
- 每 5 秒自动刷新. 模板结构镜像我们论文项目 Notion 笔记本。
"""
import json, os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote

# 内容源可配置：环境变量优先；未配置则回落到仓库自带 demo/（开箱即用）
# 本地接你的真实论文库：export RP_PROJ_ROOT=/你的内容库/projects RP_STATE_DIR=/你的内容库/state
_HERE = os.path.dirname(os.path.abspath(__file__))
_DEMO = os.path.normpath(os.path.join(_HERE, "..", "demo"))
PROJ_ROOT = os.path.expanduser(os.environ.get("RP_PROJ_ROOT", os.path.join(_DEMO, "projects")))
STATE_DIR = os.path.expanduser(os.environ.get("RP_STATE_DIR", os.path.join(_DEMO, "state")))
PORT = int(os.environ.get("RP_PORT", "8771"))
# v3.1 Daily Cockpit: planner 目录默认在内容根(STATE_DIR 的父目录)下
CONTENT_ROOT = os.path.dirname(os.path.realpath(STATE_DIR))
PLANNER_DIR = os.path.expanduser(os.environ.get("RP_PLANNER_DIR", os.path.join(CONTENT_ROOT, "planner")))
# profiles：按类别定制的任务策略，随仓库分发（src 的同级 profiles/）
PROFILES_DIR = os.path.expanduser(os.environ.get("RP_PROFILES_DIR", os.path.normpath(os.path.join(_HERE, "..", "profiles"))))

# 4 状态, 每个状态含子项, 每个子项有标准模板要点 (镜像项目 Notion)
FLOW = [
    {"key": "选题立项", "subs": [
        {"name": "Idea", "tpl": ["一句话问题陈述", "创新点 hypothesis (1-3 条)", "跟已有工作的区别"]},
        {"name": "验证创新性", "tpl": ["谁做过类似 (竞争者清单)", "我的 white-space", "关键指标对比"]},
        {"name": "设计实验", "tpl": ["baseline 选择", "数据集", "评价指标", "Plan B / 数据 audit"]},
    ]},
    {"key": "实验执行", "subs": [
        {"name": "跑实验", "tpl": ["数据采集/生成", "baseline→main→ablation 顺序", "中间结果记录"]},
        {"name": "评估结果", "tpl": ["精度/显著性", "vs baseline 对比", "Pivot 决策"]},
    ]},
    {"key": "成文", "subs": [
        {"name": "选期刊", "tpl": ["候选期刊 (IF + 河海等级)", "向上一级参考原则"]},
        {"name": "写稿", "tpl": ["outline 构建", "Result→Method→Discussion→Intro→Abstract 顺序", "图表"]},
        {"name": "审稿", "tpl": ["SciWrite 5 轮", "事实核查", "蒸馏审稿专家模拟"]},
    ]},
    {"key": "投稿发表", "subs": [
        {"name": "投稿", "tpl": ["cover letter", "reviewer 推荐/反推荐", "投稿系统提交"]},
        {"name": "跟进修回", "tpl": ["decision letter 解读", "point-by-point response"]},
    ]},
]

def product_line(name):
    if name.startswith(("thesis","phd")) or "博论" in name: return "硕博论文"
    if name.startswith("paper_"): return "小论文"
    if name.startswith("patent"): return "专利"
    if name.startswith(("projectbook","report")): return "项目报告"
    return "其他"

def safe_under_root(p):
    root = os.path.realpath(PROJ_ROOT)
    target = os.path.realpath(p)
    try:
        return os.path.commonpath([root, target]) == root
    except ValueError:
        return False

def read_json(path, default):
    try:
        if os.path.isfile(path):
            return json.load(open(path, encoding="utf-8"))
    except Exception:
        pass
    return default

def load_state(name):
    f = os.path.join(STATE_DIR, name + ".state.json")
    if os.path.isfile(f):
        try: return json.load(open(f, encoding="utf-8"))
        except: pass
    return {"title_cn": "", "summary": "", "current": "选题立项",
            "blocks": {b["key"]: "todo" for b in FLOW},
            "substeps": {}, "substep_docs": {}, "note": ""}

def scan_projects():
    out = []
    profiles = load_profiles()
    if not os.path.isdir(PROJ_ROOT): return out
    for name in sorted(os.listdir(PROJ_ROOT)):
        pdir = os.path.join(PROJ_ROOT, name)
        if not os.path.isdir(pdir) or name.startswith("."): continue
        ledger = []
        lf = os.path.join(pdir, "versions", "ledger.json")
        if os.path.isfile(lf):
            try: ledger = json.load(open(lf))
            except: pass
        files = []
        for r2, dirs, fns in os.walk(pdir):
            dirs[:] = [d for d in dirs if d not in (".git","versions","node_modules")]
            for fn in fns:
                if fn.startswith("."): continue
                full = os.path.join(r2, fn)
                files.append({"rel": os.path.relpath(full, pdir),
                              "path": os.path.relpath(full, PROJ_ROOT),
                              "mtime": os.path.getmtime(full),
                              "ext": os.path.splitext(fn)[1].lower().lstrip(".")})
        files.sort(key=lambda x: -x["mtime"])
        st = load_state(name)
        # v3.1: 项目任务池 tasks.json
        tasks_obj = read_json(os.path.join(pdir, "tasks.json"), {"tasks": []})
        tasks = tasks_obj.get("tasks", []) if isinstance(tasks_obj, dict) else []
        tc = {"todo": 0, "doing": 0, "done": 0, "blocked": 0, "dropped": 0}
        for t in tasks:
            s = (t.get("status") or "todo")
            if s in tc: tc[s] += 1
        line = product_line(name)
        pf = profiles.get(line)
        out.append({"name": name, "line": line,
                    "title_cn": st.get("title_cn") or name,
                    "versions": len(ledger),
                    "last_why": ledger[-1]["why"] if ledger else "",
                    "last_date": ledger[-1]["date"] if ledger else "",
                    "state": st, "files": files,
                    "tasks": tasks, "task_counts": tc,
                    "profile": pf.get("profile") if pf else None,
                    "profile_label": pf.get("label") if pf else None})
    return out

def normalize_today(today, projects):
    """补全 today.selected_tasks 的任务详情；空则优雅降级。"""
    pmap = {p["name"]: p for p in projects}
    def find_task(proj, tid):
        p = pmap.get(proj)
        if not p: return None
        for t in p.get("tasks", []):
            if t.get("id") == tid: return t
        return None
    if not today or not isinstance(today, dict) or not today.get("selected_tasks"):
        return {"configured": False,
                "message": "暂无今日任务。可在 planner/today.json 中添加，或用 prompts/daily_planner.md 让 Agent 生成。",
                "mode": "low_pressure", "selected_tasks": [], "recent_wins": []}
    out = []
    for sel in today.get("selected_tasks", [])[:3]:
        proj, tid = sel.get("project"), sel.get("task_id")
        t = find_task(proj, tid)
        p = pmap.get(proj)
        out.append({
            "project": proj,
            "project_title": (p["title_cn"] if p else proj),
            "task_id": tid,
            "role": sel.get("role", "main"),
            "why_today": sel.get("why_today", ""),
            "task": t,  # 找不到为 None，前端显示占位
        })
    return {"configured": True,
            "message": today.get("message", "今天只推进 1–3 件事。完成启动动作也算推进。"),
            "mode": today.get("mode", "low_pressure"),
            "date": today.get("date", ""),
            "hidden_count": max(0, len(today.get("selected_tasks", [])) - 3),
            "selected_tasks": out,
            "recent_wins": today.get("recent_wins", [])}

def load_today(projects):
    return normalize_today(read_json(os.path.join(PLANNER_DIR, "today.json"), {}), projects)

def load_done_log():
    log = read_json(os.path.join(PLANNER_DIR, "done_log.json"), [])
    return log if isinstance(log, list) else []

def load_profiles():
    """读 profiles/*.json，建立 line→profile 映射。缺失则返回空 dict（优雅降级）。"""
    out = {}
    if os.path.isdir(PROFILES_DIR):
        for fn in os.listdir(PROFILES_DIR):
            if not fn.endswith(".json"): continue
            pf = read_json(os.path.join(PROFILES_DIR, fn), None)
            if isinstance(pf, dict) and pf.get("line"):
                out[pf["line"]] = pf
    return out

class H(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def _s(self,c,b,ct="application/json"):
        bb=b.encode() if isinstance(b,str) else b
        self.send_response(c); self.send_header("Content-Type",ct+"; charset=utf-8")
        self.send_header("Content-Length",str(len(bb))); self.end_headers(); self.wfile.write(bb)
    def do_GET(self):
        u=urlparse(self.path)
        if u.path=="/": self._s(200,HTML,"text/html")
        elif u.path=="/api/tree":
            projects=scan_projects()
            self._s(200,json.dumps({"projects":projects,"flow":FLOW,
              "today":load_today(projects),"done_log":load_done_log()[-20:],
              "profiles":load_profiles()},ensure_ascii=False))
        elif u.path=="/api/file":
            rel=unquote(parse_qs(u.query).get("path",[""])[0]); full=os.path.join(PROJ_ROOT,rel)
            if not safe_under_root(full) or not os.path.isfile(full):
                self._s(404,json.dumps({"error":"nf"})); return
            ext=os.path.splitext(full)[1].lower().lstrip(".")
            if ext in ("md","txt","py","json","csv","tex"):
                c=open(full,encoding="utf-8",errors="replace").read()
                self._s(200,json.dumps({"type":"text","ext":ext,"content":c},ensure_ascii=False))
            else:
                self._s(200,json.dumps({"type":"binary","ext":ext,
                  "note":f"{ext.upper()} 文件, 网页内不渲染, 双击本地查看"},ensure_ascii=False))
        else: self._s(404,json.dumps({"e":1}))

HTML = r"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>科研流水线</title><style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:#0f1420;color:#e6edf3;height:100vh;overflow:hidden}
.app{display:grid;grid-template-columns:270px 1fr;height:100vh}
.side{background:#161b26;border-right:1px solid #232a38;overflow-y:auto;padding:14px 0}
.side h1{font-size:15px;padding:0 18px 10px;color:#7d8da5;font-weight:600}
.line{padding:10px 18px 4px;font-size:11px;color:#5a6b85;letter-spacing:1px;margin-top:6px}
.proj{padding:9px 18px;cursor:pointer;font-size:14px;color:#c5d1e0;border-left:3px solid transparent}
.proj:hover{background:#1d2433}.proj.active{background:#1d2433;border-left-color:#4493f8;color:#fff}
.proj .meta{font-size:11px;color:#5a6b85;margin-top:2px}
.proj.rdm{color:#9fb4d4;border-bottom:1px solid #232a38;margin-bottom:4px;padding-bottom:11px}
.newbtn{margin:14px 18px 4px;padding:9px;border:1px solid #2f5fa8;border-radius:6px;color:#79b0f7;font-size:12px;text-align:center;cursor:pointer;background:#16243f}
.newbtn:hover{background:#1d3052}
.main{display:grid;grid-template-rows:auto auto 1fr;overflow:hidden}
.head{padding:16px 24px;border-bottom:1px solid #232a38;background:#131824}
.head h2{font-size:20px}.head .sub{font-size:12px;color:#7d8da5;margin-top:3px}
.tabs{display:flex;gap:4px;padding:10px 24px 0;background:#131824;border-bottom:1px solid #232a38}
.tab{padding:8px 16px;font-size:13px;color:#7d8da5;cursor:pointer;border-radius:6px 6px 0 0}
.tab.active{background:#0f1420;color:#fff;border:1px solid #232a38;border-bottom:none}
.content{overflow-y:auto;padding:24px}
.crumb{font-size:13px;color:#7d8da5;margin-bottom:16px}.crumb a{color:#58a6ff;cursor:pointer}
/* 总览面板 */
.ovpanel{background:#161b26;border:1px solid #232a38;border-radius:10px;padding:16px 20px;margin-bottom:20px}
.ovpanel .t{font-size:13px;color:#7d8da5;margin-bottom:6px}
.ovpanel .s{font-size:14px;line-height:1.6;color:#c5d1e0}
.flow{display:flex;align-items:stretch;margin-bottom:8px;flex-wrap:wrap}
.fblock{flex:1;min-width:150px;background:#161b26;border:1px solid #232a38;border-radius:10px;padding:14px 16px;margin-right:8px;cursor:pointer;transition:.15s}
.fblock:hover{border-color:#4493f8;background:#1a2740}
.fblock.doing{border-color:#3fb950;box-shadow:0 0 0 1px #3fb950}
.fblock.done{opacity:.75;border-color:#388bfd}
.fblock .bt{font-size:15px;font-weight:700;margin-bottom:8px}
.fblock .bs{font-size:11px;padding:2px 8px;border-radius:10px;display:inline-block;margin-bottom:8px}
.bs.doing{background:#1a3326;color:#3fb950}.bs.done{background:#16263f;color:#58a6ff}.bs.todo{background:#21262d;color:#7d8da5}
.fblock .step{font-size:12px;color:#8da3c4;padding:2px 0}
.fblock .enter{font-size:11px;color:#58a6ff;margin-top:8px}
.arrow{align-self:center;color:#3a4555;font-size:18px;margin:0 2px}
/* 状态面板 (二级): 一段一段的框 */
.subcard{background:#161b26;border:1px solid #232a38;border-radius:10px;padding:16px 20px;margin-bottom:14px;border-left:4px solid #2d3a52;cursor:pointer;transition:border-color .15s}
.subcard:hover{border-color:#3a4a66}.subcard:hover .entr{color:#79b0f7}
.subcard.doing{border-left-color:#3fb950}.subcard.done{border-left-color:#58a6ff}
.subcard .entr{margin-left:auto;font-size:12px;color:#5a6b85}
/* 刷新按钮 + 三级面板 */
.refbtn{margin-left:14px;font-size:12px;padding:3px 12px;border:1px solid #2d3a52;border-radius:6px;color:#79b0f7;background:#16243f;cursor:pointer}
.refbtn:hover{background:#1d3052}
.subpanel{background:#161b26;border:1px solid #232a38;border-radius:10px;padding:8px 24px 20px}
.mdbox h1{font-size:20px;margin:16px 0 8px;color:#fff}.mdbox h2{font-size:16px;margin:14px 0 6px;color:#cfe0f5;border-bottom:1px solid #232a38;padding-bottom:4px}.mdbox h3{font-size:14px;margin:10px 0 4px;color:#9fb4d4}
.mdbox li{margin:3px 0 3px 20px;font-size:14px;color:#c5d1e0}.mdbox p{font-size:14px;color:#c5d1e0;margin:4px 0}.mdbox code{background:#0f1420;padding:1px 5px;border-radius:4px;color:#79b0f7}
.mdbox .docpath{font-size:11px;color:#5a6b85;margin:8px 0 12px;font-family:monospace}
.subcard .sh{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.subcard h3{font-size:16px;color:#fff}
.subcard .badge{font-size:11px;padding:2px 10px;border-radius:10px}
.badge.doing{background:#1a3326;color:#3fb950}.badge.done{background:#16263f;color:#58a6ff}.badge.todo{background:#21262d;color:#7d8da5}
.subcard .tpl-t{font-size:11px;color:#5a6b85;letter-spacing:1px;margin:8px 0 4px}
.subcard .tpl{font-size:13px;color:#c5d1e0;padding:3px 0 3px 16px;position:relative}
.subcard .tpl:before{content:"·";position:absolute;left:4px;color:#4493f8}
.subcard .files{margin-top:10px;border-top:1px solid #232a38;padding-top:8px}
.subcard .f{font-size:12px;color:#79b0f7;cursor:pointer;padding:2px 0}.subcard .f:hover{text-decoration:underline}
.subcard .nofile{font-size:12px;color:#5a6b85;font-style:italic}
/* 子步骤色点 (总览里) */
.sdot{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:5px;vertical-align:middle}
.sdot.doing{background:#3fb950}.sdot.done{background:#58a6ff}.sdot.todo{background:#3a4555}
/* 文档库 · 横向大分类标签 + 纵向折叠目录 */
.docbar{display:flex;gap:8px;margin-bottom:14px;align-items:center}
.docbtn{padding:6px 14px;font-size:13px;border:1px solid #2d3a52;border-radius:6px;color:#8da3c4;cursor:pointer;background:#161b26}
.docbtn:hover{border-color:#3a4a66}.docbtn.active{background:#1d3052;color:#fff;border-color:#4493f8}
.docbtn.tpl{color:#5a6b85}.docbtn.tpl.active{background:#21262d;color:#9fb4d4;border-color:#3a4555}
.tplpanel{background:#161b26;border:1px solid #232a38;border-radius:10px;padding:40px;text-align:center;color:#5a6b85}
.tplpanel .big{font-size:15px;color:#7d8da5;margin-bottom:10px}
.tplbadge{display:inline-block;font-size:11px;padding:2px 10px;border-radius:10px;background:#21262d;color:#7d8da5;margin-bottom:14px}
.doccat{font-size:12px;color:#8da3c4;margin:2px 0 10px;display:flex;align-items:center;justify-content:space-between}
.allf{font-weight:600;color:#cfe0f5!important;border:1px solid #2d3a52;background:#16243f;margin-bottom:6px}
.allf.active{background:#1d3052;border-color:#4493f8}
.grp{font-size:12px;color:#7d8da5;padding:8px 6px 4px;cursor:pointer;letter-spacing:.5px;user-select:none}
.grp:hover{color:#9fb4d4}.grp .caret{display:inline-block;width:12px;color:#5a6b85}
.grp .gcnt{font-size:10px;color:#5a6b85;background:#1a2030;border-radius:8px;padding:0 6px;margin-left:4px}
.f.sub{margin-left:10px;font-size:13px}
.f.dis{color:#4a5568;cursor:default}.f.dis:hover{background:none}.f.dis .ext{background:#1a2030;color:#4a5568}
.nofile.sub{margin-left:18px}
/* 文档库 */
.docview{display:grid;grid-template-columns:300px 1fr;gap:16px;height:calc(100vh - 180px)}
.flist{overflow-y:auto;border-right:1px solid #232a38;padding-right:8px}
.f{padding:7px 10px;cursor:pointer;font-size:13px;border-radius:6px;color:#c5d1e0;display:flex;justify-content:space-between;gap:6px}
.f:hover{background:#1d2433}.f.active{background:#243049;color:#fff}
.f .ext{font-size:10px;padding:1px 5px;border-radius:3px;background:#2d3a52;color:#8da3c4}
.viewer{overflow-y:auto;padding:0 8px;font-size:14px;line-height:1.7}
.viewer h1{font-size:22px;margin:14px 0 8px}.viewer h2{font-size:18px;margin:12px 0 6px;color:#8ab4f8;border-bottom:1px solid #232a38;padding-bottom:3px}
.viewer h3{font-size:15px;margin:10px 0 5px;color:#c5d1e0}.viewer code{background:#1d2433;padding:1px 5px;border-radius:3px;color:#7dd3fc}
.viewer pre{background:#0a0e16;padding:12px;border-radius:8px;overflow-x:auto;border-left:3px solid #4493f8;margin:8px 0}
.viewer li{margin:3px 0 3px 20px}.empty{color:#5a6b85;text-align:center;margin-top:60px}
.dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:#3fb950;margin-right:6px;animation:p 2s infinite}@keyframes p{0%,100%{opacity:1}50%{opacity:.3}}
/* ✨ 视觉优化 (深色/日间通用) */
::-webkit-scrollbar{width:9px;height:9px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:#2a3344;border-radius:6px}
::-webkit-scrollbar-thumb:hover{background:#3a4658}
body.light ::-webkit-scrollbar-thumb{background:#cdd5e2}
.side,.head,.tabs{box-shadow:0 1px 0 rgba(0,0,0,.12)}
.fblock,.subcard,.ovpanel,.subpanel,.tplpanel{box-shadow:0 1px 3px rgba(0,0,0,.16);border-radius:12px}
.fblock,.subcard{transition:transform .12s ease,border-color .15s,box-shadow .15s}
.fblock:hover,.subcard:hover{transform:translateY(-1px);box-shadow:0 5px 16px rgba(0,0,0,.22)}
.proj,.f,.tab,.docbtn,.newbtn,.refbtn{transition:background .12s,color .12s,border-color .12s}
.content{scroll-behavior:smooth}
.head h2{letter-spacing:.3px}
.tab{transition:all .12s}.tab:hover{color:#c5d1e0}
.docbtn{transition:all .12s}
.empty{font-size:13px;opacity:.75;line-height:1.9}
.newbtn{transition:all .12s;letter-spacing:.5px}
.allf{border-radius:8px}
.subcard .entr{transition:color .15s}
.mdbox{line-height:1.75}
/* ☀️ 日间模式 (light) · 仅覆盖配色, 不动布局 */
body.light{background:#eef1f5;color:#1c2530}
body.light .side,body.light .head,body.light .tabs{background:#fff;border-color:#dbe1ea}
body.light .side h1,body.light .head .sub,body.light .tab,body.light .line,body.light .proj .meta,body.light .grp,body.light .doccat,body.light .crumb,body.light .docpath{color:#54627a}
body.light .proj,body.light .f{color:#222b38}
body.light .proj:hover,body.light .proj.active,body.light .f:hover,body.light .f.active{background:#e8eef7}
body.light .tab.active{background:#eef1f5;color:#1c2530;border-color:#dbe1ea}
body.light .ovpanel,body.light .fblock,body.light .subcard,body.light .subpanel,body.light .tplpanel,body.light .viewer,body.light .docbtn{background:#fff;border-color:#dbe1ea}
body.light .ovpanel .s,body.light .subcard h3,body.light .mdbox p,body.light .mdbox li,body.light .fblock .bt,body.light .head h2,body.light .mdbox h1{color:#1c2530}
body.light .mdbox h2,body.light .viewer h2{color:#1858c4}
body.light .flist{border-color:#dbe1ea}
body.light code,body.light .mdbox code,body.light .viewer code{background:#e6ebf3;color:#1858c4}
body.light pre,body.light .viewer pre{background:#f0f3f8}
body.light .newbtn,body.light .allf{background:#eaf1fd;border-color:#bcd3f7}
body.light .arrow,body.light .caret{color:#9aa7ba}
body.light .docbtn.active{background:#1d3052;color:#fff}
/* v3.1 Daily Cockpit */
.proj.cockpitnav{color:#79b0f7;font-weight:600;border-bottom:1px solid #232a38;margin-bottom:2px;padding:11px 18px}
.proj.cockpitnav.active{background:#16243f;border-left-color:#4493f8;color:#fff}
.proj .tbadge{font-size:10px;background:#1d3052;color:#79b0f7;border-radius:8px;padding:1px 7px;margin-left:6px}
.cockpit{max-width:880px}
.ckmsg{background:#16243f;border:1px solid #2f5fa8;border-radius:10px;padding:12px 16px;color:#cfe0f5;font-size:14px;margin-bottom:18px}
.ckempty{text-align:center;padding:46px 20px;color:#8da3c4;font-size:15px}
.ckempty .hint{font-size:12px;color:#5a6b85;margin-top:10px}
.cksec{margin-bottom:22px}
.ckh{font-size:13px;color:#8da3c4;letter-spacing:1px;margin-bottom:10px;font-weight:600}
.ckh .cnt,.ckh .tbadge{font-size:11px;color:#5a6b85}
.tcard{background:#131a27;border:1px solid #232f44;border-radius:12px;padding:15px 18px;margin-bottom:12px;box-shadow:0 1px 3px rgba(0,0,0,.16)}
.tcard .th{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:8px}
.tcard .proj-tag{font-size:11px;background:#1a2030;color:#9fb4d4;border-radius:5px;padding:2px 8px}
.tcard .role{font-size:10px;border-radius:5px;padding:1px 7px;background:#21262d;color:#8da3c4}
.tcard .role.main{background:#1a3326;color:#3fb950}.tcard .role.fallback{background:#2a2418;color:#d29922}
.tcard .pr{font-size:12px;font-weight:700;font-family:monospace}
.tcard .en{font-size:11px;color:#8da3c4}
.tcard .stt{font-size:10px;border-radius:5px;padding:1px 7px;background:#21262d;color:#7d8da5;margin-left:auto}
.tcard .stt.doing{background:#1a3326;color:#3fb950}.tcard .stt.done{background:#16263f;color:#58a6ff}.tcard .stt.blocked{background:#3a2020;color:#f85149}
.tcard .ttl{font-size:16px;color:#fff;font-weight:600;margin-bottom:8px}
.tcard .why{font-size:13px;color:#cfe0f5;background:#16243f;border-radius:7px;padding:7px 11px;margin-bottom:8px}
.tcard .trow{font-size:13px;color:#c5d1e0;padding:4px 0;display:flex;gap:8px}
.tcard .trow .lab{color:#79b0f7;font-size:12px;min-width:74px;flex-shrink:0}
.tcard .trow.blk .lab{color:#f85149}.tcard .trow i{color:#5a6b85}
.ckfoot{text-align:center;font-size:12px;color:#5a6b85;margin-top:6px}
.hint{font-size:12px;color:#5a6b85;margin:6px 0}
.wins .win{font-size:13px;color:#a7e0b8;padding:3px 0}.wins .wd{color:#5a6b85;font-size:11px;font-family:monospace}.wins .prog{color:#d29922}
.blkrow{font-size:13px;color:#c5d1e0;padding:5px 0;border-bottom:1px solid #1c2433}.blkrow .bk{color:#f85149;font-size:12px}
.ovgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px}
.ovcard{background:#131a27;border:1px solid #232f44;border-radius:10px;padding:12px 14px;cursor:pointer;transition:.15s}
.ovcard:hover{border-color:#4493f8;transform:translateY(-1px)}
.ovcard .ovt{font-size:13px;color:#cfe0f5;margin-bottom:6px;font-weight:600}
.ovcard .ovc{display:flex;gap:10px;font-size:11px;color:#8da3c4;flex-wrap:wrap}
.ovcard .ovc .bk{color:#f85149}.ovcard .ovc .dn{color:#58a6ff}
/* === 日间模式 · 驾驶舱/任务池 配色加深(白底上提高对比度) === */
body.light .ckmsg,body.light .tcard .why{background:#eaf1fd;color:#1a3a6b;border:1px solid #cfe0f5}
body.light .tcard,body.light .ovcard{background:#fff;border-color:#dbe1ea}
body.light .tcard .ttl,body.light .ovcard .ovt{color:#1c2530}
/* 任务卡正文与标签 */
body.light .tcard .trow{color:#2a3645}
body.light .tcard .trow .lab{color:#1858c4}
body.light .tcard .en,body.light .ckfoot,body.light .hint,body.light .ckh,body.light .ovcard .ovc{color:#54627a}
body.light .tcard .proj-tag,body.light .ovcard{background:#f0f3f8}
body.light .tcard .proj-tag{color:#2a3645}
body.light .tcard .role{background:#e6ebf3;color:#54627a}
body.light .tcard .role.main{background:#dff3e6;color:#1a7f3c}
body.light .tcard .role.fallback{background:#fbf0d8;color:#8a6510}
body.light .tcard .stt{background:#e6ebf3;color:#54627a}
body.light .tcard .stt.doing{background:#dff3e6;color:#1a7f3c}
body.light .tcard .stt.done{background:#e1ecfb;color:#1858c4}
body.light .tcard .stt.blocked{background:#fbe0de;color:#c0362c}
/* 空态/计数/侧栏徽章 */
body.light .ckempty,body.light .ckempty .hint,body.light .ckh .cnt{color:#54627a}
body.light .proj .tbadge{background:#e1ecfb;color:#1858c4}
body.light .proj.cockpitnav{color:#1858c4}
body.light .proj.cockpitnav.active{background:#e8eef7;color:#0d1117}
/* 最近完成/卡住 */
body.light .wins .win{color:#1a7f3c}
body.light .wins .wd{color:#8a93a6}
body.light .blkrow{color:#2a3645;border-color:#e3e8f0}
body.light .blkrow .bk,body.light .ovcard .ovc .bk,body.light .tcard .trow.blk .lab{color:#c0362c}
body.light .ovcard .ovc .dn{color:#1858c4}
/* 状态总览/子卡 浅字加深 */
body.light .fblock .step,body.light .fblock .enter,body.light .subcard .tpl,body.light .subcard .tpl-t,body.light .ovpanel .t,body.light .subcard .nofile,body.light .nofile,body.light .empty{color:#54627a}
body.light .subcard .badge.todo,body.light .bs.todo{background:#e6ebf3;color:#54627a}
</style></head><body>
<div class="app">
 <div class="side"><h1>🔬 科研流水线</h1><div id="sidebar"></div>
   <div class="newbtn" onclick="alert('新建项目: v2 功能, 待实现')">＋ 新建项目</div>
   <div class="newbtn" onclick="alert('新建工作台: v2 功能, 待实现')">＋ 新建工作台</div>
   <div class="newbtn" id="themebtn" onclick="toggleTheme()">☀️ 日间</div>
 </div>
 <div class="main">
   <div class="head"><h2 id="ptitle">选择一个项目</h2>
     <div class="sub" id="psub"><span class="dot"></span>实时同步 · 每 5 秒自动刷新</div></div>
   <div class="tabs" id="tabs">
     <div class="tab active" id="tab-ov" onclick="setTab('ov')">📋 状态总览</div>
     <div class="tab" id="tab-task" onclick="setTab('task')">✅ 任务池</div>
     <div class="tab" id="tab-doc" onclick="setTab('doc')">📂 文档库</div>
   </div>
   <div class="content" id="content"></div>
 </div>
</div>
<script>
let DATA={projects:[],flow:[],today:{},done_log:[],profiles:{}},cur=null,view='cockpit',tab='ov',drillState=null,drillSub=null,curFile=null,docSel='__all__',openGroups={},docCat='org';
const LI={"硕博论文":"🎓","小论文":"📄","专利":"⚖️","项目报告":"📋","其他":"📦"};
const LO=["硕博论文","小论文","专利","项目报告","其他"];
const README=`# 🔬 科研流水线
**把论文 / 专利 / 项目从一个想法管到投稿发表的本地工作台。**

零依赖、本地运行、自动刷新，不依赖 Notion 或任何外部账号。

## 怎么用 (三级下钻)
1. **左边选一个项目** — 项目按类别分组：硕博论文 / 小论文 / 专利 / 项目报告。
2. **状态总览** — 一眼看到这个项目走到流程哪一步：选题立项 → 实验执行 → 成文 → 投稿发表。绿=进行中，蓝=已完成，灰=未开始。
3. **点一个状态** (如选题立项) — 进入它的子步骤框：Idea / 验证创新性 / 设计实验。
4. **点一个子步骤** — 打开它的标准格式文档 (md)，照着标准结构填内容。

## 两个视图
- **📋 状态总览**：看流程 + 标准文档 (主视图)。
- **📂 文档库**：看项目所有文件。\`归纳整理版\` = 网页能直接打开的文本 (md/txt 等)；\`原始版(素材)\` = Word/PDF/HTML 等打不开的原始文件。

## 同步
- 本地改了文档 → 点右上角 **🔄 刷新**，看板立刻更新。
- 界面也每 5 秒自动拉取一次。

---
*选左边任意项目开始 · 想回到这页点左上角「📖 功能介绍」*`;
function q(s){return String(s).replace(/\\/g,'\\\\').replace(/'/g,"\\'")}
// h(): HTML 内容转义(防注入); q(): onclick 参数转义。两者不可互替。
function h(s){return String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;')}
async function load(silent){try{DATA=await(await fetch('/api/tree')).json();renderSide();
  if(view==='cockpit'){renderCockpit();return}
  if(view==='readme'){if(!silent)renderReadme();return}
  if(!cur){renderCockpit();return}
  if(silent&&(drillSub||tab==='doc'))return; // 别打断正在看的文档(点🔄手动刷新)
  render();}catch(e){}}
function showTabs(on){const t=document.getElementById('tabs');if(t)t.style.display=on?'':'none'}
function selCockpit(){view='cockpit';cur=null;drillState=null;drillSub=null;renderCockpit()}
function selReadme(){view='readme';cur=null;drillState=null;drillSub=null;renderReadme()}
function renderReadme(){view='readme';renderSide();showTabs(false);
 document.getElementById('ptitle').textContent='科研流水线 · 功能介绍';
 document.getElementById('psub').innerHTML='<span class="dot"></span>本地运行 · 零依赖 · 自动刷新';
 document.getElementById('content').innerHTML='<div class="subpanel"><div class="mdbox">'+md(README)+'</div></div>'}
function renderSide(){const by={};DATA.projects.forEach(p=>(by[p.line]=by[p.line]||[]).push(p));
 let h=`<div class="proj cockpitnav ${view==='cockpit'?'active':''}" onclick="selCockpit()">🚀 今日驾驶舱</div>`;
 h+=`<div class="proj rdm ${view==='readme'?'active':''}" onclick="selReadme()">📖 功能介绍 (读我)</div>`;
 LO.forEach(l=>{if(!by[l])return;h+=`<div class="line">${LI[l]||''} ${l}</div>`;
  by[l].forEach(p=>{const tc=p.task_counts||{};const badge=(tc.todo||tc.doing||tc.blocked)?`<span class="tbadge">${(tc.todo||0)+(tc.doing||0)}${tc.blocked?' ⚠'+tc.blocked:''}</span>`:'';
   h+=`<div class="proj ${(p.name===cur&&view==='project')?'active':''}" onclick="sel('${q(p.name)}')">${p.title_cn}${badge}<div class="meta">${p.state.current||''} · v${p.versions}</div></div>`})});
 document.getElementById('sidebar').innerHTML=h}
function sel(n){view='project';cur=n;tab='ov';drillState=null;drillSub=null;curFile=null;setTab('ov')}
function setTab(t){tab=t;drillState=null;drillSub=null;showTabs(true);
 ['ov','task','doc'].forEach(x=>{const e=document.getElementById('tab-'+x);if(e)e.classList.toggle('active',t===x)});
 render()}
function refresh(){load();const b=document.getElementById('refbtn');if(b){b.textContent='🔄 已刷新';setTimeout(()=>b.textContent='🔄 刷新',1200)}}
function P(){return DATA.projects.find(x=>x.name===cur)}
function render(){const p=P();if(!p){selCockpit();return}
 document.getElementById('ptitle').textContent=p.title_cn;
 document.getElementById('psub').innerHTML=`<span class="dot"></span>${p.line} · 当前: ${p.state.current||'?'} · v${p.versions}`;
 renderSide();showTabs(true);
 if(tab==='task'){renderTaskPool(p);return}
 if(tab==='ov'){drillSub?renderSubPanel(p):drillState?renderStatePanel(p):renderOverview(p)}else renderDocs(p)}
function ssOf(p,name){return (p.state.substeps&&p.state.substeps[name])||'todo'}
function renderOverview(p){
 let h=`<div class="ovpanel"><div class="t">📋 项目概况 (原始信息)</div><div class="s"><b>${p.title_cn}</b><br>${p.state.summary||''}<br><br>${p.state.note||''}</div></div>`;
 h+='<div class="flow">';
 DATA.flow.forEach((b,i)=>{const st=p.state.blocks[b.key]||'todo';
  const stt=st==='doing'?'进行中':st==='done'?'已完成':'未开始';
  h+=`<div class="fblock ${st}" onclick="drill('${q(b.key)}')"><div class="bt">${b.key}</div><span class="bs ${st}">${stt}</span>`;
  b.subs.forEach(s=>{const ss=ssOf(p,s.name);h+=`<div class="step"><span class="sdot ${ss}"></span>${s.name}</div>`});
  h+='<div class="enter">点击进入 →</div></div>';
  if(i<DATA.flow.length-1)h+='<span class="arrow">→</span>'});
 h+='</div>';
 document.getElementById('content').innerHTML=h}
function drill(k){drillState=k;render()}
function docOf(p,name){return (p.state.substep_docs&&p.state.substep_docs[name])||''}
function renderStatePanel(p){const b=DATA.flow.find(x=>x.key===drillState);if(!b){drillState=null;return renderOverview(p)}
 let h=`<div class="crumb"><a onclick="backOv()">状态总览</a> &nbsp;›&nbsp; ${b.key} <button id="refbtn" class="refbtn" onclick="refresh()">🔄 刷新</button></div>`;
 b.subs.forEach(s=>{const ss=ssOf(p,s.name);const st=ss==='doing'?'进行中':ss==='done'?'已完成':'未开始';
   const hasDoc=docOf(p,s.name);
   h+=`<div class="subcard ${ss}" onclick="drillIn('${q(s.name)}')"><div class="sh"><h3>${s.name}</h3><span class="badge ${ss}">${st}</span><span class="entr">${hasDoc?'打开标准文档 →':'点击进入 →'}</span></div><div class="tpl-t">标准模板要点</div>`;
   s.tpl.forEach(t=>h+=`<div class="tpl">${t}</div>`);
   h+='</div>'});
 document.getElementById('content').innerHTML=h}
function backOv(){drillState=null;drillSub=null;render()}
function backState(){drillSub=null;render()}
function drillIn(name){drillSub=name;render()}
async function renderSubPanel(p){const b=DATA.flow.find(x=>x.key===drillState);const s=b&&b.subs.find(x=>x.name===drillSub);
 if(!s){drillSub=null;return renderStatePanel(p)}
 const ss=ssOf(p,drillSub);const st=ss==='doing'?'进行中':ss==='done'?'已完成':'未开始';
 const dp=docOf(p,drillSub);
 let h=`<div class="crumb"><a onclick="backOv()">状态总览</a> &nbsp;›&nbsp; <a onclick="backState()">${b.key}</a> &nbsp;›&nbsp; ${drillSub} <span class="badge ${ss}">${st}</span><button id="refbtn" class="refbtn" onclick="refresh()">🔄 刷新</button></div>`;
 h+=`<div class="subpanel"><div id="mdbox" class="mdbox"><div class="nofile">加载中…</div></div></div>`;
 document.getElementById('content').innerHTML=h;
 const box=document.getElementById('mdbox');
 if(!dp){box.innerHTML='<div class="nofile">这一步还没有标准文档。本地在项目目录建一个 md，并在 state.json 的 substep_docs 里登记「'+drillSub+'」即可显示。</div>';return}
 try{const j=await(await fetch('/api/file?path='+encodeURIComponent(p.name+'/'+dp))).json();
   if(j.type==='binary'){box.innerHTML='<div class="nofile">'+j.note+'</div>'}
   else{box.innerHTML='<div class="docpath">📄 '+dp+'</div>'+md(j.content)}}
 catch(e){box.innerHTML='<div class="nofile">读取失败：'+dp+'</div>'}}
// 网页能直接渲染的文本类; Word/PDF/HTML 等打不开的 → 原始素材
const OPEN_EXT=["md","txt","csv","tex","json","py"];
// 按"文件所在文件夹"把文件归到 4 阶段之一; 归不了→null(未归类)
function stageOfFile(f){
  for(const b of DATA.flow){ if(f.rel.includes(b.key)) return b.key; }
  const low=f.rel.toLowerCase();
  for(const b of DATA.flow){ for(const s of b.subs){ if(low.includes(s.name.toLowerCase())) return b.key; } }
  const m=low.match(/(?:^|\/)stages\/(\d+)_/);
  if(m){const n=+m[1]; return DATA.flow[n<=3?0:n<=5?1:n<=7?2:3].key;}
  return null;
}
function selDoc(t){docSel=t;curFile=(t==='__all__')?null:t;renderDocs(P())}
function toggleGroup(k){openGroups[k]=(openGroups[k]===false);renderDocs(P())}
function setDocCat(c){docCat=c;docSel=(c==='org')?'__all__':null;renderDocs(P())}
function renderDocs(p){
 // 顶部横向大分类标签
 let h=`<div class="docbar">
   <div class="docbtn ${docCat==='org'?'active':''}" onclick="setDocCat('org')">归纳整理版</div>
   <div class="docbtn ${docCat==='raw'?'active':''}" onclick="setDocCat('raw')">📎 原始素材</div>
   <div class="docbtn tpl ${docCat==='tpl'?'active':''}" onclick="setDocCat('tpl')">⚙ 模板·设置</div>
   <button id="refbtn" class="refbtn" onclick="refresh()" style="margin-left:auto">🔄 刷新</button>
 </div>`;
 if(docCat==='tpl'){
   h+=`<div class="tplpanel"><div class="tplbadge">功能未上线</div><div class="big">⚙ 模板 · 设置</div>以后在这里给每个阶段(选题立项 / 实验执行 / 成文 / 投稿发表)指定用哪份标准模板。<br>正在设计中，敬请期待。</div>`;
   document.getElementById('content').innerHTML=h;return}
 if(docCat==='raw'){
   const raw=p.files.filter(f=>!OPEN_EXT.includes(f.ext));
   h+='<div class="docview"><div class="flist">';
   h+=`<div class="doccat"><span>📎 原始素材 (Word/PDF/HTML 等，网页打不开)</span></div>`;
   if(raw.length){raw.forEach(f=>h+=`<div class="f ${docSel===f.path?'active':''}" onclick="selDoc('${q(f.path)}')"><span>${f.rel}</span><span class="ext">${f.ext||'?'}</span></div>`)}
   else h+='<div class="nofile">暂无原始素材</div>';
   h+='</div><div class="viewer mdbox" id="viewer"></div></div>';
   document.getElementById('content').innerHTML=h;
   const v=document.getElementById('viewer');
   if(docSel&&docSel!=='__all__')renderOneDoc(docSel);else v.innerHTML='<div class="empty">← 选一个素材</div>';
   return}
 // docCat==='org' 归纳整理版: 全文档 + 4 阶段(按文件夹归类) + 未归类
 const txt=p.files.filter(f=>OPEN_EXT.includes(f.ext));
 h+='<div class="docview"><div class="flist">';
 h+=`<div class="doccat"><span>📁 ${p.title_cn} · 源文件按阶段归类</span></div>`;
 h+=`<div class="f allf ${docSel==='__all__'?'active':''}" onclick="selDoc('__all__')">📄 全文档 (概况)</div>`;
 const fileRow=f=>`<div class="f sub ${docSel===f.path?'active':''}" onclick="selDoc('${q(f.path)}')"><span>${f.rel}</span><span class="ext">${f.ext||'?'}</span></div>`;
 DATA.flow.forEach(b=>{const op=openGroups[b.key]!==false;const fs=txt.filter(f=>stageOfFile(f)===b.key);
   h+=`<div class="grp" onclick="toggleGroup('${q(b.key)}')"><span class="caret">${op?'▾':'▸'}</span> ${b.key} <span class="gcnt">${fs.length}</span></div>`;
   if(op){ h+= fs.length? fs.map(fileRow).join('') : '<div class="nofile sub">无文件</div>'; }});
 // 第五标签: 未归类
 const un=txt.filter(f=>!stageOfFile(f));const uo=openGroups['__un__']!==false;
 h+=`<div class="grp" onclick="toggleGroup('__un__')"><span class="caret">${uo?'▾':'▸'}</span> 📂 未归类 <span class="gcnt">${un.length}</span></div>`;
 if(uo){ h+= un.length? un.map(fileRow).join('') : '<div class="nofile sub">无文件</div>'; }
 h+='</div><div class="viewer mdbox" id="viewer"></div></div>';
 document.getElementById('content').innerHTML=h;
 if(docSel==='__all__')renderAllDoc(p);else renderOneDoc(docSel)}
async function renderAllDoc(p){const v=document.getElementById('viewer');if(!v)return;
 let head='# '+p.title_cn+'\n\n> '+(p.state.summary||'')+'\n\n'+(p.state.note?'**当前**：'+p.state.note:'');
 v.innerHTML=md(head)+'<div class="nofile">聚合各环节文档中…</div>';
 const tasks=[];DATA.flow.forEach(b=>b.subs.forEach(s=>{const dp=docOf(p,s.name);if(dp)tasks.push({stage:b.key,name:s.name,path:p.name+'/'+dp})}));
 let body=head+'\n\n';
 for(const t of tasks){try{const j=await(await fetch('/api/file?path='+encodeURIComponent(t.path))).json();
   if(j.type==='text')body+='\n\n---\n\n## 〔'+t.stage+'〕'+t.name+'\n\n'+j.content}catch(e){}}
 if(docSel==='__all__')v.innerHTML=md(body)}
async function renderOneDoc(fp){const v=document.getElementById('viewer');if(!v)return;
 v.innerHTML='<div class="nofile">加载中…</div>';
 try{const j=await(await fetch('/api/file?path='+encodeURIComponent(fp))).json();
   if(docSel!==fp)return;
   if(j.type==='binary'){v.innerHTML='<div class="empty">'+j.note+'</div>';return}
   v.innerHTML='<div class="docpath">📄 '+fp+'</div>'+(j.ext==='md'?md(j.content):'<pre><code>'+esc(j.content)+'</code></pre>')}
 catch(e){v.innerHTML='<div class="empty">读取失败</div>'}}
function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
function md(s){s=esc(s);const L=s.split('\n');let o=[],c=false;
 for(let ln of L){if(ln.trim().startsWith('```')){o.push(c?'</code></pre>':'<pre><code>');c=!c;continue}if(c){o.push(ln);continue}
  ln=ln.replace(/\*\*(.+?)\*\*/g,'<b>$1</b>').replace(/`(.+?)`/g,'<code>$1</code>');
  if(/^#### /.test(ln)){o.push('<h3>'+ln.slice(5)+'</h3>')}else if(/^### /.test(ln)){o.push('<h3>'+ln.slice(4)+'</h3>')}
  else if(/^## /.test(ln)){o.push('<h2>'+ln.slice(3)+'</h2>')}else if(/^# /.test(ln)){o.push('<h1>'+ln.slice(2)+'</h1>')}
  else if(/^[-*] /.test(ln)){o.push('<li>'+ln.slice(2)+'</li>')}else if(/^\d+\. /.test(ln)){o.push('<li>'+ln.replace(/^\d+\. /,'')+'</li>')}
  else if(ln.trim()===''){o.push('<br>')}else{o.push('<p>'+ln+'</p>')}}return o.join('')}
function applyTheme(t){document.body.classList.toggle('light',t==='light');try{localStorage.setItem('rp_theme',t)}catch(e){}
 const b=document.getElementById('themebtn');if(b)b.textContent=(t==='light')?'🌙 夜间':'☀️ 日间'}
function toggleTheme(){applyTheme(document.body.classList.contains('light')?'dark':'light')}
try{applyTheme(localStorage.getItem('rp_theme')||'dark')}catch(e){applyTheme('dark')}
// ===== v3.1 Daily Cockpit =====
const PRIO={P0:'#f85149',P1:'#d29922',P2:'#3fb950',P3:'#7d8da5'};
const ENERGY={low:'🟢低',medium:'🟡中',high:'🔴高'};
function taskCard(sel){const t=sel.task;const ptt=h(sel.project_title||sel.project);const role=h(sel.role);
 if(!t)return `<div class="tcard"><div class="th"><b>${ptt}</b><span class="role ${role}">${role}</span></div><div class="nofile">任务 ${h(sel.task_id)} 在该项目任务池里没找到（占位）。检查 tasks.json。</div>${sel.why_today?'<div class="why">📍 今天做：'+h(sel.why_today)+'</div>':''}</div>`;
 const st=t.status||'todo';
 return `<div class="tcard">
   <div class="th"><span class="proj-tag">${ptt}</span><span class="role ${role}">${role}</span>
     <span class="pr" style="color:${PRIO[t.priority]||'#7d8da5'}">${h(t.priority||'P2')}</span>
     <span class="en">${ENERGY[t.energy]||''}</span><span class="stt ${h(st)}">${h(st)}</span></div>
   <div class="ttl">${h(t.title)}</div>
   ${sel.why_today?`<div class="why">📍 为什么今天做：${h(sel.why_today)}</div>`:(t.why?`<div class="why">📍 ${h(t.why)}</div>`:'')}
   <div class="trow"><span class="lab">▶ 最小启动</span>${t.starter?h(t.starter):'<i>暂无启动动作</i>'}</div>
   <div class="trow"><span class="lab">🎯 实际动作</span>${t.action?h(t.action):'<i>—</i>'}</div>
   <div class="trow"><span class="lab">✅ 完成标准</span>${t.done_criteria?h(t.done_criteria):'<i>暂无完成标准</i>'}</div>
   ${t.blocker?`<div class="trow blk"><span class="lab">⛔ 卡在</span>${h(t.blocker)}</div>`:''}
 </div>`;}
function renderCockpit(){view='cockpit';renderSide();showTabs(false);
 const T=DATA.today||{};const sel=T.selected_tasks||[];
 document.getElementById('ptitle').textContent='🚀 今日科研驾驶舱';
 document.getElementById('psub').innerHTML='<span class="dot"></span>今天只推进 1–3 件事 · 完成最小启动也算推进';
 let o='<div class="cockpit">';
 // 顶部低压力提示
 o+=`<div class="ckmsg">${h(T.message||'今天只推进 1–3 件事。完成启动动作也算推进。')}</div>`;
 if(!T.configured){
   o+=`<div class="ckempty">📭 ${h(T.message||'暂无今日任务')}<div class="hint">可在 planner/today.json 添加，或用 prompts/daily_planner.md 让 Agent 生成今日任务。</div></div>`;
 }else{
   const main=sel.filter(s=>s.role==='main');
   const sec=sel.filter(s=>['secondary','experiment','thesis'].includes(s.role));
   const fb=sel.filter(s=>s.role==='fallback');
   const other=sel.filter(s=>!['main','secondary','experiment','thesis','fallback'].includes(s.role));
   if(main.length){o+='<div class="cksec"><div class="ckh">🎯 主任务</div>'+main.map(taskCard).join('')+'</div>'}
   if(sec.length){o+='<div class="cksec"><div class="ckh">📎 次任务</div>'+sec.map(taskCard).join('')+'</div>'}
   if(fb.length){o+='<div class="cksec"><div class="ckh">🛟 保底任务（不断线即可）</div>'+fb.map(taskCard).join('')+'</div>'}
   if(other.length){o+='<div class="cksec">'+other.map(taskCard).join('')+'</div>'}
   if(T.hidden_count>0)o+=`<div class="hint">其余 ${T.hidden_count} 个任务已隐藏，避免过载。</div>`;
   o+='<div class="ckfoot">完成「最小启动」也算推进。不要求完美，先让任务重新动起来。</div>';
 }
 // 最近完成 / 正反馈
 const wins=(T.recent_wins||[]).slice(0,5);const dl=(DATA.done_log||[]).slice(-5).reverse();
 if(wins.length||dl.length){
   o+='<div class="cksec"><div class="ckh">🌱 最近完成（正反馈）</div><div class="wins">';
   wins.forEach(w=>o+=`<div class="win">✅ ${h(w)}</div>`);
   dl.forEach(r=>o+=`<div class="win">✅ <span class="wd">${h(r.date||'')}</span> ${h(r.note||r.task_id||'')}${r.result==='progress'?' <span class="prog">(推进)</span>':''}</div>`);
   o+='</div></div>';
 }
 // 当前卡住
 const blocked=[];DATA.projects.forEach(p=>(p.tasks||[]).forEach(t=>{if((t.status||'')==='blocked')blocked.push({p:p.title_cn,t})}));
 if(blocked.length){o+='<div class="cksec"><div class="ckh">⛔ 当前卡住</div>';
   blocked.slice(0,5).forEach(b=>o+=`<div class="blkrow"><b>${h(b.p)}</b> · ${h(b.t.title)} <span class="bk">${h(b.t.blocker||'')}</span></div>`);o+='</div>';}
 // 项目任务概览
 const withTasks=DATA.projects.filter(p=>p.tasks&&p.tasks.length);
 if(withTasks.length){o+='<div class="cksec"><div class="ckh">📊 项目任务概览</div><div class="ovgrid">';
   withTasks.forEach(p=>{const c=p.task_counts||{};
     o+=`<div class="ovcard" onclick="sel('${q(p.name)}')"><div class="ovt">${h(p.title_cn)}</div><div class="ovc"><span>待办 ${c.todo||0}</span><span>进行 ${c.doing||0}</span>${c.blocked?`<span class="bk">卡 ${c.blocked}</span>`:''}<span class="dn">完成 ${c.done||0}</span></div></div>`;});
   o+='</div></div>';}
 o+='</div>';
 document.getElementById('content').innerHTML=o;}
function renderTaskPool(p){const tasks=p.tasks||[];
 const by=s=>tasks.filter(t=>(t.status||'todo')===s);
 const sec=(title,arr,emptymsg)=>{if(!arr.length)return emptymsg?`<div class="cksec"><div class="ckh">${title}</div><div class="nofile">${emptymsg}</div></div>`:'';
   return `<div class="cksec"><div class="ckh">${title} <span class="cnt">${arr.length}</span></div>`+arr.map(t=>poolCard(t)).join('')+'</div>';};
 let o='<div class="cockpit">';
 const pf=(DATA.profiles||{})[p.line];
 if(pf)o+=`<div class="ckmsg">📐 模板：${h(pf.label||pf.profile)} · ${h(pf.planner_hint||pf.desc||'')}</div>`;
 if(!tasks.length){o+=`<div class="ckempty">📭 该项目暂无任务池<div class="hint">在 projects/${h(p.name)}/tasks.json 添加任务，或用 prompts/revision_task_splitter.md 从审稿意见生成。</div></div>`;}
 else{
   o+=sec('🔵 进行中',by('doing'));
   o+=sec('⚪ 待办',by('todo'));
   o+=sec('⛔ 卡住',by('blocked'));
   const done=by('done');if(done.length)o+=sec('✅ 最近完成',done.slice(0,5));
 }
 o+='</div>';
 document.getElementById('content').innerHTML=o;}
function poolCard(t){const st=t.status||'todo';
 return `<div class="tcard">
   <div class="th"><span class="pr" style="color:${PRIO[t.priority]||'#7d8da5'}">${h(t.priority||'P2')}</span>
     <span class="en">${ENERGY[t.energy]||''}</span><span class="stt ${h(st)}">${h(st)}</span>
     ${t.stage?`<span class="proj-tag">${h(t.stage)}${t.substep?' · '+h(t.substep):''}</span>`:''}</div>
   <div class="ttl">${h(t.title)}</div>
   <div class="trow"><span class="lab">▶ 最小启动</span>${t.starter?h(t.starter):'<i>暂无启动动作</i>'}</div>
   <div class="trow"><span class="lab">✅ 完成标准</span>${t.done_criteria?h(t.done_criteria):'<i>暂无完成标准</i>'}</div>
   ${t.blocker?`<div class="trow blk"><span class="lab">⛔ 卡在</span>${h(t.blocker)}</div>`:''}
 </div>`;}
load();setInterval(()=>load(true),5000);
</script></body></html>"""

if __name__=="__main__":
    print(f"🔬 科研流水线 v3.1 Daily Cockpit: http://localhost:{PORT}")
    HTTPServer(("127.0.0.1",PORT),H).serve_forever()
