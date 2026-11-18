import smtplib
from email.message import EmailMessage
from html import escape

def build_email(project, items, summaries, subject_prefix):
    subject = f"{subject_prefix} {project} - {len(items)} assigned item(s)"
    rows = []
    for item in items:
        s = summaries.get(str(item["id"]), {})
        summary = s.get("summary", "Summary unavailable.")
        action = s.get("next_action", "Review the item and confirm next steps.")
        due = item.get("due_date") or "Not set"
        rows.append(f"""
        <tr>
          <td>{item['rank']}</td>
          <td><a href="{escape(item['url'], quote=True)}">#{item['id']} - {escape(item['title'])}</a><br>
              <small>{escape(item['type'])} | {escape(item.get('state',''))}</small></td>
          <td>{escape(str(item.get('severity') or '—'))}</td>
          <td>{escape(str(item.get('priority') or '—'))}</td>
          <td>{escape(str(due))}<br><small>{escape(item.get('due_status',''))}</small></td>
          <td>{escape(summary)}</td>
          <td>{escape(action)}</td>
        </tr>""")
    body = f"""<html><body>
    <h2>Your Azure DevOps daily to-do list</h2>
    <p><b>Project:</b> {escape(project)} &nbsp; <b>Items:</b> {len(items)}</p>
    <p>Rank order: severity, priority, nearest due/target date, then oldest created date.
    Missing values are placed after populated values for that field.</p>
    {"<table border='1' cellpadding='7' cellspacing='0'><tr><th>#</th><th>Work item</th><th>Severity</th><th>Priority</th><th>Due</th><th>Summary</th><th>Suggested next action</th></tr>" + "".join(rows) + "</table>" if rows else "<p>No active assigned work items were found.</p>"}
    <p><small>Generated automatically. Confirm dates, field conventions, and priority with Azure DevOps.</small></p>
    </body></html>"""
    return subject, body

def send_email(host, port, username, password, sender, recipient, subject, html):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content("Your email client does not support HTML. Please view this message in an HTML-capable client.")
    msg.add_alternative(html, subtype="html")
    with smtplib.SMTP(host, int(port), timeout=30) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(username, password)
        server.send_message(msg)
