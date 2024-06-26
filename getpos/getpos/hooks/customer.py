import frappe
from frappe import _
from frappe.model.naming import make_autoname


@frappe.whitelist(allow_guest=True)
def get_customer_by_ward(ward):
    assigned_customer_list = []
    customer_list=frappe.db.sql(""" 
		SELECT 
			name
		FROM `tabCustomer` 
        WHERE ward =%s and disabled = 0""",(ward),as_dict = 1)
    for item in customer_list:
        assigned_customer_list.append(item.name)
    return assigned_customer_list







