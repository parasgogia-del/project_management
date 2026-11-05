import frappe
from frappe.rate_limiter import rate_limit
from frappe.utils import validate_email_address


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=5, seconds=60 * 60)
def create_portal_user(full_name=None, email=None, password=None):
    if not full_name or not email or not password:
        frappe.throw("Full name, email and password are required")

    full_name = full_name.strip()
    if len(full_name) > 140:
        frappe.throw("Name is too long")

    if len(password) < 8:
        frappe.throw("Password must be at least 8 characters long")

    email = email.strip().lower()
    validate_email_address(email, throw=True)

    if frappe.db.exists("User", email):
        frappe.throw("Unable to create account with these details")

    user = frappe.get_doc({
        "doctype": "User",
        "email": email,
        "first_name": full_name,
        "enabled": 1,
        "user_type": "Website User",
        "send_welcome_email": 0,
        "new_password": password,
    })
    user.flags.ignore_permissions = True
    user.insert()

    frappe.db.commit()
    return {"status": "ok"}
