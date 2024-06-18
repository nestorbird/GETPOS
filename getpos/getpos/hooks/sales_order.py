import frappe
from frappe.model.naming import make_autoname
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
from erpnext.controllers.accounts_controller import get_taxes_and_charges


def on_submit(doc, method):
    create_sales_invoice_from_sales_order(doc)

def validate(doc, method):
    set_warehouse(doc)
    # if doc.is_new():
    #     hub_manager_series = frappe.db.get_value('Hub Manager', doc.hub_manager, 'series')
    #     doc.name = make_autoname(hub_manager_series)


def create_sales_invoice_from_sales_order(doc):
    if (doc.custom_source == "WEB"):
        pass
    else:
        sales_invoice = make_sales_invoice(doc.name)
        sales_invoice.posting_date = doc.transaction_date
        sales_invoice.posting_time = doc.transaction_time
        sales_invoice.due_date = doc.transaction_date        
        sales_invoice.update_stock = 1
        if doc.custom_redeem_loyalty_points:
            sales_invoice.redeem_loyalty_points = doc.custom_redeem_loyalty_points
            sales_invoice.loyalty_points = doc.loyalty_points
            sales_invoice.loyalty_amount = doc.loyalty_amount
            sales_invoice.loyalty_program = doc.custom_loyalty_program
            sales_invoice.loyalty_redemption_account = doc.custom_redemption_account
        sales_invoice.save(ignore_permissions=1)
        sales_invoice.submit()

def set_warehouse(doc):
    if not doc.set_warehouse:
        doc.set_warehouse = frappe.db.get_value('Warehouse', {'warehouse_name': 'Stores'}, 'name')
        for item in doc.items:
            item.warehouse = doc.set_warehouse
