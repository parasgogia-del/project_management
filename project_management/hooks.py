app_name = "project_management"
app_title = "Project Management"
app_publisher = "Paras Gogia"
app_description = "Project Management Application"
app_email = "paras.gogia@korecent.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "project_management",
# 		"logo": "/assets/project_management/logo.png",
# 		"title": "Project Management",
# 		"route": "/project_management",
# 		"has_permission": "project_management.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/project_management/css/project_management.css"
# app_include_js = "/assets/project_management/js/project_management.js"

# include js, css files in header of web template
# web_include_css = "/assets/project_management/css/project_management.css"
# web_include_js = "/assets/project_management/js/project_management.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "project_management/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "project_management/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
home_page = "project_management"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
jinja = {
	"methods": [
		"project_management.utils.vite_assets.get_vite_js",
		"project_management.utils.vite_assets.get_vite_css",
	]
}

# CSRF Exempt
csrf_exempt = [
	"project_management.api.client.get_progress_report",
	"project_management.api.client.get_tasks",
	"project_management.api.client.get_task",
	"project_management.api.client.get_projects",
	"project_management.api.client.get_project",
	"project_management.api.client.get_deliverables",
	"project_management.api.client.get_deliverable",
	"project_management.api.client.get_deliverables_with_details",
	"project_management.api.client.get_time_logs",
	"project_management.api.client.get_comments",
	"project_management.api.client.get_gantt_tasks",
	"project_management.api.client.get_session_user",
	"project_management.api.client.get_csrf_token",
	"project_management.api.client.get_notifications",
	"project_management.api.client.create_project",
	"project_management.api.client.create_task",
	"project_management.api.client.create_time_log",
	"project_management.api.client.update_project",
	"project_management.api.client.update_task_status",
	"project_management.api.client.update_deliverable_status",
	"project_management.api.client.add_comment",
	"project_management.api.client.edit_comment",
	"project_management.api.client.delete_comment",
	"project_management.api.client.delete_project",
	"project_management.api.client.update_task",
	"project_management.api.client.toggle_today_focus",
	"project_management.api.client.get_today_hours",
	"project_management.api.vendor.get_vendor_projects",
	"project_management.api.vendor.get_vendor_deliverables",
	"project_management.api.vendor.get_vendor_tasks",
	"project_management.api.file.upload_project_file",
	"project_management.api.file.get_project_files",
	"project_management.api.file.delete_project_file",
	"project_management.api.file.upload_deliverable_file",
	"project_management.api.file.get_deliverable_files",
	"project_management.api.file.delete_deliverable_file",
	"project_management.api.file.upload_task_file",
	"project_management.api.file.get_task_files",
	"project_management.api.file.delete_task_file",
]

# Installation
# ------------

# before_install = "project_management.install.before_install"
# after_install = "project_management.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "project_management.uninstall.before_uninstall"
# after_uninstall = "project_management.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "project_management.utils.before_app_install"
# after_app_install = "project_management.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "project_management.utils.before_app_uninstall"
# after_app_uninstall = "project_management.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "project_management.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "project_management.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"project_management.tasks.all"
# 	],
# 	"daily": [
# 		"project_management.tasks.daily"
# 	],
# 	"hourly": [
# 		"project_management.tasks.hourly"
# 	],
# 	"weekly": [
# 		"project_management.tasks.weekly"
# 	],
# 	"monthly": [
# 		"project_management.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "project_management.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "project_management.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "project_management.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "project_management.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["project_management.utils.before_request"]
# after_request = ["project_management.utils.after_request"]

# Job Events
# ----------
# before_job = ["project_management.utils.before_job"]
# after_job = ["project_management.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"project_management.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

# Website Route Rules (SPA)
# -------------------------
website_route_rules = [
    {
        "from_route": "/project_management/<path:app_path>",
        "to_route": "project_management",
    },
]

