import frappe
from frappe import _


def validate_hub_manager(doc, method):
    warehouse = frappe.get_value('Warehouse', {'hub_manager': doc.hub_manager}, 'name')
    if warehouse:
        frappe.throw(_("Already been used in some another warehouse."))
