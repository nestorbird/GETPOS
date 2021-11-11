import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def validate_item_price(doc,method):
    if doc.price_list_rate<=0:
        frappe.throw(_("Rate can not be Zero or Negative"))