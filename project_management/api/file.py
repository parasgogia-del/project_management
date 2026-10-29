import frappe
from frappe import _
from frappe.utils.file_manager import save_file

# Ek hi jagah config: har type ka DocType
PROJECT = "Project Info"
DELIVERABLE = "Deliverable"
TASK = "Project Task"


def _check_access(doctype, name, ptype):
    """User ko is record par permission na ho to error."""
    if not frappe.db.exists(doctype, name):
        frappe.throw(_("{0} {1} not found").format(doctype, name), frappe.DoesNotExistError)
    frappe.has_permission(doctype, ptype, name, throw=True)


def _upload(doctype, name):
    _check_access(doctype, name, "write")

    if "file" not in frappe.request.files:
        frappe.throw(_("No file uploaded"))

    uploaded_file = frappe.request.files["file"]

    file_doc = save_file(
        uploaded_file.filename,
        uploaded_file.read(),
        doctype,
        name,
        is_private=1,
    )

    result = file_doc.as_dict()
    result.file_url = frappe.utils.get_url(result.file_url)
    return result


def _list(doctype, name):
    _check_access(doctype, name, "read")

    files = frappe.get_all(
        "File",
        filters={
            "attached_to_doctype": doctype,
            "attached_to_name": name,
        },
        fields=["name", "file_name", "file_url", "is_private", "creation"],
        order_by="creation desc",
    )

    for f in files:
        f.file_url = frappe.utils.get_url(f.file_url)

    return files


def _delete(file_name, doctype):
    file = frappe.db.get_value(
        "File",
        file_name,
        ["attached_to_doctype", "attached_to_name"],
        as_dict=True,
    )

    if not file:
        frappe.throw(_("File not found"), frappe.DoesNotExistError)

    # Ye file isi type ke record ki honi chahiye
    if file.attached_to_doctype != doctype:
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    # User ko us parent record par write permission honi chahiye
    _check_access(doctype, file.attached_to_name, "write")

    # Permission upar hum khud check kar chuke hain
    frappe.delete_doc("File", file_name, ignore_permissions=True)

    return {"message": "Deleted"}


# ---------- Project ----------
@frappe.whitelist()
def upload_project_file(project):
    return _upload(PROJECT, project)


@frappe.whitelist()
def get_project_files(project):
    return _list(PROJECT, project)


@frappe.whitelist()
def delete_project_file(file_name):
    return _delete(file_name, PROJECT)


# ---------- Deliverable ----------
@frappe.whitelist()
def upload_deliverable_file(deliverable):
    return _upload(DELIVERABLE, deliverable)


@frappe.whitelist()
def get_deliverable_files(deliverable):
    return _list(DELIVERABLE, deliverable)


@frappe.whitelist()
def delete_deliverable_file(file_name):
    return _delete(file_name, DELIVERABLE)


# ---------- Task ----------
@frappe.whitelist()
def upload_task_file(task):
    return _upload(TASK, task)


@frappe.whitelist()
def get_task_files(task):
    return _list(TASK, task)


@frappe.whitelist()
def delete_task_file(file_name):
    return _delete(file_name, TASK)
