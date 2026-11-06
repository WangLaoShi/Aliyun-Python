"""将讲义生成离线阅读页面。构建依赖：python -m pip install markdown。"""
from pathlib import Path
import markdown

ROOT = Path(__file__).resolve().parent
source = (ROOT / "01-Python一篇概全.md").read_text(encoding="utf-8")
md = markdown.Markdown(extensions=["fenced_code", "tables", "toc"], extension_configs={"toc": {"toc_depth": "2-2"}})
body = md.convert(source)
html = '''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Python 一篇概全 · v2610</title>
<style>
:root{color-scheme:light;--ink:#20332f;--muted:#61736d;--line:#dbe5df;--paper:#fffef9;--green:#226b51}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:25px}body{margin:0;background:#f1f5ef;color:var(--ink);font:16px/1.85 system-ui,-apple-system,"PingFang SC",sans-serif}
aside{position:fixed;inset:0 auto 0 0;width:275px;padding:30px 22px;overflow:auto;border-right:1px solid var(--line);background:#f5f8f2}aside strong{display:block;font-size:21px}aside small{color:var(--muted)}aside ul{padding:0;list-style:none}aside li{margin:8px 0}a{color:var(--green);text-decoration:none}aside a{display:block;font-size:14px;padding:5px 8px;border-radius:6px}aside a:hover{background:#e2ecdf}
main{margin-left:275px;padding:40px 6vw 90px;max-width:1330px;background:var(--paper);min-height:100vh}h1{font-size:38px;line-height:1.35;letter-spacing:-1px}h2{margin-top:65px;padding-top:22px;border-top:1px solid var(--line);font-size:27px;line-height:1.5}h3{font-size:19px;margin-top:30px}p,li{max-width:90ch}blockquote{margin:20px 0;padding:12px 22px;background:#edf4e9;border-left:4px solid #86a878;color:var(--muted)}blockquote p{margin:7px 0}pre{background:#152c29;color:#edf8f0;padding:23px;border-radius:10px;overflow:auto;font-size:14px;line-height:1.7}code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}p code,li code,td code{background:#eaf0e6;padding:2px 5px;border-radius:4px}table{display:block;overflow:auto;border-collapse:collapse;width:100%;font-size:14px}td,th{border:1px solid var(--line);padding:11px 14px;text-align:left;min-width:110px}th{background:#edf3e9}.notice{font-size:14px;color:var(--muted);border:1px solid var(--line);padding:12px 16px;border-radius:8px}.top{font-size:12px;letter-spacing:2px;color:var(--green)}
@media(max-width:850px){aside{position:relative;width:auto;max-height:320px;border-bottom:1px solid var(--line)}main{margin:0;padding:25px 20px}h1{font-size:30px}h2{font-size:23px}}
@media print{aside,.notice{display:none}main{margin:0;padding:0;max-width:none}pre{white-space:pre-wrap;color:#111;background:#f2f2f2}h2{break-before:page}body{background:white;font-size:11pt}}
</style><link rel="stylesheet" href="tutorial.css"></head><body><aside><strong>Python 一篇概全</strong><small>第一章 · 交互教程 / v2610</small><p><a href="#usage-guide">开始之前 · 使用说明</a></p>__TOC__</aside>
<main><div class="top">READ · UNDERSTAND · MODIFY · VERIFY</div><p class="notice">先读代码，再修改、运行或向右侧 AI 提问。示例独立运行，部分片段需自行补上前文变量。</p>__USAGE____BODY__</main>
<section id="assistant" aria-label="AI 代码讲解">
<h2>AI 代码讲解</h2><p class="muted">DashScope · qwen-plus · 流式对话</p>
<details open><summary>调用配置</summary><label for="key">百炼 API Key</label><input id="key" type="password" autocomplete="off" placeholder="sk-…（仅保留在当前页面内存）"><div class="row"><button id="forget" type="button">清空 KEY</button><button id="reconnect" type="button">重新连接</button></div><div><span id="connection" class="status" role="status">连接中…</span></div><p class="muted">当前接入为模型调用，代码会随问题发送至百炼。刷新后页面 KEY 清空。</p></details>
<div id="context" class="context"></div><div class="quick"><button type="button" data-prompt="请用一个具体输入逐步解释当前代码。">走读代码</button><button type="button" data-prompt="这段代码有哪些边界情况？给出输入和预期结果。">检查边界</button><button type="button" data-prompt="请出一道类似的练习，先给提示，不要给答案。">给我练习</button><button id="clear" type="button">新对话</button></div>
<div id="messages" role="log" aria-label="对话记录"></div><form id="chat-form"><label for="question">围绕当前代码提问</label><textarea id="question" required placeholder="这段代码中的 return 起什么作用？"></textarea><div class="row"><button id="send" type="submit">发送问题</button><span id="usage" class="status" role="status"></span></div></form>
<details><summary>运行方式说明</summary><p class="run-note">“本机运行”会使用服务的 Python 执行当前代码，具有当前用户的文件与网络权限，并非安全沙箱。仅运行信任的练习代码。每次使用独立临时目录，最长 8 秒；文件不会在练习间保留，图形窗口不适合在此运行。第三方包使用服务所在环境。</p></details>
</section><script src="vendor/highlight.js"></script><script src="vendor/marked.js"></script><script src="vendor/purify.js"></script><script src="tutorial.js"></script></body></html>'''
(ROOT / "index.html").write_text(html.replace("__USAGE__", (ROOT / "usage.html").read_text(encoding="utf-8")).replace("__TOC__", md.toc).replace("__BODY__", body), encoding="utf-8")
print(ROOT / "index.html")
