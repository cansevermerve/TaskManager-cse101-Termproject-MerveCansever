import json
import os
from datetime import datetime


def validate_task_schema(tasks):
    required = {
        "id",
        "title",
        "description",
        "category",
        "priority",
        "status",
        "due_date",
        "created_at",
        "updated_at",
        "subtasks"
    }
    for t in tasks:
        if not isinstance(t, dict):
            return False
        if not required.issubset(t.keys()):
            return False
        if t.get("due_date"):
            try:
                datetime.strptime(t["due_date"], "%Y-%m-%d")
            except ValueError:
                return False
        try:
            datetime.fromisoformat(t["created_at"])
            datetime.fromisoformat(t["updated_at"])
        except Exception:
            return False
    return True


def _safe_load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def _restore_latest_backup(base_dir, backup_dir):
    if not os.path.exists(backup_dir):
        return
    files = [f for f in os.listdir(backup_dir) if f.startswith("state_") and f.endswith(".json")]
    if not files:
        return
    files.sort(reverse=True)
    latest = files[0]
    backup_path = os.path.join(backup_dir, latest)
    try:
        with open(backup_path, "r") as f:
            snapshot = json.load(f)
    except (json.JSONDecodeError, OSError):
        return

    os.makedirs(base_dir, exist_ok=True)
    with open(os.path.join(base_dir, "tasks.json"), "w") as f:
        json.dump(snapshot.get("tasks", []), f, indent=2)
    with open(os.path.join(base_dir, "categories.json"), "w") as f:
        json.dump(snapshot.get("categories", []), f, indent=2)
    with open(os.path.join(base_dir, "activity.log"), "w") as f:
        json.dump(snapshot.get("activity_log", []), f, indent=2)


def load_state(base_dir):
    os.makedirs(base_dir, exist_ok=True)

    tasks_path = os.path.join(base_dir, "tasks.json")
    categories_path = os.path.join(base_dir, "categories.json")
    activity_path = os.path.join(base_dir, "activity.log")

    tasks = _safe_load_json(tasks_path, [])
    categories = _safe_load_json(categories_path, [])
    activity_log = _safe_load_json(activity_path, [])

    if not validate_task_schema(tasks):
        backup_dir = "backups"
        _restore_latest_backup(base_dir, backup_dir)
        tasks = _safe_load_json(tasks_path, [])
        categories = _safe_load_json(categories_path, [])
        activity_log = _safe_load_json(activity_path, [])

    return tasks, categories, activity_log


def save_state(base_dir, tasks, categories, activity_log):
    os.makedirs(base_dir, exist_ok=True)

    tasks_path = os.path.join(base_dir, "tasks.json")
    categories_path = os.path.join(base_dir, "categories.json")
    activity_path = os.path.join(base_dir, "activity.log")

    with open(tasks_path, "w") as f:
        json.dump(tasks, f, indent=2)
    with open(categories_path, "w") as f:
        json.dump(categories, f, indent=2)
    with open(activity_path, "w") as f:
        json.dump(activity_log, f, indent=2)


def backup_state(base_dir, backup_dir):
    os.makedirs(backup_dir, exist_ok=True)

    tasks_path = os.path.join(base_dir, "tasks.json")
    categories_path = os.path.join(base_dir, "categories.json")
    activity_path = os.path.join(base_dir, "activity.log")

    tasks = _safe_load_json(tasks_path, [])
    categories = _safe_load_json(categories_path, [])
    activity_log = _safe_load_json(activity_path, [])

    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "tasks": tasks,
        "categories": categories,
        "activity_log": activity_log
    }

    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_file = os.path.join(backup_dir, f"state_{ts}.json")
    with open(backup_file, "w") as f:
        json.dump(snapshot, f, indent=2)

    return [backup_file]
