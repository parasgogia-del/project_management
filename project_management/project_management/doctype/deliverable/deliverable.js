// Copyright (c) 2026, Paras Gogia and contributors
// For license information, please see license.txt

frappe.ui.form.on("Deliverable", {
    refresh(frm) {
        frm.fields_dict.tasks.grid.get_field("task").get_query = function(doc) {
            return {
                filters: {
                    project: doc.project
                }
            };
        };
    }
});
