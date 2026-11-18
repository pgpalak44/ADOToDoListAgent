from datetime import datetime, timezone

def _date(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None

def _number(value, missing=999):
    try:
        return float(value)
    except (TypeError, ValueError):
        return missing

def rank_items(items):
    """Sort severity (1 highest), priority (1 highest), nearest due date, oldest created."""
    now = datetime.now(timezone.utc)
    def key(item):
        severity = _number(item.get("severity"))
        # Severity is meaningful primarily for Bugs; missing values sort last.
        priority = _number(item.get("priority"))
        due = _date(item.get("due_date"))
        created = _date(item.get("created_date"))
        due_key = due.timestamp() if due else float("inf")
        created_key = created.timestamp() if created else float("inf")
        return (severity, priority, due_key, created_key, int(item.get("id", 0)))
    ranked = sorted(items, key=key)
    for index, item in enumerate(ranked, 1):
        item["rank"] = index
        due = _date(item.get("due_date"))
        item["due_status"] = (
            "Overdue" if due and due.date() < now.date()
            else "Due today" if due and due.date() == now.date()
            else "Upcoming" if due else "No due date"
        )
    return ranked
