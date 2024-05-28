import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def validate_item_price(doc,method):
    if doc.price_list_rate<=0:
        frappe.throw(_("Rate can not be Zero or Negative"))


@frappe.whitelist()
def get_item_price(item_code):
    price_list_rate = frappe.db.get_value('Item Price', {'item_code': item_code}, 'price_list_rate')
    if price_list_rate is not None:
        return {'price_list_rate': price_list_rate}
    else:
        return {'price_list_rate': 0}
