import frappe
from frappe import _

def get_hub_manager(doc,method):
    hub_manager = frappe.get_value('Hub Manager',{'ward': doc.ward},'name')
    doc.hub_manager = hub_manager