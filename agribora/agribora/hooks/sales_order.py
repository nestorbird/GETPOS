import frappe
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice

def on_submit(doc, method):
    create_sales_invoice_from_sales_order(doc)

def validate(doc, method):
    set_warehouse(doc)

def create_sales_invoice_from_sales_order(doc):
    sales_invoice = make_sales_invoice(doc.name)
    sales_invoice.posting_date = doc.transaction_date
    sales_invoice.due_date = doc.transaction_date
    sales_invoice.update_stock = 1
    sales_invoice.save()
    sales_invoice.submit()
    frappe.db.commit()

def set_warehouse(doc):
    if not doc.set_warehouse:
        doc.set_warehouse = frappe.db.get_value('Warehouse', {'hub_manager': doc.hub_manager}, 'name')
        for item in doc.items:
            item.warehouse = doc.set_warehouse

