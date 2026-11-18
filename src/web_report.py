"""Styled HTML dashboard for the daily digest, served on localhost."""
from datetime import datetime
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CSS = """
:root{--bg:#f5f7fb;--card:#fff;--text:#1d2433;--muted:#5f6b7f;--border:#e3e8f0;--accent:#0b63ce;
--red:#c62828;--red-bg:#fdecea;--amber:#a15c00;--amber-bg:#fff4e0;--green:#1b7a3d;--green-bg:#e7f6ec;
--gray-bg:#eef1f5;--shadow:0 1px 3px rgba(16,24,40,.06),0 1px 2px rgba(16,24,40,.04)}
@media (prefers-color-scheme:dark){:root{--bg:#0f141c;--card:#171e29;--text:#e6ebf2;--muted:#9aa6b8;
--border:#273142;--accent:#5aa2ff;--red:#ff8a80;--red-bg:#3a1c1c;--amber:#ffc266;--amber-bg:#3a2c12;
--green:#7fd89a;--green-bg:#15301f;--gray-bg:#222b38}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 "Segoe UI",system-ui,-apple-system,sans-serif}
.wrap{max-width:1200px;margin:0 auto;padding:28px 16px 48px}
header{display:flex;flex-wrap:wrap;gap:12px;justify-content:space-between;align-items:flex-end;margin-bottom:20px}
h1{margin:0;font-size:26px;letter-spacing:-.01em}
.sub{color:var(--muted);margin-top:4px}
.btn{background:var(--accent);color:#fff;border:0;border-radius:8px;padding:9px 16px;font-weight:600;
text-decoration:none;cursor:pointer}
.btn:hover{filter:brightness(1.08)}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:20px}
.stat{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px 16px;box-shadow:var(--shadow)}
.stat .n{font-size:28px;font-weight:700}
.stat .l{color:var(--muted);font-size:13px}
.tabs{display:flex;gap:4px;border-bottom:1px solid var(--border);margin-bottom:16px}
.tab{background:none;border:0;border-bottom:3px solid transparent;padding:10px 16px;font:inherit;font-weight:600;
color:var(--muted);cursor:pointer;margin-bottom:-1px}
.tab:hover{color:var(--text)}
.tab.on{color:var(--accent);border-bottom-color:var(--accent)}
.tab .count{display:inline-block;min-width:22px;padding:0 7px;margin-left:4px;border-radius:999px;
background:var(--gray-bg);color:var(--muted);font-size:12px;text-align:center}
.tab.on .count{background:var(--accent);color:#fff}
.chips{display:contents}
[hidden]{display:none !important}
.item.done{border-left-color:var(--green)}
.item.done .rank{background:var(--green-bg);color:var(--green)}
.item.done .title{color:var(--muted)}
.note{color:var(--muted);font-size:13px;margin:0 0 4px}
.toolbar{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px}
.toolbar input{flex:1;min-width:200px;padding:9px 12px;border:1px solid var(--border);border-radius:8px;
background:var(--card);color:var(--text);font:inherit}
.chip{border:1px solid var(--border);background:var(--card);color:var(--text);border-radius:999px;
padding:7px 14px;cursor:pointer;font:inherit;font-size:13px}
.chip.on{background:var(--accent);border-color:var(--accent);color:#fff}
.list{display:flex;flex-direction:column;gap:12px}
.item{background:var(--card);border:1px solid var(--border);border-left:4px solid var(--border);border-radius:12px;
padding:16px 18px;box-shadow:var(--shadow);display:grid;grid-template-columns:44px 1fr;gap:14px}
.item.overdue{border-left-color:var(--red)}.item.today{border-left-color:var(--amber)}
.item.upcoming{border-left-color:var(--green)}
.rank{width:36px;height:36px;border-radius:50%;background:var(--gray-bg);display:grid;place-items:center;
font-weight:700;color:var(--muted)}
.head{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.ticon{display:inline-grid;place-items:center;width:28px;height:28px;border-radius:7px;flex:none;
background:color-mix(in srgb,currentColor 14%,transparent)}
.wid{color:var(--muted);font-size:13px;font-variant-numeric:tabular-nums}
.title{font-size:16px;font-weight:600;color:var(--text);text-decoration:none}
.title:hover{color:var(--accent);text-decoration:underline}
.meta{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0 10px}
.tag{font-size:12px;padding:2px 9px;border-radius:999px;background:var(--gray-bg);color:var(--muted);white-space:nowrap}
.tag.red{background:var(--red-bg);color:var(--red)}.tag.amber{background:var(--amber-bg);color:var(--amber)}
.tag.green{background:var(--green-bg);color:var(--green)}
.summary{margin:0 0 8px}
.next{margin:0;padding:8px 12px;border-radius:8px;background:var(--gray-bg);font-size:14px}
.next b{color:var(--accent)}
.empty{text-align:center;padding:48px;color:var(--muted);background:var(--card);border-radius:12px;border:1px dashed var(--border)}
footer{color:var(--muted);font-size:12px;margin-top:24px}
@media (max-width:600px){.item{grid-template-columns:1fr}.rank{width:30px;height:30px}}
"""

JS = """
const q=document.getElementById('q'),chips=[...document.querySelectorAll('.chip')];let f='all';
function apply(){const t=q.value.toLowerCase();document.querySelectorAll('.item').forEach(e=>{
const okF=f==='all'||e.dataset.status===f||e.dataset.status==='done';const okT=!t||e.textContent.toLowerCase().includes(t);
e.style.display=okF&&okT?'':'none'})}
q.addEventListener('input',apply);
chips.forEach(c=>c.addEventListener('click',()=>{chips.forEach(x=>x.classList.remove('on'));c.classList.add('on');f=c.dataset.f;apply()}));
const tabs=[...document.querySelectorAll('.tab')];
function show(name){tabs.forEach(b=>{const on=b.dataset.tab===name;b.classList.toggle('on',on);b.setAttribute('aria-selected',on)});
document.querySelectorAll('.panel').forEach(p=>p.hidden=p.id!=='panel-'+name);
document.querySelector('.chips').hidden=name==='completed';
document.querySelector('.stats').hidden=name!=='todo';
q.value='';f='all';chips.forEach(x=>x.classList.toggle('on',x.dataset.f==='all'));apply();
if(location.hash!=='#'+name)history.replaceState(null,'','#'+name);
try{localStorage.setItem('adoTab',name)}catch(e){}}
tabs.forEach(b=>b.addEventListener('click',()=>show(b.dataset.tab)));
let start='todo';try{start=localStorage.getItem('adoTab')||start}catch(e){}
const h=location.hash.slice(1);if(document.getElementById('panel-'+h))start=h;
show(document.getElementById('panel-'+start)?start:'todo');
"""

_SVG = '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true">{}</svg>'
TYPE_ICONS = {  # (colour, svg path) - colours follow Azure DevOps conventions
    "epic": ("#FF7B00", '<path d="M3 7l4.5 4L12 4l4.5 7L21 7l-2 12H5L3 7z"/>'),
    "feature": ("#773B93", '<path d="M7 3h10v3h4v3a5 5 0 0 1-5 5h-.3A5 5 0 0 1 13 16.9V19h3v2H8v-2h3v-2.1A5 5 0 0 1 8.3 14H8a5 5 0 0 1-5-5V6h4V3zm0 5H5v1a3 3 0 0 0 2 2.8V8zm10 0v3.8A3 3 0 0 0 19 9V8h-2z"/>'),
    "user story": ("#009CCC", '<path d="M5 3h11a3 3 0 0 1 3 3v15H8a3 3 0 0 1-3-3V3zm2 2v13a1 1 0 0 0 1 1h9v-2H8V5H7zm3 2v2h6V7h-6zm0 4v2h6v-2h-6z"/>'),
    "product backlog item": ("#009CCC", '<path d="M5 3h11a3 3 0 0 1 3 3v15H8a3 3 0 0 1-3-3V3zm2 2v13a1 1 0 0 0 1 1h9v-2H8V5H7zm3 2v2h6V7h-6zm0 4v2h6v-2h-6z"/>'),
    "task": ("#F2CB1D", '<path d="M9 2h6v2h3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h3V2zm1.5 14.6 6.2-6.2-1.4-1.4-4.8 4.8-2.3-2.3-1.4 1.4 3.7 3.7z"/>'),
    "bug": ("#CC293D", '<path d="M9 4.5 7.6 3.1 9 1.7l1.8 1.8a5 5 0 0 1 2.4 0L15 1.7l1.4 1.4L15 4.5A5 5 0 0 1 17 8h3v2h-3v2h3v2h-3v1a5 5 0 0 1-.2 1H20v2h-4.1a5 5 0 0 1-7.8 0H4v-2h3.2a5 5 0 0 1-.2-1v-1H4v-2h3v-2H4V8h3a5 5 0 0 1 2-3.5zM11 10v8h2v-8h-2z"/>'),
    "issue": ("#B4009E", '<path d="M5 2h2v1h12l-2 5 2 5H7v9H5V2z"/>'),
    "impediment": ("#B4009E", '<path d="M5 2h2v1h12l-2 5 2 5H7v9H5V2z"/>'),
    "test case": ("#004B50", '<path d="M9 2h6v2h-1v5.2l5.6 9.7A2 2 0 0 1 17.9 22H6.1a2 2 0 0 1-1.7-3.1L10 9.2V4H9V2zm-.6 13h7.2l-2.6-4.5V9h-2v1.5L8.4 15z"/>'),
    "test plan": ("#004B50", '<path d="M6 2h12a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2zm1 4v2h2V6H7zm4 0v2h6V6h-6zm-4 5v2h2v-2H7zm4 0v2h6v-2h-6zm-4 5v2h2v-2H7zm4 0v2h6v-2h-6z"/>'),
    "test suite": ("#00809D", '<path d="M3 5h7l2 2h9v12a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5zm7.5 13.1 5.6-5.6-1.4-1.4-4.2 4.2-2-2-1.4 1.4 3.4 3.4z"/>'),
}
_DEFAULT_ICON =("#6B7A90", '<path d="M5 3h10l4 4v14H5V3zm9 1.5V8h3.5L14 4.5z"/>')


def type_icon(work_type):
    colour, path = TYPE_ICONS.get((work_type or "").strip().lower(), _DEFAULT_ICON)
    return (f'<span class="ticon" style="color:{colour}" title="{escape(work_type or "Work item")}">'
            f'{_SVG.format(path)}</span>')


STATUS_CLASS = {"Overdue": ("overdue", "red"), "Due today": ("today", "amber"),
                "Upcoming": ("upcoming", "green"), "No due date": ("none", "")}


def completed_cards(completed):
    cards = []
    for item in completed:
        when = str(item.get("closed_date") or item.get("changed_date") or "")[:10]
        tags = [f'<span class="tag">{escape(item.get("type", ""))}</span>',
                f'<span class="tag green">✓ {escape(item.get("state", ""))}</span>']
        if when:
            tags.append(f'<span class="tag">Closed {escape(when)}</span>')
        if item.get("iteration_path"):
            tags.append(f'<span class="tag">{escape(item["iteration_path"])}</span>')
        cards.append(f"""
<article class="item done" data-status="done">
  <div class="rank">✓</div>
  <div>
    <div class="head">{type_icon(item.get('type'))}<span class="wid">{item['id']}</span>
    <a class="title" href="{escape(item['url'], quote=True)}" target="_blank" rel="noopener">{escape(item['title'])}</a></div>
    <div class="meta">{''.join(tags)}</div>
  </div>
</article>""")
    return "".join(cards)


def has_priority(item):
    return item.get("priority") not in (None, "")


def todo_cards(items, summaries):
    """Cards in the existing rank order; the circle shows the position within this tab."""
    cards = []
    for position, item in enumerate(items, 1):
        s = summaries.get(str(item["id"]), {})
        status = item.get("due_status", "No due date")
        cls, tone = STATUS_CLASS.get(status, ("none", ""))
        tags = [f'<span class="tag">{escape(item.get("type", ""))}</span>']
        if item.get("state"):
            tags.append(f'<span class="tag">{escape(item["state"])}</span>')
        if item.get("severity"):
            tags.append(f'<span class="tag red">Severity {escape(str(item["severity"]))}</span>')
        if item.get("priority"):
            tags.append(f'<span class="tag amber">Priority {escape(str(item["priority"]))}</span>')
        due = item.get("due_date")
        due_txt = f"{status} · {escape(str(due)[:10])}" if due else status
        tags.append(f'<span class="tag {tone}">{escape(due_txt)}</span>')
        if item.get("iteration_path"):
            tags.append(f'<span class="tag">{escape(item["iteration_path"])}</span>')
        cards.append(f"""
<article class="item {cls}" data-status="{cls}">
  <div class="rank">{position}</div>
  <div>
    <div class="head">{type_icon(item.get('type'))}<span class="wid">{item['id']}</span>
    <a class="title" href="{escape(item['url'], quote=True)}" target="_blank" rel="noopener">{escape(item['title'])}</a></div>
    <div class="meta">{''.join(tags)}</div>
    <p class="summary">{escape(s.get('summary', 'Summary unavailable.'))}</p>
    <p class="next"><b>Next:</b> {escape(s.get('next_action', 'Review the item and confirm next steps.'))}</p>
  </div>
</article>""")
    return "".join(cards)


def build_page(project, items, summaries, generated_at=None, completed=None, completed_days=30):
    generated_at = generated_at or datetime.now()
    completed = completed or []
    no_priority = [i for i in items if not has_priority(i)]
    items = [i for i in items if has_priority(i)]
    counts = {k: sum(1 for i in items if i.get("due_status") == k) for k in STATUS_CLASS}
    body = todo_cards(items, summaries) or '<div class="empty">No prioritized work items right now. 🎉</div>'
    no_pri_body = (todo_cards(no_priority, summaries)
                   or '<div class="empty">Every active item has a priority set.</div>')
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ADO Daily To-Do</title><style>{CSS}</style></head><body><div class="wrap">
<header><div><h1>Your Azure DevOps daily to-do</h1>
<div class="sub">Project <b>{escape(project)}</b> · generated {generated_at:%A, %d %b %Y %H:%M}</div></div>
<a class="btn" href="/refresh">↻ Refresh from ADO</a></header>
<section class="stats">
 <div class="stat"><div class="n">{len(items)}</div><div class="l">Active items</div></div>
 <div class="stat"><div class="n" style="color:var(--red)">{counts['Overdue']}</div><div class="l">Overdue</div></div>
 <div class="stat"><div class="n" style="color:var(--amber)">{counts['Due today']}</div><div class="l">Due today</div></div>
 <div class="stat"><div class="n" style="color:var(--green)">{counts['Upcoming']}</div><div class="l">Upcoming</div></div>
 <div class="stat"><div class="n">{counts['No due date']}</div><div class="l">No due date</div></div>
</section>
<nav class="tabs" role="tablist">
 <button class="tab on" role="tab" data-tab="todo">To-do <span class="count">{len(items)}</span></button>
 <button class="tab" role="tab" data-tab="nopriority">No priority <span class="count">{len(no_priority)}</span></button>
 <button class="tab" role="tab" data-tab="completed">Completed <span class="count">{len(completed)}</span></button>
</nav>
<div class="toolbar"><input id="q" type="search" placeholder="Filter by title, type, summary…">
 <span class="chips"><button class="chip on" data-f="all">All</button><button class="chip" data-f="overdue">Overdue</button>
 <button class="chip" data-f="today">Due today</button><button class="chip" data-f="upcoming">Upcoming</button>
 <button class="chip" data-f="none">No due date</button></span></div>
<main class="list panel" id="panel-todo">{body}</main>
<main class="list panel" id="panel-nopriority" hidden>
 <p class="note">Active items with no priority set in Azure DevOps. Set a priority to move them to the To-do tab.</p>
 {no_pri_body}
</main>
<main class="list panel" id="panel-completed" hidden>
 <p class="note">Items assigned to you that reached a completed state in the last {completed_days} days, most recent first.</p>
 {completed_cards(completed) or '<div class="empty">No items completed in this period.</div>'}
</main>
<footer>Rank order: severity, priority, nearest due/target date, then oldest created date. Missing values sort last.
Confirm dates, field conventions and priority in Azure DevOps.</footer>
</div><script>{JS}</script></body></html>"""


def serve(generate, host="127.0.0.1", port=8000):
    """generate() -> HTML string. Called once at start and again on /refresh."""
    state = {"html": generate()}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith("/refresh"):
                try:
                    state["html"] = generate()
                except Exception as exc:  # keep serving the last good page
                    print(f"Refresh failed: {exc}")
                self.send_response(303)
                self.send_header("Location", "/")
                self.end_headers()
                return
            if self.path not in ("/", "/index.html"):
                self.send_error(404)
                return
            data = state["html"].encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Serving ADO daily to-do at http://{host}:{port}  (Ctrl+C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
