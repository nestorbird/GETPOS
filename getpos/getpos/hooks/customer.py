import frappe
from frappe import _
from frappe.model.naming import make_autoname
from erpnext.selling.doctype.customer.customer import get_customer_outstanding

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
        if not doc.hub_manager:
            hub_manager = frappe.db.get_value('Ward Detail', 
                            {
                                'ward': doc.ward, 
                                'is_assigned': 1,
                                'parenttype': 'Hub Manager'
                            }, 
                            ['parent'])
        doc.hub_manager = hub_manager
        existing_customer = frappe.db.get_value("Customer", {"mobile_no": doc.mobile_no})        
        if existing_customer and doc.mobile_no is not None and doc.name != existing_customer:
            frappe.throw(_("Customer With Mobile Number {0} Already Exists").format(frappe.bold(doc.mobile_no)))
        if existing_customer:
             outstanding_amount =  get_customer_outstanding(
			        existing_customer, frappe.get_doc("Global Defaults").default_company, ignore_outstanding_sales_order=False
		        )
             if doc.custom_credit_limit >0 and doc.custom_credit_limit < outstanding_amount:
                    frappe.throw(
                        _(
                            """New credit limit is less than current outstanding amount for the customer. Credit limit has to be atleast {0}"""
                        ).format(outstanding_amount)
                    )



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

