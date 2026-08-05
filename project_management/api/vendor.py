import frappe
from project_management.api.client import require_roles, _can_manage_deliverable


def _resolve_vendor_name(vendor_name=None):
    """Resolve the Vendor doc name from the session user if not provided."""
    if vendor_name:
        return vendor_name
    names = frappe.get_all("Vendor", filters={"user": frappe.session.user}, pluck="name")
    return names[0] if names else None


def _get_vendor_project_names(vendor_name):
    """Projects in which the given vendor is linked (via Project Vendors child)."""
    return frappe.get_all(
        "Project Vendors",
        filters={"vendor": vendor_name},
        pluck="parent",
    )


@frappe.whitelist()
@require_roles("Project Manager", "Vendor")
def get_vendor_projects(vendor_name=None):
    vendor_name = _resolve_vendor_name(vendor_name)
    if not vendor_name:
        return []

    project_names = _get_vendor_project_names(vendor_name)
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
    vendor_name = _resolve_vendor_name(vendor_name)
    if not vendor_name:
        return []

    project_names = _get_vendor_project_names(vendor_name)
    if not project_names:
        return []

    deliverables = frappe.get_all(
        "Deliverable",
        filters={"project": ["in", project_names]},
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

    for d in deliverables:
        comments = frappe.get_all(
            "Comment",
            filters={
                "reference_doctype": "Deliverable",
                "reference_name": d["name"],
                "comment_type": "Comment",
            },
            fields=["content", "comment_by", "creation"],
            order_by="creation desc",
            limit=2,
        )
        d["feedback_comments"] = comments

    return deliverables


@frappe.whitelist()
@require_roles("Project Manager", "Vendor")
def get_vendor_tasks(vendor_name=None):
    vendor_name = _resolve_vendor_name(vendor_name)
    if not vendor_name:
        return []

    tasks = frappe.get_all(
        "Project Task",
        filters={"assigned_vendor": vendor_name},
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
            "assigned_vendor",
        ],
        order_by="creation desc",
    )
    return tasks


@frappe.whitelist()
@require_roles("Project Manager", "Vendor")
def submit_deliverable(name=None, file_url=None, notes=None):
    """Submit a deliverable for review. Only allowed from WIP state.

    Records the delivery (file, notes, submitter, delivery date) and moves the
    deliverable to 'Ready for Approval' for the manager to review.
    """
    if not name:
        frappe.throw("Deliverable name is required")

    deliverable = frappe.get_doc("Deliverable", name)
    if not _can_manage_deliverable(deliverable):
        frappe.throw("You are not associated with this project", frappe.PermissionError)

    if deliverable.status != "WIP":
        frappe.throw("Only deliverables in progress can be submitted", frappe.ValidationError)

    if file_url:
        deliverable.file = file_url
    if notes:
        deliverable.access_link__notes = notes
    deliverable.submitted_by = frappe.session.user
    deliverable.delivery_date = frappe.utils.today()
    deliverable.status = "Ready for Approval"
    deliverable.flags.ignore_permissions = True
    deliverable.save()
    frappe.db.commit()
    return deliverable.as_dict()