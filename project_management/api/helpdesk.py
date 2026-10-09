import functools
import json

import frappe


def require_roles(*roles):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            user_roles = set(frappe.get_roles())
            if not any(r in user_roles for r in roles):
                frappe.throw("You do not have permission", frappe.PermissionError)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def _value(v):
    """Coerce Autocomplete-style {label, value} objects into their plain value."""
    if isinstance(v, dict):
        return v.get("value") or v.get("label")
    return v


def _can_access_project(project):
    if not project:
        return False
    p = frappe.get_doc("Project Info", project)
    user = frappe.session.user
    roles = set(frappe.get_roles())
    if "Project Manager" in roles:
        return True
    if p.client == user:
        return True
    # member check
    for m in p.project_members:
        if m.get("user") == user:
            return True
    return False


@frappe.whitelist()
def get_project_tickets(project):
    if not _can_access_project(project):
        frappe.throw("No access", frappe.PermissionError)
    tickets = frappe.get_all(
        "HD Ticket",
        filters={"custom_project": project},
        fields=["name", "subject", "status", "priority", "raised_by",
                "agent_group", "creation", "modified"],
        order_by="creation desc",
    )
    return tickets


@frappe.whitelist()
def create_ticket(project, data=None):
    if not _can_access_project(project):
        frappe.throw("No access", frappe.PermissionError)
    if isinstance(data, str):
        data = json.loads(data)
    if not data:
        frappe.throw("Data is required")
    ticket = frappe.get_doc({
        "doctype": "HD Ticket",
        "subject": data.get("subject"),
        "description": data.get("description"),
        "priority": _value(data.get("priority")) or "Medium",
        "custom_project": project,
        "raised_by": frappe.session.user,
    })
    ticket.insert(ignore_permissions=True)
    frappe.db.commit()
    return ticket.as_dict()


@frappe.whitelist()
def get_ticket(name):
    doc = frappe.get_doc("HD Ticket", name)
    # check the ticket's project access
    if not _can_access_project(doc.custom_project):
        frappe.throw("No access", frappe.PermissionError)
    user_roles = set(frappe.get_roles())
    is_staff = user_roles.intersection(
        {"Project Manager", "Project Member"}
    )
    if not is_staff and doc.raised_by != frappe.session.user:
        frappe.throw("Only your own tickets", frappe.PermissionError)
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


@frappe.whitelist()
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
    frappe.db.commit()
    return doc.as_dict()


@frappe.whitelist()
def add_ticket_comment(name, content=None):
    if not content:
        frappe.throw("Content is required")
    doc = frappe.get_doc("HD Ticket", name)
    if not _can_access_project(doc.custom_project):
        frappe.throw("No access", frappe.PermissionError)
    user_roles = set(frappe.get_roles())
    is_staff = user_roles.intersection(
        {"Project Manager", "Project Member"}
    )
    if not is_staff and doc.raised_by != frappe.session.user:
        frappe.throw("Only your own tickets", frappe.PermissionError)
    comment = frappe.get_doc({
        "doctype": "HD Ticket Comment",
        "reference_ticket": name,
        "content": content,
        "commented_by": frappe.session.user,
    })
    comment.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"status": "ok", "name": comment.name}


@frappe.whitelist()
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
    frappe.db.commit()
    return {"status": "ok"}


@frappe.whitelist()
def delete_ticket_comment(name):
    comment = frappe.get_doc("HD Ticket Comment", name)
    ticket = frappe.get_doc("HD Ticket", comment.reference_ticket)
    if not _can_access_project(ticket.custom_project):
        frappe.throw("No access", frappe.PermissionError)
    if comment.commented_by != frappe.session.user:
        frappe.throw("Only your own comments", frappe.PermissionError)
    comment.delete(ignore_permissions=True)
    frappe.db.commit()
    return {"status": "ok"}


@frappe.whitelist()
def get_my_tickets():
    """Role-based list of all tickets across the projects the user can access.

    - Project Manager: every ticket.
    - Any other role (Client, Project Member, Vendor): only tickets on projects
      where they are the client or a listed project member.
    """
    fields = ["name", "subject", "status", "priority", "raised_by",
              "custom_project", "agent_group", "creation", "modified"]
    roles = set(frappe.get_roles())
    if "Project Manager" in roles:
        return frappe.get_all(
            "HD Ticket", fields=fields, order_by="creation desc"
        )
    user = frappe.session.user
    accessible = set()
    client_projects = frappe.get_all(
        "Project Info", filters={"client": user}, fields=["name"]
    )
    for p in client_projects:
        accessible.add(p["name"])
    member_projects = frappe.get_all(
        "Project Member", filters={"user": user}, fields=["parent"]
    )
    for p in member_projects:
        accessible.add(p["parent"])
    # keep only valid Project Info parents
    if accessible:
        accessible = {
            n for n in accessible
            if frappe.db.exists("Project Info", n)
        }
    if not accessible:
        return []
    return frappe.get_all(
        "HD Ticket",
        filters={"custom_project": ["in", list(accessible)]},
        fields=fields,
        order_by="creation desc",
    )


@frappe.whitelist()
def get_ticket_stats(project):
    if not _can_access_project(project):
        frappe.throw("No access", frappe.PermissionError)
    rows = frappe.db.sql(
        """
        SELECT status, COUNT(*) AS count
        FROM `tabHD Ticket`
        WHERE custom_project = %s
        GROUP BY status
        """,
        project,
        as_dict=True,
    )
    stats = {row["status"]: row["count"] for row in rows}
    stats["total"] = sum(stats.values())
    return stats
