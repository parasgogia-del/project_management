import frappe

from project_management.api.client import can_manage_deliverable

VENDOR_ROLES = ("Project Manager", "Vendor", "System Manager")


def resolve_vendor_name(vendor_name=None):
	if vendor_name and set(frappe.get_roles()) & {"Project Manager", "System Manager"}:
		return vendor_name
	names = frappe.get_all("Vendor", filters={"user": frappe.session.user}, pluck="name")
	return names[0] if names else None


def get_vendor_project_names(vendor_name):
	return frappe.get_all(
		"Project Vendors",
		filters={"vendor": vendor_name},
		pluck="parent",
	)


@frappe.whitelist()
def get_vendor_projects(vendor_name=None):
	frappe.only_for(VENDOR_ROLES)
	vendor_name = resolve_vendor_name(vendor_name)
	if not vendor_name:
		return []

	project_names = get_vendor_project_names(vendor_name)
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
def get_vendor_project(name=None):
	frappe.only_for(VENDOR_ROLES)
	if not name:
		frappe.throw("Project name is required")

	vendor_name = resolve_vendor_name()
	if not vendor_name:
		return None

	if name not in get_vendor_project_names(vendor_name):
		frappe.throw("You are not associated with this project", frappe.PermissionError)

	project = frappe.get_doc("Project Info", name)
	data = {
		"name": project.name,
		"project_name": project.project_name,
		"status": project.status,
		"progress": project.progress,
		"client": project.client,
		"start_date": project.start_date,
		"end_date": project.end_date,
		"description": project.description,
	}

	data["deliverables"] = frappe.get_all(
		"Deliverable",
		filters={"project": name},
		fields=[
			"name",
			"title",
			"status",
			"due_date",
			"description",
			"submitted_by",
			"delivery_date",
		],
		order_by="creation desc",
	)

	data["tasks"] = frappe.get_all(
		"Project Task",
		filters={"project": name, "assigned_vendor": vendor_name},
		fields=[
			"name",
			"title",
			"deliverable",
			"status",
			"priority",
			"due_date",
			"description",
		],
		order_by="creation desc",
	)

	return data


@frappe.whitelist()
def get_vendor_deliverables(vendor_name=None):
	frappe.only_for(VENDOR_ROLES)
	vendor_name = resolve_vendor_name(vendor_name)
	if not vendor_name:
		return []

	project_names = get_vendor_project_names(vendor_name)
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
def get_vendor_tasks(vendor_name=None):
	frappe.only_for(VENDOR_ROLES)
	vendor_name = resolve_vendor_name(vendor_name)
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
def submit_deliverable(name=None, file_url=None, notes=None):
	frappe.only_for(VENDOR_ROLES)
	if not name:
		frappe.throw("Deliverable name is required")

	deliverable = frappe.get_doc("Deliverable", name)
	if not can_manage_deliverable(deliverable):
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
