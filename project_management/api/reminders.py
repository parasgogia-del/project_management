import frappe
from frappe.utils import today


def send_overdue_task_reminders():

    overdue_tasks = frappe.get_all(
        "Project Task",
        filters={
            "status": ["!=", "Completed"],
            "due_date": ["<", today()]
        },
        fields=[
            "name",
            "title",
            "project",
            "assigned_to",
            "due_date"
        ]
    )

    print(f"Found {len(overdue_tasks)} overdue tasks")


    for task in overdue_tasks:
        channel_name = frappe.db.get_value(
            "Raven Channel",
            {
                "linked_doctype": "Project Info",
                "linked_document": task.project,
                "channel_name": "internal"
            },
            "name"
        )

        if not channel_name:
            print(f"No internal channel for {task.project}")
            continue

        frappe.get_doc({
            "doctype": "Raven Message",
            "channel_id": channel_name,
            "message_type": "Text",
            "text": "<p>✅ Reminder Test from Project Management App</p>"
        }).insert(ignore_permissions=True)

        print("Message Sent")
