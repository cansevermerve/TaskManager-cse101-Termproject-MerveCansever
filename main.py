import json
import uuid 
from datetime import datetime
try:
    with open("tasks.json","r") as file:
        tasks=json.load(file)
except FileNotFoundError:
    tasks=[]
print("Create a new task")
title=input("Enter task title:")
description=input("Description:")
category=input("Category:")
priority=input("Priority(Low/Medium/High)")
while True:
    due_date=input("Due date (year/month/day)").strip()
    try:
        due_date_obj=datetime.strptime(due_date,"%Y/%m/%d").date()
        due_date=due_date_obj.isoformat()
        print("Date looks okay!,",due_date)
        break
    except ValueError:
        print("Wrong day format!Use year/month/day")
task={
    "id":str(uuid.uuid4()),
    "title":title,
    "description":description,
    "category":category,
    "priority":priority,
    "status":"pending",
    "due_date":due_date,
    "created_at":datetime.now().isoformat(),
    "updated_at":datetime.now().isoformat(),
    "subtasks":[]
}
tasks.append(task)
with open("tasks.json","w") as file:
    json.dump(tasks,file)
print("\nTask created succesfully!")
print("Task ID:",task["id"])

