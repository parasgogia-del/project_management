import re

import frappe

ALLOWED_SIGNUP_ROLES = ["Project Member", "Client", "Vendor"]


@frappe.whitelist(allow_guest=True)
def create_portal_user(full_name=None, email=None, password=None, role=None):
    if not full_name or not email or not password:
        frappe.throw("Full name, email and password are required")

    if len(password) < 6:
        frappe.throw("Password must be at least 6 characters long")

    if role not in ALLOWED_SIGNUP_ROLES:
        frappe.throw("Invalid role", frappe.ValidationError)

    email = email.strip().lower()
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        frappe.throw("Please enter a valid email address")

    if frappe.db.exists("User", email):
        frappe.throw(f"A user with email {email} already exists")

    user = frappe.get_doc({
        "doctype": "User",
        "email": email,
        "first_name": full_name.strip(),
        "enabled": 1,
        "send_welcome_email": 0,
        "roles": [{"role": role}],
    })
    user.insert(ignore_permissions=True)
    user.new_password = password
    user.save(ignore_permissions=True)

    frappe.db.commit()
    return {"status": "ok"}
