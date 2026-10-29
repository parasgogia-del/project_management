import json
from collections import Counter

import frappe
from project_management.utils.permissions import require_roles


STAFF_ROLES = {"Project Manager", "Project Member"}


def _value(v):
    """Coerce Autocomplete-style {label, value} objects into their plain value."""
    if isinstance(v, dict):
        return v.get("value") or v.get("label")
    return v


def _is_staff():
    return bool(set(frappe.get_roles()) & STAFF_ROLES)


def _can_access_project(project):
    if not project or not frappe.db.exists("Project Info", project):
        return False
    user = frappe.session.user
    roles = set(frappe.get_roles())
    if user == "Administrator" or roles & {"Project Manager", "System Manager"}:
        return True
    if frappe.db.get_value("Project Info", project, "client") == user:
        return True
    return bool(
        frappe.db.exists(
            "Project Member",
            {"parent": project, "parenttype": "Project Info", "user": user},
        )
    )


def _check_ticket_access(doc):
    """Project access + (for non-staff) only their own tickets."""
    if not _can_access_project(doc.custom_project):
        frappe.throw("No access", frappe.PermissionError)
    if not _is_staff() and doc.raised_by != frappe.session.user:
        frappe.throw("Only your own tickets", frappe.PermissionError)


@frappe.whitelist()
def get_project_tickets(project):
    if not _can_access_project(project):
        frappe.throw("No access", frappe.PermissionError)
    filters = {"custom_project": project}
    if not _is_staff():
        filters["raised_by"] = frappe.session.user
    return frappe.get_all(
        "HD Ticket",
        filters=filters,
        fields=["name", "subject", "status", "priority", "raised_by",
                "agent_group", "creation", "modified"],
        order_by="creation desc",
    )


@frappe.whitelist(methods=["POST"])
def create_ticket(project, data=None):
    if not _can_access_project(project):
        frappe.throw("No access", frappe.PermissionError)
    if isinstance(data, str):
        data = json.loads(data)
    if not data:
        frappe.throw("Data is required")
    if not data.get("subject"):
        frappe.throw("Subject is required")
    ticket = frappe.get_doc({
        "doctype": "HD Ticket",
        "subject": data.get("subject"),
        "description": data.get("description"),
        "priority": _value(data.get("priority")) or "Medium",
        "custom_project": project,
        "raised_by": frappe.session.user,
    })
    ticket.insert(ignore_permissions=True)
    return ticket.as_dict()


@frappe.whitelist()
def get_ticket(name):
    doc = frappe.get_doc("HD Ticket", name)
    _check_ticket_access(doc)
    return {
        "ticket": doc.as_dict(),
        "comments": _get_ticket_comments(name),
    }


def _get_ticket_comments(name):
    """Read the conversation from HD Ticket Comment (UI) + Communication (email)."""
    comments = frappe.get_all(
        "HD Ticket Comment",
        filters={"reference_ticket": name},
        fields=["name", "content", "commented_by", "creation"],
        order_by="creation asc",
    )
    for c in comments:
        c["_type"] = "comment"
        c["author"] = c.get("commented_by")
    communications = frappe.get_all(
        "Communication",
        filters={"reference_doctype": "HD Ticket", "reference_name": name},
        fields=["name", "content", "sender", "creation", "communication_type"],
        order_by="creation asc",
    )
    for c in communications:
        # only show user-facing communication types (skip system/hidden types)
        if c.get("communication_type") not in (None, "Communication", "Comment"):
            continue
        c["_type"] = "communication"
        c["author"] = c.get("sender")
        comments.append(c)
    comments.sort(key=lambda c: c.get("creation") or "")
    return comments


@frappe.whitelist(methods=["POST"])
@require_roles("Project Manager")
def update_ticket(name, data=None):
    if isinstance(data, str):
        data = json.loads(data)
    if not data:
        frappe.throw("Data is required")
    doc = frappe.get_doc("HD Ticket", name)
    if not _can_access_project(doc.custom_project):
        frappe.throw("No access", frappe.PermissionError)
    for field in ("status", "priority", "agent_group", "subject", "description"):
        if field in data:
            doc.set(field, _value(data[field]))
    doc.save(ignore_permissions=True)
    return doc.as_dict()


@frappe.whitelist(methods=["POST"])
def add_ticket_comment(name, content=None):
    if not content:
        frappe.throw("Content is required")
    doc = frappe.get_doc("HD Ticket", name)
    _check_ticket_access(doc)
    comment = frappe.get_doc({
        "doctype": "HD Ticket Comment",
        "reference_ticket": name,
        "content": content,
        "commented_by": frappe.session.user,
    })
    comment.insert(ignore_permissions=True)
    return {"status": "ok", "name": comment.name}


@frappe.whitelist(methods=["POST"])
def edit_ticket_comment(name, content=None):
    if not content:
        frappe.throw("Content is required")
    comment = frappe.get_doc("HD Ticket Comment", name)
    ticket = frappe.get_doc("HD Ticket", comment.reference_ticket)
    if not _can_access_project(ticket.custom_project):
        frappe.throw("No access", frappe.PermissionError)
    if comment.commented_by != frappe.session.user:
        frappe.throw("Only your own comments", frappe.PermissionError)
    comment.content = content
    comment.save(ignore_permissions=True)
    return {"status": "ok"}


@frappe.whitelist(methods=["POST", "DELETE"])
def delete_ticket_comment(name):
    comment = frappe.get_doc("HD Ticket Comment", name)
    ticket = frappe.get_doc("HD Ticket", comment.reference_ticket)
    if not _can_access_project(ticket.custom_project):
        frappe.throw("No access", frappe.PermissionError)
    if comment.commented_by != frappe.session.user:
        frappe.throw("Only your own comments", frappe.PermissionError)
    frappe.delete_doc("HD Ticket Comment", name, ignore_permissions=True)
    return {"status": "ok"}


@frappe.whitelist()
def get_my_tickets():
    """Role-based list of all tickets across the projects the user can access.

    - Project Manager: every ticket.
    - Project Member: every ticket on projects where they are the client or a
      listed project member.
    - Anyone else (Client, Vendor): only tickets they raised, on projects where
      they are the client or a listed project member.
    """
    fields = ["name", "subject", "status", "priority", "raised_by",
              "custom_project", "agent_group", "creation", "modified"]
    user = frappe.session.user
    roles = set(frappe.get_roles())

    if "Project Manager" in roles:
        return frappe.get_all(
            "HD Ticket", fields=fields, order_by="creation desc"
        )

    accessible = set()
    for p in frappe.get_all(
        "Project Info", filters={"client": user}, fields=["name"]
    ):
        accessible.add(p["name"])
    for p in frappe.get_all(
        "Project Member",
        filters={"user": user, "parenttype": "Project Info"},
        fields=["parent"],
    ):
        accessible.add(p["parent"])

    # keep only valid Project Info parents
    accessible = {n for n in accessible if frappe.db.exists("Project Info", n)}
    if not accessible:
        return []

    filters = {"custom_project": ["in", list(accessible)]}
    if not _is_staff():
        filters["raised_by"] = user
    return frappe.get_all(
        "HD Ticket", filters=filters, fields=fields, order_by="creation desc"
    )


@frappe.whitelist()
def get_ticket_stats(project):
    if not _can_access_project(project):
        frappe.throw("No access", frappe.PermissionError)
    filters = {"custom_project": project}
    if not _is_staff():
        filters["raised_by"] = frappe.session.user
    statuses = frappe.get_all("HD Ticket", filters=filters, pluck="status")
    stats = dict(Counter(statuses))
    stats["total"] = len(statuses)
    return stats
