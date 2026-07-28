import frappe


@frappe.whitelist(allow_guest=True)
def create_project(data=None):
    if not data:
        frappe.throw("Data is required")
    if isinstance(data, str):
        import json
        data = json.loads(data)

    _skip = {"doctype", "project_members", "vendors"}
    project_data = {k: v for k, v in data.items() if k not in _skip}
    project_data["doctype"] = "Project Info"
    doc = frappe.get_doc(project_data)

    for m in data.get("project_members", []):
        if m.get("user"):
            doc.append("project_members", m)
    for v in data.get("vendors", []):
        if v.get("vendor"):
            doc.append("vendors", v)

    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return doc.as_dict()


@frappe.whitelist(allow_guest=True)
def create_task(data=None):
    if not data:
        frappe.throw("Data is required")
    if isinstance(data, str):
        import json
        data = json.loads(data)

    task_data = {
        "doctype": "Project Task",
        "title": data.get("title"),
        "project": data.get("project"),
        "deliverable": data.get("deliverable"),
        "description": data.get("description", ""),
        "priority": data.get("priority", "Medium"),
        "status": data.get("status", "Open"),
        "estimated_hours": data.get("estimated_hours"),
        "assigned_to": data.get("assigned_to"),
        "assigned_vendor": data.get("assigned_vendor"),
        "start_date": data.get("start_date"),
        "due_date": data.get("due_date"),
    }
    doc = frappe.get_doc(task_data)
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return doc.as_dict()


@frappe.whitelist(allow_guest=True)
def get_projects():
    projects = frappe.get_all(
        "Project Info",
        fields=[
            "name",
            "project_name",
            "status",
            "progress",
            "client",
            "project_manager",
            "start_date",
            "end_date",
            "description",
        ],
    )
    return projects


@frappe.whitelist(allow_guest=True)
def get_project(name=None):
    if not name:
        return None
    try:
        project = frappe.get_doc("Project Info", name)
        data = project.as_dict()

        if data.get("project_members"):
            for m in data["project_members"]:
                if m.get("user"):
                    email = frappe.db.get_value("User", m["user"], "email")
                    m["email"] = email or ""
                if not m.get("notes"):
                    member_doc = frappe.db.get_value("Project Member", {"parent": name, "user": m.get("user")}, "notes")
                    m["notes"] = member_doc or ""

        return data
    except frappe.DoesNotExistError:
        return None


@frappe.whitelist(allow_guest=True)
def get_deliverables(project=None):
    filters = {}
    if project:
        filters["project"] = project

    deliverables = frappe.get_all(
        "Deliverable",
        filters=filters,
        fields=[
            "name",
            "title",
            "project",
            "status",
            "due_date",
            "description",
            "submitted_by",
            "delivery_date",
        ],
    )
    return deliverables


@frappe.whitelist(allow_guest=True)
def update_project(name=None, data=None):
    if not name:
        frappe.throw("Project name is required")
    if not data:
        frappe.throw("Data is required")

    if isinstance(data, str):
        import json
        data = json.loads(data)

    allowed_fields = ["project_name", "client", "project_manager", "status", "start_date", "end_date", "description"]
    filtered = {k: v for k, v in data.items() if k in allowed_fields}

    for field, value in filtered.items():
        frappe.db.set_value("Project Info", name, field, value)

    if "project_members" in data:
        _update_child_table("Project Info", name, "project_members", "Project Member", data["project_members"])

    if "vendors" in data:
        _update_child_table("Project Info", name, "vendors", "Project Vendors", data["vendors"])

    frappe.db.commit()
    return frappe.get_doc("Project Info", name).as_dict()

def _update_child_table(parent_doctype, parent_name, fieldname, child_doctype, rows):
    _skip = {"name", "doctype", "parent", "parenttype", "parentfield", "idx", "creation", "modified", "modified_by", "owner"}

    existing = frappe.get_all(child_doctype, filters={"parent": parent_name}, pluck="name")
    incoming_ids = {r.get("name") for r in rows if r.get("name")}

    for e_name in existing:
        if e_name not in incoming_ids:
            frappe.delete_doc(child_doctype, e_name, ignore_permissions=True)

    for row in rows:
        row_data = {k: v for k, v in row.items() if k not in _skip}
        if row.get("name") and row["name"] in existing:
            frappe.db.set_value(child_doctype, row["name"], row_data)
        else:
            row_data["parent"] = parent_name
            row_data["parenttype"] = parent_doctype
            row_data["parentfield"] = fieldname
            frappe.get_doc({"doctype": child_doctype, **row_data}).insert(ignore_permissions=True)


@frappe.whitelist(allow_guest=True)
def get_deliverables_with_details(project=None):
    filters = {}
    if project:
        filters["project"] = project

    deliverables = frappe.get_all(
        "Deliverable",
        filters=filters,
        fields=[
            "name",
            "title",
            "project",
            "status",
            "due_date",
            "delivery_date",
            "description",
            "submitted_by",
        ],
    )

    for d in deliverables:
        tasks = frappe.get_all(
            "Project Task",
            filters={"deliverable": d.name},
            fields=["name", "status", "assigned_to", "assigned_vendor"],
        )

        total = len(tasks)
        completed = sum(1 for t in tasks if t.status == "Completed")

        d.total_tasks = total
        d.completed_tasks = completed
        d.progress = round((completed / total) * 100) if total else 0

        members = set()
        vendors = set()
        for t in tasks:
            if t.assigned_to:
                members.add(t.assigned_to)
            if t.assigned_vendor:
                vendors.add(t.assigned_vendor)

        d.members = sorted(members)
        d.vendors = sorted(vendors)

    return deliverables


@frappe.whitelist(allow_guest=True)
def get_deliverable(name=None):
    if not name:
        return None
    try:
        deliverable = frappe.get_doc("Deliverable", name)
        return deliverable.as_dict()
    except frappe.DoesNotExistError:
        return None


@frappe.whitelist(allow_guest=True)
def get_tasks(project=None, deliverable=None, assigned_to=None):
    filters = {}
    if project:
        filters["project"] = project
    if deliverable:
        filters["deliverable"] = deliverable
    if assigned_to:
        filters["assigned_to"] = assigned_to

    tasks = frappe.get_all(
        "Project Task",
        filters=filters,
        fields=[
            "name",
            "title",
            "project",
            "deliverable",
            "status",
            "priority",
            "start_date",
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


@frappe.whitelist(allow_guest=True)
def get_task(name=None):
    if not name:
        return None
    try:
        task = frappe.get_doc("Project Task", name)
        return task.as_dict()
    except frappe.DoesNotExistError:
        return None


@frappe.whitelist(allow_guest=True)
def get_time_logs(task=None):
    filters = {}
    if task:
        filters["task"] = task

    logs = frappe.get_all(
        "Time Log",
        filters=filters,
        fields=[
            "name",
            "task",
            "project",
            "project_member",
            "date",
            "hours",
            "description",
        ],
        order_by="date desc",
    )
    return logs


@frappe.whitelist(allow_guest=True)
def create_time_log(task=None, project=None, date=None, hours=None, description="", project_member=None):
    if not task or not hours:
        frappe.throw("Task and hours are required")

    doc = frappe.get_doc({
        "doctype": "Time Log",
        "task": task,
        "project": project or "",
        "project_member": project_member or frappe.session.user,
        "date": date or frappe.utils.today(),
        "hours": float(hours),
        "description": description or "",
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return doc.as_dict()

@frappe.whitelist(allow_guest=True)
def update_task_status(name=None, status=None):
    if not name or not status:
        frappe.throw("Name and status are required")

    task = frappe.get_doc("Project Task", name)
    task.status = status
    task.flags.ignore_permissions = True
    task.save()
    frappe.db.commit()

    return {"status": "ok"}


@frappe.whitelist(allow_guest=True)
def update_deliverable_status(name=None, action=None):
    if not name or not action:
        frappe.throw("Name and action are required")

    workflow_name = frappe.db.get_value("Workflow", {"document_type": "Deliverable"}, "name")
    if not workflow_name:
        frappe.throw("No workflow found for Deliverable")

    transitions = frappe.get_all(
        "Workflow Transition",
        filters={"parent": workflow_name, "action": action},
        fields=["state", "next_state"],
    )

    if not transitions:
        frappe.throw(f"Invalid workflow action: {action}")

    doc = frappe.get_doc("Deliverable", name)
    current_state = doc.get("workflow_state") or doc.get("status")

    transition = None
    for t in transitions:
        if t.state == current_state:
            transition = t
            break

    if not transition:
        frappe.throw(f"Action '{action}' not valid from current state '{current_state}'")

    workflow = frappe.get_doc("Workflow", workflow_name)
    workflow_state_field = workflow.workflow_state_field or "workflow_state"

    frappe.db.set_value("Deliverable", name, workflow_state_field, transition.next_state)
    frappe.db.set_value("Deliverable", name, "status", transition.next_state)
    frappe.db.commit()

    return {"status": "ok", "workflow_state": transition.next_state}


@frappe.whitelist(allow_guest=True)
def get_gantt_tasks(project=None):
    filters = {}
    if project:
        filters["project"] = project

    tasks = frappe.get_all(
        "Project Task",
        filters=filters,
        fields=[
            "name",
            "title",
            "project",
            "deliverable",
            "status",
            "priority",
            "start_date",
            "due_date",
            "assigned_to",
            "assigned_vendor",
            "estimated_hours",
        ],
        order_by="start_date asc",
    )

    today = frappe.utils.today()
    for t in tasks:
        t.start_date = t.start_date or t.due_date or today
        if not t.due_date:
            t.due_date = t.start_date
        t.color = {
            "Open": "#6b7280",
            "Working": "#3b82f6",
            "Blocked": "#ef4444",
            "Completed": "#22c55e",
        }.get(t.status, "#6b7280")

    return tasks


@frappe.whitelist(allow_guest=True)
def get_comments(reference_doctype=None, reference_name=None):
    if not reference_doctype or not reference_name:
        frappe.throw("reference_doctype and reference_name are required")
    comments = frappe.get_all(
        "Comment",
        filters={
            "reference_doctype": reference_doctype,
            "reference_name": reference_name,
            "comment_type": "Comment",
        },
        fields=["name", "content", "comment_email", "owner", "creation"],
        order_by="creation asc",
    )
    return comments


@frappe.whitelist(allow_guest=True)
def add_comment(reference_doctype=None, reference_name=None, content=None):
    if not reference_doctype or not reference_name or not content:
        frappe.throw("reference_doctype, reference_name, and content are required")
    doc = frappe.get_doc({
        "doctype": "Comment",
        "comment_type": "Comment",
        "reference_doctype": reference_doctype,
        "reference_name": reference_name,
        "content": content,
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"status": "ok"}


@frappe.whitelist(allow_guest=True)
def get_session_user():
    return frappe.session.user


@frappe.whitelist(allow_guest=True)
def edit_comment(name=None, content=None):
    if not name or not content:
        frappe.throw("name and content are required")
    owner = frappe.db.get_value("Comment", name, "owner")
    if not owner:
        frappe.throw("Comment not found")
    if owner != frappe.session.user:
        frappe.throw("You can only edit your own comments")
    frappe.db.set_value("Comment", name, "content", content)
    frappe.db.commit()
    comment = frappe.db.get_value("Comment", name, ["name", "content", "comment_email", "owner", "creation"], as_dict=True)
    return comment


@frappe.whitelist(allow_guest=True)
def delete_comment(name=None):
    if not name:
        frappe.throw("name is required")
    owner = frappe.db.get_value("Comment", name, "owner")
    if not owner:
        frappe.throw("Comment not found")
    if owner != frappe.session.user:
        frappe.throw("You can only delete your own comments")
    frappe.db.delete("Comment", name)
    frappe.db.commit()
    return {"status": "ok"}


@frappe.whitelist(allow_guest=True)
def get_notifications():
    try:
        from frappe.core.doctype.notification_log.notification_log import get_notifications
        return get_notifications()
    except Exception:
        return []


@frappe.whitelist(allow_guest=True)
def get_progress_report(project=None, period="daily"):
    today = frappe.utils.today()
    if period == "weekly":
        start = frappe.utils.add_days(today, -7)
    else:
        start = today

    task_filters = {"status": ["in", ["Open", "Working", "Blocked", "Completed"]]}
    if project:
        task_filters["project"] = project

    all_tasks = frappe.get_all(
        "Project Task",
        filters=task_filters,
        fields=["name", "title", "status", "start_date", "due_date", "assigned_to", "estimated_hours", "actual_hours", "project"],
    )

    total_tasks = len(all_tasks)
    completed_tasks = sum(1 for t in all_tasks if t.status == "Completed")
    in_progress_tasks = sum(1 for t in all_tasks if t.status == "Working")
    blocked_tasks = sum(1 for t in all_tasks if t.status == "Blocked")
    overdue_tasks = sum(
        1 for t in all_tasks
        if t.due_date and str(t.due_date) < today and t.status != "Completed"
    )

    time_logs = frappe.get_all(
        "Time Log",
        filters={"date": ["between", [start, today]]},
        fields=["name", "task", "project", "date", "hours", "project_member"],
    )
    if project:
        time_logs = [l for l in time_logs if l.project == project]

    total_hours = sum(l.hours or 0 for l in time_logs)

    deliverable_filters = {}
    if project:
        deliverable_filters["project"] = project
    deliverables = frappe.get_all(
        "Deliverable",
        filters=deliverable_filters,
        fields=["name", "title", "status"],
    )
    total_deliverables = len(deliverables)
    approved_deliverables = sum(1 for d in deliverables if d.status == "Approved")

    return {
        "period": period,
        "start_date": start,
        "end_date": today,
        "tasks": {
            "total": total_tasks,
            "completed": completed_tasks,
            "in_progress": in_progress_tasks,
            "blocked": blocked_tasks,
            "overdue": overdue_tasks,
        },
        "time": {
            "total_hours": total_hours,
        },
        "deliverables": {
            "total": total_deliverables,
            "approved": approved_deliverables,
        },
        "recent_tasks": [
            {"name": t.name, "title": t.title, "status": t.status, "assigned_to": t.assigned_to, "project": t.project}
            for t in all_tasks[:10]
        ],
        "recent_logs": [
            {"name": l.name, "task": l.task, "date": l.date, "hours": l.hours, "member": l.project_member}
            for l in time_logs[:10]
        ],
    }
