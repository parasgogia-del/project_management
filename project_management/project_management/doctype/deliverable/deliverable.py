# Copyright (c) 2026, Paras Gogia and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Deliverable(Document):

    def before_insert(self):
        if not self.submitted_by:
            self.submitted_by = frappe.session.user

    def on_update(self):
        if self.workflow_state == "Approved" and not self.delivery_date:
            self.db_set("delivery_date", frappe.utils.today())
