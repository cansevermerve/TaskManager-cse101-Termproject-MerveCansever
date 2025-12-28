from datetime import datetime
import json
import os


def log_activity(log_path, event):
    logs = []
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
    logs.append(event)
    os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
    with open(log_path, "w") as f:
        json.dump(logs, f, indent=2)


def load_activity(log_path):
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def productivity_stats(tasks, activity_log):
    stats = {
        "tasks_completed": 0,
        "avg_completion_days": 0,
        "category_trends": {},
        "completed_per_week": {}
    }

    completed_times = []

    for t in tasks:
        if t.get("status") == "completed":
            stats["tasks_completed"] += 1
            created = datetime.fromisoformat(t["created_at"])
            updated = datetime.fromisoformat(t["updated_at"])
            completed_times.append((updated - created).days)
            category = t.get("category", "Uncategorized")
            stats["category_trends"][category] = stats["category_trends"].get(category, 0) + 1

    if completed_times:
        stats["avg_completion_days"] = sum(completed_times) / len(completed_times)

    for event in activity_log:
        action = event.get("action")
        if action not in ("completed", "status_change"):
            continue
        if action == "status_change" and event.get("new_status") != "completed":
            continue
        ts_str = event.get("timestamp")
        if not ts_str:
            continue
        try:
            ts = datetime.fromisoformat(ts_str)
        except ValueError:
            continue
        year, week, _ = ts.isocalendar()
        key = f"{year}-W{week:02d}"
        stats["completed_per_week"][key] = stats["completed_per_week"].get(key, 0) + 1

    return stats


def export_report(report, filename):
    base_dir = "reports"
    os.makedirs(base_dir, exist_ok=True)
    path = os.path.join(base_dir, filename)
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    return path
