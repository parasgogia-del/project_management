# Copyright (c) 2026, Paras Gogia and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ProjectTask(Document):

    def on_update(self):
        self.update_project_progress()

    def on_trash(self):
        # on_trash runs before the row is actually deleted from DB,
        # so we must exclude this task manually from the count
        self.update_project_progress(exclude_self=True)

    def update_project_progress(self, exclude_self=False):

        if not self.project:
            return

        filters = {"project": self.project}
        if exclude_self:
            filters["name"] = ["!=", self.name]

        tasks = frappe.get_all(
            "Project Task",
            filters=filters,
            fields=["status"]
        )

        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.status == "Completed")

        progress = (completed_tasks / total_tasks) * 100 if total_tasks else 0

        frappe.db.set_value(
            "Project Info",
            self.project,
            "progress",
            progress
        )
