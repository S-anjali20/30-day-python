import json
import os
import questionary

FILE_NAME = "tasks.json"


def load_tasks():
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return []

    return []


def save_tasks(tasks):
    with open(FILE_NAME, "w") as file:
        json.dump(tasks, file, indent=4)


def add_task(tasks):
    task_name = questionary.text(
        "Enter your task:"
    ).ask()

    if not task_name.strip():
        print("❌ Task cannot be empty.")
        return

    priority = questionary.select(
        "Select priority:",
        choices=[
            "🔴 High",
            "🟡 Medium",
            "🟢 Low"
        ]
    ).ask()

    task = {
        "id": len(tasks) + 1,
        "task": task_name,
        "priority": priority,
        "completed": False
    }

    tasks.append(task)
    save_tasks(tasks)

    print("✅ Task added successfully!")


def view_tasks(tasks):

    if not tasks:
        print("\n📭 No tasks found.")
        return

    print("\n" + "=" * 70)
    print("                         📝 YOUR TASKS")
    print("=" * 70)

    for task in tasks:

        if task["completed"]:
            status = "✅ Completed"
        else:
            status = "⏳ Pending"

        print(
            f"{task['id']}. "
            f"{task['task']} | "
            f"{task['priority']} | "
            f"{status}"
        )

    print("=" * 70)


def complete_task(tasks):

    pending_tasks = [
        task for task in tasks
        if not task["completed"]
    ]

    if not pending_tasks:
        print("\n🎉 No pending tasks!")
        return

    choices = [
        f"{task['id']}. {task['task']}"
        for task in pending_tasks
    ]

    selected = questionary.select(
        "Select a task to complete:",
        choices=choices
    ).ask()

    task_id = int(selected.split(".")[0])

    for task in tasks:

        if task["id"] == task_id:
            task["completed"] = True
            break

    save_tasks(tasks)

    print("✅ Task marked as completed!")


def edit_task(tasks):

    if not tasks:
        print("\n📭 No tasks available.")
        return

    choices = [
        f"{task['id']}. {task['task']}"
        for task in tasks
    ]

    selected = questionary.select(
        "Select a task to edit:",
        choices=choices
    ).ask()

    task_id = int(selected.split(".")[0])

    for task in tasks:

        if task["id"] == task_id:

            new_task = questionary.text(
                "Enter new task:",
                default=task["task"]
            ).ask()

            if new_task.strip():
                task["task"] = new_task

            new_priority = questionary.select(
                "Select new priority:",
                choices=[
                    "🔴 High",
                    "🟡 Medium",
                    "🟢 Low"
                ],
                default=task["priority"]
            ).ask()

            task["priority"] = new_priority

            break

    save_tasks(tasks)

    print("✏️ Task updated successfully!")


def delete_task(tasks):

    if not tasks:
        print("\n📭 No tasks available.")
        return

    choices = [
        f"{task['id']}. {task['task']}"
        for task in tasks
    ]

    selected = questionary.select(
        "Select a task to delete:",
        choices=choices
    ).ask()

    task_id = int(selected.split(".")[0])

    for task in tasks:

        if task["id"] == task_id:

            tasks.remove(task)
            break

    for index, task in enumerate(tasks, start=1):
        task["id"] = index

    save_tasks(tasks)

    print("🗑️ Task deleted successfully!")


def search_task(tasks):

    search = questionary.text(
        "Enter task to search:"
    ).ask()

    results = [
        task for task in tasks
        if search.lower() in task["task"].lower()
    ]

    if not results:
        print("\n❌ No matching tasks found.")
        return

    print("\n🔍 Search Results")
    print("=" * 70)

    for task in results:

        status = (
            "✅ Completed"
            if task["completed"]
            else "⏳ Pending"
        )

        print(
            f"{task['id']}. "
            f"{task['task']} | "
            f"{task['priority']} | "
            f"{status}"
        )

    print("=" * 70)


def statistics(tasks):

    total = len(tasks)

    completed = sum(
        task["completed"]
        for task in tasks
    )

    pending = total - completed

    high = sum(
        task["priority"] == "🔴 High"
        for task in tasks
    )

    medium = sum(
        task["priority"] == "🟡 Medium"
        for task in tasks
    )

    low = sum(
        task["priority"] == "🟢 Low"
        for task in tasks
    )

    print("\n" + "=" * 50)
    print("                 📊 STATISTICS")
    print("=" * 50)

    print(f"Total Tasks       : {total}")
    print(f"Completed Tasks   : {completed}")
    print(f"Pending Tasks     : {pending}")
    print()
    print(f"🔴 High Priority  : {high}")
    print(f"🟡 Medium Priority: {medium}")
    print(f"🟢 Low Priority   : {low}")

    print("=" * 50)


def main():

    tasks = load_tasks()

    print("\n" + "=" * 50)
    print("           📝 TO-DO TASK MANAGER")
    print("=" * 50)

    while True:

        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "➕ Add Task",
                "📋 View Tasks",
                "✅ Complete Task",
                "✏️ Edit Task",
                "❌ Delete Task",
                "🔍 Search Task",
                "📊 Statistics",
                "🚪 Exit"
            ]
        ).ask()

        if choice == "➕ Add Task":
            add_task(tasks)

        elif choice == "📋 View Tasks":
            view_tasks(tasks)

        elif choice == "✅ Complete Task":
            complete_task(tasks)

        elif choice == "✏️ Edit Task":
            edit_task(tasks)

        elif choice == "❌ Delete Task":
            delete_task(tasks)

        elif choice == "🔍 Search Task":
            search_task(tasks)

        elif choice == "📊 Statistics":
            statistics(tasks)

        elif choice == "🚪 Exit":
            print("\n👋 Thank you for using To-Do Task Manager!")
            break


if __name__ == "__main__":
    main()