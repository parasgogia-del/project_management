import functools
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
