import functools

import frappe


def require_roles(*roles):
    """Decorator to restrict a whitelisted method to the given roles."""
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            user_roles = set(frappe.get_roles())
            if not any(r in user_roles for r in roles):
                frappe.throw(
                    "You do not have permission to perform this action",
                    frappe.PermissionError,
                )
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def _erpnext_available():
    try:
        import erpnext  # noqa: F401
        return True
    except ImportError:
        return False


def _valid_purchase_invoice_names(names):
    """Only keep live (non-cancelled) Purchase Invoice names."""
    names = {n for n in names if n}
    if not names:
        return set()
    rows = frappe.get_all(
        "Purchase Invoice",
        filters={"name": ["in", list(names)]},
        fields=["name", "status"],
        ignore_permissions=True,
    )
    return {r.name for r in rows if r.status != "Cancelled"}


def _is_row_billed(row, valid_pi_names):
    return bool(row.get("is_billed") and row.get("purchase_invoice") and row.get("purchase_invoice") in valid_pi_names)


def _get_vendor_rows(project):
    return frappe.get_all(
        "Project Vendors",
        filters={"parent": project},
        fields=["name", "vendor", "supplier", "item", "amount", "is_billed", "purchase_invoice"],
        order_by="creation asc",
    )


def _get_billable_rows(project):
    rows = _get_vendor_rows(project)
    valid_pi = _valid_purchase_invoice_names({r.get("purchase_invoice") for r in rows})
    return [r for r in rows if (r.get("amount") or 0) > 0 and not _is_row_billed(r, valid_pi)]


def _ensure_supplier(vendor_row):
    """Return an ERPNext Supplier for a project vendor row, auto-creating one if needed."""
    if vendor_row.get("supplier"):
        return vendor_row["supplier"]
    if not frappe.db.exists("Vendor", vendor_row["vendor"]):
        frappe.throw(f"Vendor {vendor_row['vendor']} not found", frappe.ValidationError)
    vendor_doc = frappe.get_doc("Vendor", vendor_row["vendor"])
    name = (vendor_doc.vendor_name or vendor_doc.name or vendor_row["vendor"]).strip()
    if frappe.db.exists("Supplier", name):
        return name
    supplier = frappe.new_doc("Supplier")
    supplier.supplier_name = name
    supplier.supplier_group = "Services"
    if vendor_doc.email:
        supplier.email_id = vendor_doc.email
    supplier.insert(ignore_permissions=True)
    frappe.db.commit()
    return supplier.name


def _resolve_item(data, vendor_row):
    """Pick a purchase item for a vendor row (row.item, else data.item, else any buy item)."""
    if vendor_row.get("item") and frappe.db.exists("Item", vendor_row["item"]):
        return vendor_row["item"]
    item = (data or {}).get("item")
    if item and frappe.db.exists("Item", item):
        return item
    items = frappe.get_all("Item", filters={"is_purchase_item": 1}, fields=["name", "stock_uom", "sales_uom"], limit=1)
    if items:
        return items[0].name
    return None


@frappe.whitelist()
@require_roles("Project Manager", "System Manager")
def get_purchase_config():
    """Return ERPNext purchase setup data (companies, currencies, buy items,
    and suppliers) for the vendor form."""
    if not _erpnext_available():
        frappe.throw("ERPNext app is not installed. Please install ERPNext to use purchasing.", frappe.ValidationError)

    companies = frappe.get_all("Company", fields=["name", "default_currency"], order_by="name asc", limit=50)
    currencies = frappe.get_all("Currency", fields=["name"], order_by="name asc", limit=100)
    items = frappe.get_all("Item", filters={"is_purchase_item": 1}, fields=["name", "stock_uom", "sales_uom"], order_by="name asc", limit=50)
    suppliers = frappe.get_all("Supplier", fields=["name", "supplier_name"], order_by="name asc", limit=100)

    return {
        "companies": [{"label": c.name, "value": c.name, "default_currency": c.default_currency} for c in companies],
        "currencies": [{"label": c.name, "value": c.name} for c in currencies],
        "items": [{"label": f"{i.name} ({i.stock_uom or i.sales_uom or 'UOM'})", "value": i.name} for i in items],
        "suppliers": [{"label": s.supplier_name or s.name, "value": s.name} for s in suppliers],
        "default_currency": frappe.db.get_single_value("Global Defaults", "default_currency"),
    }


@frappe.whitelist()
@require_roles("Project Manager", "System Manager")
def get_purchase_billing(project=None):
    """Return purchasing data for a project: vendor rows (with amounts/billed
    status), linked Purchase Invoices, and setup data for the UI."""
    if not project:
        frappe.throw("Project name is required")

    project_doc = frappe.get_doc("Project Info", project)
    rows = _get_vendor_rows(project)

    valid_pi = _valid_purchase_invoice_names({r.get("purchase_invoice") for r in rows})
    for r in rows:
        if not _is_row_billed(r, valid_pi):
            r["is_billed"] = 0

    invoices = []
    if valid_pi:
        invoices = frappe.get_all(
            "Purchase Invoice",
            filters={"name": ["in", sorted(valid_pi)]},
            fields=["name", "posting_date", "grand_total", "status", "currency", "outstanding_amount"],
            order_by="posting_date desc",
            limit=50,
            ignore_permissions=True,
        )
        for inv in invoices:
            inv["paid_amount"] = max(0, (inv.get("grand_total") or 0) - (inv.get("outstanding_amount") or 0))

    companies = frappe.get_all("Company", fields=["name", "default_currency"], order_by="name asc", limit=50)
    currencies = frappe.get_all("Currency", fields=["name"], order_by="name asc", limit=100)
    items = frappe.get_all("Item", filters={"is_purchase_item": 1}, fields=["name", "stock_uom", "sales_uom"], order_by="name asc", limit=50)
    suppliers = frappe.get_all("Supplier", fields=["name", "supplier_name"], order_by="name asc", limit=100)

    return {
        "project_name": project_doc.project_name,
        "billing_company": project_doc.billing_company,
        "billing_currency": project_doc.billing_currency,
        "vendor_rows": rows,
        "invoices": invoices,
        "config": {
            "companies": [{"label": c.name, "value": c.name, "default_currency": c.default_currency} for c in companies],
            "currencies": [{"label": c.name, "value": c.name} for c in currencies],
            "items": [{"label": f"{i.name} ({i.stock_uom or i.sales_uom or 'UOM'})", "value": i.name} for i in items],
            "suppliers": [{"label": s.supplier_name or s.name, "value": s.name} for s in suppliers],
            "default_currency": frappe.db.get_single_value("Global Defaults", "default_currency"),
        },
    }


@frappe.whitelist()
@require_roles("Project Manager", "System Manager")
def create_purchase_invoice(project=None, data=None):
    """Generate a Purchase Invoice from a project's unbilled vendor rows."""
    if not project:
        frappe.throw("Project name is required")
    if not _erpnext_available():
        frappe.throw("ERPNext app is not installed. Please install ERPNext to use purchasing.", frappe.ValidationError)

    if isinstance(data, str):
        import json
        data = json.loads(data)
    data = data or {}

    project_doc = frappe.get_doc("Project Info", project)
    rows = _get_billable_rows(project)
    if not rows:
        frappe.throw("No billable (unbilled, amount > 0) vendor purchases found for this project.", frappe.ValidationError)

    company = data.get("company") or project_doc.billing_company
    if not company:
        frappe.throw("Please select a Company before creating a purchase invoice.", frappe.ValidationError)

    currency = data.get("currency") or project_doc.billing_currency
    if not currency:
        currency = frappe.db.get_single_value("Global Defaults", "default_currency")
    if not currency:
        frappe.throw("Please specify a currency", frappe.ValidationError)

    # Group billable rows by supplier so each vendor gets its own invoice,
    # each under the correct supplier name.
    by_supplier = {}
    for row in rows:
        item = _resolve_item(data, row)
        if not item:
            frappe.throw("No purchase Item found for vendor purchase. Create an Item with is_purchase_item = 1.", frappe.ValidationError)
        supplier = _ensure_supplier(row)
        item_doc = frappe.get_doc("Item", item)
        uom = data.get("uom") or item_doc.sales_uom or item_doc.stock_uom
        by_supplier.setdefault(supplier, []).append({
            "row_name": row["name"],
            "item_code": item,
            "uom": uom,
            "rate": row["amount"],
            "amount": row["amount"],
            "description": f"Purchase: {row.get('vendor')}",
        })

    created = []
    for supplier, items in by_supplier.items():
        invoice = frappe.new_doc("Purchase Invoice")
        invoice.company = company
        invoice.currency = currency
        invoice.supplier = supplier
        invoice.set_posting_time = 1
        invoice.posting_date = data.get("posting_date") or frappe.utils.today()
        if data.get("due_date"):
            invoice.due_date = data["due_date"]
        invoice.remarks = data.get("remark") or f"Purchase Invoice for project {project_doc.project_name}"

        for it in items:
            row = invoice.append("items", {})
            row.item_code = it["item_code"]
            row.qty = 1
            row.uom = it["uom"]
            row.rate = it["rate"]
            row.description = it["description"]

        invoice.insert(ignore_permissions=True)

        for it in items:
            frappe.db.set_value("Project Vendors", it["row_name"], "is_billed", 1)
            frappe.db.set_value("Project Vendors", it["row_name"], "purchase_invoice", invoice.name)

        created.append({
            "name": invoice.name,
            "supplier": invoice.supplier,
            "grand_total": invoice.grand_total,
            "currency": invoice.currency,
            "status": invoice.status,
            "rows_billed": len(items),
        })

    frappe.db.commit()

    if not created:
        frappe.throw("No purchase invoice was created.", frappe.ValidationError)
    return {
        "invoices": created,
        "count": len(created),
    }


@frappe.whitelist()
@require_roles("Project Manager", "System Manager")
def get_purchase_invoice(name=None):
    if not name:
        frappe.throw("Purchase Invoice name is required")
    if not _erpnext_available():
        frappe.throw("ERPNext app is not installed.", frappe.ValidationError)
    try:
        doc = frappe.get_doc("Purchase Invoice", name)
    except frappe.DoesNotExistError:
        frappe.throw("Purchase Invoice not found")
    return _format_purchase_invoice(doc)


@frappe.whitelist()
@require_roles("Project Manager", "System Manager")
def submit_purchase_invoice(name=None):
    if not name:
        frappe.throw("Purchase Invoice name is required")
    if not _erpnext_available():
        frappe.throw("ERPNext app is not installed.", frappe.ValidationError)
    try:
        doc = frappe.get_doc("Purchase Invoice", name)
    except frappe.DoesNotExistError:
        frappe.throw("Purchase Invoice not found")

    if doc.docstatus == 1:
        return _format_purchase_invoice(doc)

    doc.flags.ignore_permissions = True
    doc.submit()
    frappe.db.commit()
    return _format_purchase_invoice(frappe.get_doc("Purchase Invoice", name))


def _format_purchase_invoice(doc):
    items = []
    for it in doc.items:
        items.append({
            "item_code": it.item_code,
            "item_name": it.item_name,
            "description": it.description,
            "qty": it.qty,
            "uom": it.uom,
            "rate": it.rate,
            "amount": it.amount,
        })

    taxes = []
    for t in doc.taxes:
        taxes.append({
            "account_head": t.account_head,
            "description": t.description,
            "tax_amount": t.tax_amount,
        })

    outstanding = doc.outstanding_amount
    return {
        "name": doc.name,
        "supplier": doc.supplier,
        "supplier_name": doc.supplier_name,
        "company": doc.company,
        "currency": doc.currency,
        "grand_total": doc.grand_total,
        "net_total": doc.net_total,
        "total_taxes_and_charges": doc.total_taxes_and_charges,
        "posting_date": doc.posting_date,
        "due_date": doc.due_date,
        "status": doc.status,
        "docstatus": doc.docstatus,
        "remarks": doc.remarks,
        "outstanding_amount": outstanding,
        "paid_amount": max(0, (doc.grand_total or 0) - (outstanding or 0)),
        "items": items,
        "taxes": taxes,
    }
