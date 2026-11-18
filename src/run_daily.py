import argparse
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")
from src.ado_client import AdoClient
from src.ranker import rank_items
from src.claude_summarizer import summarize
from src.email_sender import build_email, send_email

def required(name):
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required setting: {name} (check your .env file)")
    return value

def main():
    parser = argparse.ArgumentParser(description="Generate and email an ADO daily to-do digest.")
    parser.add_argument("--test-ado", action="store_true")
    parser.add_argument("--preview", action="store_true", help="Print digest and do not send email")
    parser.add_argument("--send-test-email", action="store_true")
    parser.add_argument("--serve", action="store_true", help="Host the digest as a styled web page on localhost")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    logdir = ROOT / "logs"
    logdir.mkdir(exist_ok=True)
    logging.basicConfig(filename=logdir / "agent.log", level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    client = AdoClient(
        required("ADO_ORGANIZATION"), required("ADO_PROJECT"), required("ADO_PAT"),
        os.getenv("ADO_ASSIGNED_TO", ""),
        os.getenv("ADO_TEAM_PROJECT_FILTER", "true").lower() == "true"
    )
    if args.test_ado:
        client.test_connection()
        print("ADO connection successful.")
        return
    if args.send_test_email:
        subject, html = build_email(os.getenv("ADO_PROJECT", "ADO"), [], {}, os.getenv("EMAIL_SUBJECT_PREFIX", "[ADO Daily To-Do]"))
        send_email(required("SMTP_HOST"), os.getenv("SMTP_PORT", "587"), required("SMTP_USERNAME"),
                   required("SMTP_PASSWORD"), required("EMAIL_FROM"), required("EMAIL_TO"), subject, html)
        print("Test email sent.")
        return

    def collect(prioritized_only=False):
        excluded = [x.strip() for x in os.getenv("ADO_EXCLUDED_STATES", "Closed,Removed,Done").split(",") if x.strip()]
        ranked = rank_items(client.fetch_items(excluded))
        if prioritized_only:
            # Email: leave out items with no priority set (they live in the web page's "No priority" tab).
            ranked = [i for i in ranked if i.get("priority") not in (None, "")]
            for position, item in enumerate(ranked, 1):
                item["rank"] = position
        ranked = ranked[:int(os.getenv("MAX_ITEMS_IN_EMAIL", "50"))]
        sums = summarize(
            ranked, os.getenv("ADO_PROJECT", ""),
            os.getenv("CLAUDE_COMMAND", "claude"), os.getenv("CLAUDE_MODEL", "sonnet"),
            int(os.getenv("CLAUDE_TIMEOUT_SECONDS", "180")),
            os.getenv("USE_CLAUDE", "true").lower() == "true"
        )
        return ranked, sums

    if args.serve:
        from src.web_report import build_page, serve
        def generate():
            print("Fetching work items from ADO and summarizing...", flush=True)
            ranked, sums = collect()
            days = int(os.getenv("COMPLETED_LOOKBACK_DAYS", "30"))
            completed = client.fetch_completed_items(days)
            print(f"Loaded {len(ranked)} to-do and {len(completed)} completed work item(s).", flush=True)
            return build_page(os.getenv("ADO_PROJECT", ""), ranked, sums,
                              completed=completed, completed_days=days)
        serve(generate, port=args.port)
        return

    items, summaries = collect(prioritized_only=True)
    subject, html = build_email(os.getenv("ADO_PROJECT", ""), items, summaries,
                                os.getenv("EMAIL_SUBJECT_PREFIX", "[ADO Daily To-Do]"))
    if args.preview:
        from html import unescape
        import re
        print(unescape(re.sub("<[^>]+>", " ", html)))
        return
    send_email(required("SMTP_HOST"), os.getenv("SMTP_PORT", "587"), required("SMTP_USERNAME"),
               required("SMTP_PASSWORD"), required("EMAIL_FROM"), required("EMAIL_TO"), subject, html)
    logging.info("Digest sent with %d items", len(items))
    print(f"Digest sent with {len(items)} work item(s).")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logging.exception("Daily digest failed")
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
