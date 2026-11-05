import frappe
from frappe import _
from frappe.utils.file_manager import save_file

PROJECT = "Project Info"
DELIVERABLE = "Deliverable"
TASK = "Project Task"


def check_access(doctype, name, ptype):
    if not frappe.db.exists(doctype, name):
        frappe.throw(_("{0} {1} not found").format(doctype, name), frappe.DoesNotExistError)
    frappe.has_permission(doctype, ptype, name, throw=True)


def upload_attached_file(doctype, name):
    check_access(doctype, name, "write")

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


def list_attached_files(doctype, name):
    check_access(doctype, name, "read")

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


def delete_attached_file(file_name, doctype):
    file = frappe.db.get_value(
        "File",
        file_name,
        ["attached_to_doctype", "attached_to_name"],
        as_dict=True,
    )

    if not file:
        frappe.throw(_("File not found"), frappe.DoesNotExistError)

    if file.attached_to_doctype != doctype:
        frappe.throw(_("Not permitted"), frappe.PermissionError)


    check_access(doctype, file.attached_to_name, "write")

    frappe.delete_doc("File", file_name, ignore_permissions=True)

    return {"message": "Deleted"}


@frappe.whitelist()
def upload_project_file(project):
    return upload_attached_file(PROJECT, project)


@frappe.whitelist()
def get_project_files(project):
    return list_attached_files(PROJECT, project)


@frappe.whitelist()
def delete_project_file(file_name):
    return delete_attached_file(file_name, PROJECT)


@frappe.whitelist()
def upload_deliverable_file(deliverable):
    return upload_attached_file(DELIVERABLE, deliverable)


@frappe.whitelist()
def get_deliverable_files(deliverable):
    return list_attached_files(DELIVERABLE, deliverable)


@frappe.whitelist()
def delete_deliverable_file(file_name):
    return delete_attached_file(file_name, DELIVERABLE)


@frappe.whitelist()
def upload_task_file(task):
    return upload_attached_file(TASK, task)


@frappe.whitelist()
def get_task_files(task):
    return list_attached_files(TASK, task)


@frappe.whitelist()
def delete_task_file(file_name):
    return delete_attached_file(file_name, TASK)
