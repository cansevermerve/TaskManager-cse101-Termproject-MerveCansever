import json
import uuid
from datetime import datetime, date

from activity import log_activity, load_activity, productivity_stats, export_report

TASKS_FILE = "tasks.json"
LOG_FILE = "activity.log"


def load_tasks():
    try:
        with open(TASKS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_tasks(tasks):
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=2)


def create_task(tasks):
    print("\n--- Create a new task ---")
    title = input("Enter task title: ").strip()
    description = input("Description: ").strip()
    category = input("Category: ").strip()
    priority = input("Priority (Low/Medium/High): ").strip()

    while True:
        due_date_input = input("Due date (year/month/day): ").strip()
        try:
            due_date_obj = datetime.strptime(due_date_input, "%Y/%m/%d").date()
            due_date = due_date_obj.isoformat()
            print("Date looks okay:", due_date)
            break
        except ValueError:
            print("Wrong day format! Use year/month/day like 2025/01/15")

    now = datetime.now().isoformat()
    task = {
        "id": str(uuid.uuid4()),
        "title": title,
        "description": description,
        "category": category,
        "priority": priority,
        "status": "pending",
        "due_date": due_date,
        "created_at": now,
        "updated_at": now,
        "subtasks": []
    }

    tasks.append(task)

    event = {
        "timestamp": now,
        "action": "create",
        "task_id": task["id"],
        "summary": f"Created task '{task['title']}'"
    }
    log_activity(LOG_FILE, event)

    print("\nTask created successfully!")
    print("Task ID:", task["id"])


def filter_tasks(tasks, *, status=None, category=None, due_before=None):
    filtered = tasks

    if status:
        filtered = [t for t in filtered if t.get("status") == status]

    if category:
        filtered = [t for t in filtered if t.get("category") == category]

    if due_before:
        try:
            cutoff = datetime.strptime(due_before, "%Y/%m/%d").date()
        except ValueError:
            print("Wrong date format. Use year/month/day like 2025/01/15.")
            return []
        filtered = [
            t for t in filtered
            if t.get("due_date")
            and datetime.strptime(t["due_date"], "%Y-%m-%d").date() <= cutoff
        ]

    return filtered


def search_tasks(tasks, query):
    query = query.lower()
    return [
        t for t in tasks
        if query in t["title"].lower()
        or query in t.get("description", "").lower()
    ]


def summarize_by_category(tasks):
    summary = {}
    for t in tasks:
        category = t.get("category", "Uncategorized")
        summary[category] = summary.get(category, 0) + 1
    return summary


def upcoming_tasks(tasks, within_days):
    today = date.today()
    upcoming = []

    for t in tasks:
        due_str = t.get("due_date")
        if not due_str:
            continue
        try:
            due = datetime.strptime(due_str, "%Y-%m-%d").date()
        except ValueError:
            continue

        days_left = (due - today).days
        if 0 <= days_left <= within_days:
            upcoming.append(t)

    return upcoming


def show_tasks(tasks):
    if not tasks:
        print("No tasks.")
        return
    for t in tasks:
        print("Title:", t["title"])
        print("Description:", t["description"])
        print("Category:", t.get("category", ""))
        print("Priority:", t.get("priority", ""))
        print("Status:", t.get("status", ""))
        print("Due date:", t.get("due_date", ""))
        print("ID:", t["id"])
        print("---")


def mark_task_completed(tasks):
    task_id = input("Enter task ID to mark as completed: ").strip()
    for t in tasks:
        if t["id"] == task_id:
            t["status"] = "completed"
            now = datetime.now().isoformat()
            t["updated_at"] = now
            t["completed_at"] = now
            event = {
                "timestamp": now,
                "action": "completed",
                "task_id": t["id"],
                "summary": f"Completed task '{t['title']}'"
            }
            log_activity(LOG_FILE, event)
            print("Task marked as completed.")
            return
    print("Task not found.")


def show_stats(tasks):
    activity_log = load_activity(LOG_FILE)
    stats = productivity_stats(tasks, activity_log)
    print("\n--- Productivity statistics ---")
    print("Tasks completed:", stats["tasks_completed"])
    print("Average completion days:", stats["avg_completion_days"])
    print("Category trends:")
    for cat, count in stats["category_trends"].items():
        print(" ", cat, ":", count)
    print("Completed per week:")
    for week, count in stats["completed_per_week"].items():
        print(" ", week, ":", count)

    choice = input("Export this report to reports/productivity.json? (y/n): ").strip().lower()
    if choice == "y":
        path = export_report(stats, "productivity.json")
        print("Report saved to", path)


def main():
    tasks = load_tasks()

    while True:
        print("\nTask Manager")
        print("1. Add task")
        print("2. View all tasks")
        print("3. Filter tasks")
        print("4. Search tasks")
        print("5. Upcoming tasks (next 7 days)")
        print("6. Category summary")
        print("7. Mark task completed")
        print("8. Show productivity stats")
        print("0. Save and exit")

        choice = input("Select: ").strip()

        if choice == "1":
            create_task(tasks)
        elif choice == "2":
            show_tasks(tasks)
        elif choice == "3":
            s = input("Status (pending/completed or empty): ").strip() or None
            c = input("Category (or empty): ").strip() or None
            d = input("Due before (YYYY/MM/DD) or empty: ").strip() or None
            result = filter_tasks(tasks, status=s, category=c, due_before=d)
            show_tasks(result)
        elif choice == "4":
            q = input("Search text: ").strip()
            result = search_tasks(tasks, q)
            show_tasks(result)
        elif choice == "5":
            result = upcoming_tasks(tasks, within_days=7)
            show_tasks(result)
        elif choice == "6":
            summary = summarize_by_category(tasks)
            print("\nTasks by category:")
            for cat, count in summary.items():
                print(cat, ":", count)
        elif choice == "7":
            mark_task_completed(tasks)
        elif choice == "8":
            show_stats(tasks)
        elif choice == "0":
            save_tasks(tasks)
            print("Saved. Goodbye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
