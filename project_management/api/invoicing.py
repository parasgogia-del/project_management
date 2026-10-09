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
    """Whether ERPNext app is installed and importable."""
    try:
        import erpnext  # noqa: F401
        return True
    except ImportError:
        return False


def _valid_invoice_names(invoice_names):
    """Return only the given invoice names that are live (not Cancelled).

    A deliverable is only considered truly billed when its linked Sales
    Invoice is valid. Deliverables pointing at Cancelled invoices (or with a
    stale/empty link) must be billable again.
    """
    invoice_names = {n for n in invoice_names if n}
    if not invoice_names:
        return set()
    rows = frappe.get_all(
        "Sales Invoice",
        filters={"name": ["in", list(invoice_names)]},
        fields=["name", "status"],
        ignore_permissions=True,
    )
    return {r.name for r in rows if r.status != "Cancelled"}


def _is_deliverable_billed(d, valid_invoice_names):
    """A deliverable is billed only if marked billed AND linked to a valid,
    non-cancelled Sales Invoice."""
    return bool(d.is_billed and d.sales_invoice and d.sales_invoice in valid_invoice_names)


@frappe.whitelist()
@require_roles("Project Manager", "System Manager")
def get_billing_config():
    """Return ERPNext setup data needed for the billing UI:
    customers, companies, currencies, and default item/selling settings."""
    if not _erpnext_available():
        frappe.throw("ERPNext app is not installed. Please install ERPNext to use invoicing.", frappe.ValidationError)

    customers = frappe.get_all(
        "Customer",
        filters={"disabled": 0},
        fields=["name", "customer_name", "customer_group", "territory"],
        order_by="customer_name asc",
        limit=50,
    )
    companies = frappe.get_all("Company", fields=["name", "default_currency"], order_by="name asc", limit=50)
    currencies = frappe.get_all("Currency", fields=["name"], order_by="name asc", limit=100)

    item = None
    if frappe.db.exists("Item", {"is_sales_item": 1}):
        first_item = frappe.get_all("Item", filters={"is_sales_item": 1}, fields=["name", "stock_uom", "sales_uom"], limit=1)
        item = first_item[0] if first_item else None

    sell_settings = frappe.get_single("Selling Settings")
    default_currency = frappe.db.get_single_value("Global Defaults", "default_currency")

    return {
        "customers": customers,
        "companies": [
            {"label": c.name, "value": c.name, "default_currency": c.default_currency}
            for c in companies
        ],
        "currencies": [{"label": c.name, "value": c.name} for c in currencies],
        "items": [
            {"label": f"{it.name} ({it.stock_uom or it.sales_uom or 'UOM'})", "value": it.name}
            for it in frappe.get_all("Item", filters={"is_sales_item": 1}, fields=["name", "stock_uom", "sales_uom"], order_by="name asc", limit=50)
        ],
        "default_item": {"label": item.name if item else None, "value": item.name if item else None, "name": item.name if item else None},
        "default_currency": default_currency,
        "allow_multiple_items": bool(getattr(sell_settings, "allow_multiple_items", 0)),
    }


@frappe.whitelist()
@require_roles("Project Manager", "System Manager")
def get_project_billing(project=None):
    """Return billing-relevant data for a project: project setup, deliverables
    (with amounts and billed status), and existing sales invoices."""
    if not project:
        frappe.throw("Project name is required")

    project_doc = frappe.get_doc("Project Info", project)

    deliverables = frappe.get_all(
        "Deliverable",
        filters={"project": project},
        fields=["name", "title", "status", "amount", "is_billed", "sales_invoice", "delivery_date"],
        order_by="creation desc",
    )

    # Cancelled invoices from ERPNext must not count toward the project's
    # invoiced/paid/outstanding totals. A deliverable is only considered billed
    # when linked to a valid (non-cancelled) Sales Invoice; otherwise it is
    # billable again so it can be (re-)invoiced.
    invoice_names = {d.sales_invoice for d in deliverables if d.sales_invoice}
    valid_invoices = _valid_invoice_names(invoice_names)

    for d in deliverables:
        if not _is_deliverable_billed(d, valid_invoices):
            d.is_billed = 0

    invoices = []
    if valid_invoices:
        invoices = frappe.get_all(
            "Sales Invoice",
            filters={"name": ["in", sorted(valid_invoices)]},
            fields=["name", "posting_date", "grand_total", "status", "currency", "paid_amount", "outstanding_amount"],
            order_by="posting_date desc",
            limit=50,
            ignore_permissions=True,
        )
        for inv in invoices:
            # ERPNext's paid_amount isn't reliably updated by Payment Entries;
            # derive it from grand_total - outstanding instead.
            inv.paid_amount = max(0, (inv.grand_total or 0) - (inv.outstanding_amount or 0))

    return {
        "project_name": project_doc.project_name,
        "customer": project_doc.customer,
        "billing_currency": project_doc.billing_currency,
        "billing_company": project_doc.billing_company,
        "taxes_and_charges": project_doc.taxes_and_charges,
        "deliverables": deliverables,
        "invoices": invoices,
    }


def _resolve_item(project_doc, billing_data):
    """Pick a default sellable item for the invoice."""
    # User-supplied item
    item = (billing_data or {}).get("item")
    if item and frappe.db.exists("Item", item):
        return item

    # Fall back to any sellable item
    items = frappe.get_all("Item", filters={"is_sales_item": 1}, fields=["name", "stock_uom", "sales_uom"], limit=1)
    if items:
        return items[0].name

    return None


@frappe.whitelist()
@require_roles("Project Manager", "System Manager")
def create_sales_invoice(project=None, data=None):
    """Generate a Sales Invoice from a project's billed deliverables.

    Positional 'data' (dict or JSON):
      - item: name of the item to bill
      - uom: unit of measure (defaults to item's sales_uom or stock_uom)
      - delivery_note: optional delivery note reference
      - due_date: invoice due date
      - posting_date: invoice date (defaults to today)
      - remark: remark on the invoice

    Only deliverables with amount > 0, status 'Approved', and not already
    billed are included. The invoice is created as a 'Draft'. Deliverables are
    marked billed and linked to the generated invoice.
    """
    if not project:
        frappe.throw("Project name is required")
    if not _erpnext_available():
        frappe.throw("ERPNext app is not installed. Please install ERPNext to use invoicing.", frappe.ValidationError)

    if isinstance(data, str):
        import json
        data = json.loads(data)
    data = data or {}

    project_doc = frappe.get_doc("Project Info", project)

    if not project_doc.customer:
        frappe.throw("Please select a Customer on the project before creating an invoice.", frappe.ValidationError)

    company = data.get("company") or project_doc.billing_company
    if not company:
        frappe.throw("Please select a Company on the project (or pass one) before creating an invoice.", frappe.ValidationError)

    amount_field = data.get("amount_field", "amount")
    if amount_field not in ("amount",):
        frappe.throw("Invalid amount field", frappe.ValidationError)

    deliverables = frappe.get_all(
        "Deliverable",
        filters={
            "project": project,
            "status": "Approved",
        },
        fields=["name", "title", "amount", "is_billed", "sales_invoice"],
        order_by="creation asc",
    )

    # A deliverable is billable only if it's not already on a valid,
    # non-cancelled invoice. This lets users re-bill deliverables that were
    # cancelled, or those erroneously flagged billed without a live invoice.
    valid_invoices = _valid_invoice_names({d.sales_invoice for d in deliverables})
    billable = [
        d for d in deliverables
        if (d.amount or 0) > 0 and not _is_deliverable_billed(d, valid_invoices)
    ]
    if not billable:
        frappe.throw("No billable (approved, unbilled, amount > 0) deliverables found for this project.", frappe.ValidationError)

    item = _resolve_item(project_doc, data)
    if not item:
        frappe.throw("No sellable Item found. Please create at least one Item in ERPNext (is_sales_item = 1).", frappe.ValidationError)

    item_doc = frappe.get_doc("Item", item)
    uom = data.get("uom") or item_doc.sales_uom or item_doc.stock_uom

    currency = data.get("currency") or project_doc.billing_currency
    if not currency:
        currency = frappe.db.get_single_value("Global Defaults", "default_currency")
    if not currency:
        frappe.throw("Please specify a currency", frappe.ValidationError)

    posting_date = data.get("posting_date") or frappe.utils.today()
    due_date = data.get("due_date")

    # Build invoice items, one per deliverable amount
    items = []
    for d in billable:
        items.append({
            "item_code": item,
            "qty": 1,
            "uom": uom,
            "rate": d.amount,
            "amount": d.amount,
            "description": d.title,
            "deliverable": d.name,
        })

    invoice = frappe.new_doc("Sales Invoice")
    invoice.customer = project_doc.customer
    invoice.company = company
    invoice.currency = currency
    invoice.set_posting_time = 1
    invoice.posting_date = posting_date
    if due_date:
        invoice.due_date = due_date
    invoice.remarks = data.get("remark") or f"Sales Invoice for project {project_doc.project_name}"
    if project_doc.taxes_and_charges:
        invoice.taxes_and_charges = project_doc.taxes_and_charges

    for it in items:
        row = invoice.append("items", {})
        row.item_code = it["item_code"]
        row.qty = it["qty"]
        row.uom = it["uom"]
        row.rate = it["rate"]
        row.description = it["description"]

    invoice.insert(ignore_permissions=True)

    # Mark deliverables as billed and link them to the invoice
    for it in items:
        frappe.db.set_value("Deliverable", it["deliverable"], "is_billed", 1)
        frappe.db.set_value("Deliverable", it["deliverable"], "sales_invoice", invoice.name)

    frappe.db.commit()

    return {
        "name": invoice.name,
        "customer": invoice.customer,
        "grand_total": invoice.grand_total,
        "currency": invoice.currency,
        "status": invoice.status,
        "billable_count": len(items),
        "item": item,
        "uom": uom,
    }


@frappe.whitelist()
@require_roles("Project Manager", "System Manager")
def get_sales_invoice(name=None):
    """Fetch a single Sales Invoice by name for viewing in the portal."""
    if not name:
        frappe.throw("Sales Invoice name is required")
    if not _erpnext_available():
        frappe.throw("ERPNext app is not installed.", frappe.ValidationError)
    try:
        doc = frappe.get_doc("Sales Invoice", name)
        return _format_sales_invoice(doc)
    except frappe.DoesNotExistError:
        frappe.throw("Sales Invoice not found")

@frappe.whitelist()
@require_roles("Project Manager", "System Manager")
def submit_sales_invoice(name=None):
    """Submit a Draft Sales Invoice so it can be booked/emailed."""
    if not name:
        frappe.throw("Sales Invoice name is required")
    if not _erpnext_available():
        frappe.throw("ERPNext app is not installed.", frappe.ValidationError)
    try:
        doc = frappe.get_doc("Sales Invoice", name)
    except frappe.DoesNotExistError:
        frappe.throw("Sales Invoice not found")

    if doc.docstatus == 1:
        return _format_sales_invoice(doc)

    doc.flags.ignore_permissions = True
    doc.submit()
    frappe.db.commit()
    return _format_sales_invoice(frappe.get_doc("Sales Invoice", name))


def _format_sales_invoice(doc):
    """Return a clean, portal-safe representation of a Sales Invoice."""
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
            "charge_type": t.charge_type,
            "account_head": t.account_head,
            "description": t.description,
            "tax_amount": t.tax_amount,
        })

    payments = []
    if hasattr(doc, "payments"):
        for p in doc.payments:
            payments.append({
                "mode_of_payment": p.mode_of_payment,
                "amount": p.amount,
            })

    return {
        "name": doc.name,
        "customer": doc.customer,
        "customer_name": doc.customer_name,
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
        "outstanding_amount": doc.outstanding_amount,
        "paid_amount": max(0, (doc.grand_total or 0) - (doc.outstanding_amount or 0)),
        "items": items,
        "taxes": taxes,
        "payments": payments,
    }
