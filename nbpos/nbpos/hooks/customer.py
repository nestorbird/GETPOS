import frappe
from frappe.model.naming import make_autoname

def validate(doc,method):
    if not doc.hub_manager:
        hub_manager = frappe.db.get_value('Ward Detail', 
                        {
                            'ward': doc.ward, 
                            'is_assigned': 1,
                            'parenttype': 'Hub Manager'
                        }, 
                        ['parent'])
        doc.hub_manager = hub_manager

def validate(doc,method):
        doc.name = make_autoname("CUST"+"-.YYYY." +"-.###")


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



