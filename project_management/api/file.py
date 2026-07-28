import frappe
from frappe.utils.file_manager import save_file


@frappe.whitelist(allow_guest=True)
def upload_project_file(project):
    if "file" not in frappe.request.files:
        frappe.throw("No file uploaded")

    uploaded_file = frappe.request.files["file"]

    file_doc = save_file(
        uploaded_file.filename,
        uploaded_file.read(),
        "Project Info",
        project,
        is_private=0,
    )

    result = file_doc.as_dict()
    result.file_url = frappe.utils.get_url(result.file_url)
    return result


@frappe.whitelist(allow_guest=True)
def get_project_files(project):
    files = frappe.get_all(
        "File",
        filters={
            "attached_to_doctype": "Project Info",
            "attached_to_name": project,
        },
        fields=[
            "name",
            "file_name",
            "file_url",
            "is_private",
            "creation",
        ],
        order_by="creation desc",
    )

    for f in files:
        f.file_url = frappe.utils.get_url(f.file_url)

    return files


@frappe.whitelist(allow_guest=True)
def delete_project_file(file_name):
    if not frappe.db.exists("File", file_name):
        frappe.throw("File not found")

    frappe.delete_doc("File", file_name, ignore_permissions=True)
    frappe.db.commit()

    return {"message": "Deleted"}


@frappe.whitelist(allow_guest=True)
def upload_deliverable_file(deliverable):
    if "file" not in frappe.request.files:
        frappe.throw("No file uploaded")

    uploaded_file = frappe.request.files["file"]

    file_doc = save_file(
        uploaded_file.filename,
        uploaded_file.read(),
        "Deliverable",
        deliverable,
        is_private=0,
    )

    result = file_doc.as_dict()
    result.file_url = frappe.utils.get_url(result.file_url)
    return result


@frappe.whitelist(allow_guest=True)
def get_deliverable_files(deliverable):
    files = frappe.get_all(
        "File",
        filters={
            "attached_to_doctype": "Deliverable",
            "attached_to_name": deliverable,
        },
        fields=[
            "name",
            "file_name",
            "file_url",
            "is_private",
            "creation",
        ],
        order_by="creation desc",
    )

    for f in files:
        f.file_url = frappe.utils.get_url(f.file_url)

    return files


@frappe.whitelist(allow_guest=True)
def delete_deliverable_file(file_name):
    if not frappe.db.exists("File", file_name):
        frappe.throw("File not found")

    frappe.delete_doc("File", file_name, ignore_permissions=True)
    frappe.db.commit()

    return {"message": "Deleted"}
