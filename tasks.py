import json
import uuid
from datetime import datetime

try:
    with open("tasks.json", "r") as file:
        tasks = json.load(file)
except FileNotFoundError:
    tasks = []

print("Create a new task")
title = input("Enter task title: ")
description = input("Description: ")
category = input("Category: ")
priority = input("Priority (Low/Medium/High): ")

while True:
    due_date_input = input("Due date (year/month/day): ").strip()
    try:
        due_date_obj = datetime.strptime(due_date_input, "%Y/%m/%d").date()
        due_date = due_date_obj.isoformat()
        print("Date looks okay!", due_date)
        break
    except ValueError:
        print("Wrong day format! Use year/month/day format")

task = {
    "id": str(uuid.uuid4()),
    "title": title,
    "description": description,
    "category": category,
    "priority": priority,
    "status": "pending",
    "due_date": due_date,
    "created_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
    "subtasks": []
}

tasks.append(task)

with open("tasks.json", "w") as file:
    json.dump(tasks, file, indent=2)

print("\nTask created successfully!")
print("Task ID:", task["id"])


from datetime import datetime


def filter_tasks(tasks, *, status=None, category=None, due_before=None):
    filtered = tasks

    if status:
        filtered = [t for t in filtered if t.get("status") == status]

    if category:
        filtered = [t for t in filtered if t.get("category") == category]

    if due_before:
        cutoff = datetime.strptime(due_before, "%Y/%m/%d").date()
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
    today = datetime.today().date()
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
