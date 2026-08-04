import frappe
from project_management.project_management.api.client import require_roles


@frappe.whitelist()
@require_roles("Project Manager", "Vendor")
def get_vendor_projects(vendor_name=None):
    if not vendor_name:
        return []

    project_names = frappe.get_all(
        "Vendor",
        filters={"vendor_name": vendor_name},
        pluck="parent",
    )

    if not project_names:
        return []

    projects = frappe.get_all(
        "Project Info",
        filters={"name": ["in", project_names]},
        fields=[
            "name",
            "project_name",
            "client",
            "project_manager",
            "status",
            "progress",
            "start_date",
            "end_date",
            "description",
        ],
        order_by="creation desc",
    )
    return projects


@frappe.whitelist()
@require_roles("Project Manager", "Vendor")
def get_vendor_deliverables(vendor_name=None):
    if not vendor_name:
        return []

    deliverables = frappe.get_all(
        "Deliverable",
        filters={"assigned_to": vendor_name},
        fields=[
            "name",
            "title",
            "project",
            "status",
            "due_date",
            "description",
            "assigned_to",
            "submitted_by",
            "delivery_date",
        ],
        order_by="creation desc",
    )
    return deliverables


@frappe.whitelist()
@require_roles("Project Manager", "Vendor")
def get_vendor_tasks(vendor_name=None):
    if not vendor_name:
        return []

    tasks = frappe.get_all(
        "Project Task",
        filters={"assigned_to": vendor_name},
        fields=[
            "name",
            "title",
            "project",
            "deliverable",
            "status",
            "priority",
            "due_date",
            "estimated_hours",
            "actual_hours",
            "description",
            "assigned_to",
        ],
        order_by="creation desc",
    )
    return tasks
