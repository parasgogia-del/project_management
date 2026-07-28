# Copyright (c) 2026, Paras Gogia and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document


class TimeLog(Document):
    def on_update(self):
        self.update_task_hours()

    def on_trash(self):
        self.update_task_hours(exclude_self=True)

    def before_insert(self):
        if not self.project_member:
            self.project_member = frappe.session.user

    def update_task_hours(self, exclude_self=False):
        if not self.task:
            return

        filters = {"task": self.task}
        if exclude_self:
            filters["name"] = ["!=", self.name]

        logs = frappe.get_all(
            "Time Log",
            filters=filters,
            fields=["hours"]
        )

        total = sum(log.hours for log in logs)

        frappe.db.set_value(
            "Project Task",
            self.task,
            "actual_hours",
            total
        )
