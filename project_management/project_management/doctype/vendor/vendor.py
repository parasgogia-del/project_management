# Copyright (c) 2026, Paras Gogia and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Vendor(Document):
	def after_insert(self):
		self._ensure_vendor_role()

	def on_update(self):
		self._ensure_vendor_role()

	def _ensure_vendor_role(self):
		if not self.user:
			return
		user = frappe.get_doc("User", self.user)
		if "Vendor" in [r.role for r in user.roles]:
			return
		user.append("roles", {"role": "Vendor"})
		user.flags.ignore_permissions = True
		user.save(ignore_permissions=True)
		frappe.db.commit()
