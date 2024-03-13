# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.model.document import Document
class POSClosingList(Document):
    def validate(self):
        if frappe.db.get_value("POS Opening List", self.pos_opening_entry, "status") != "Open":
            frappe.throw(_("Selected POS Opening Entry should be open."), title=_("Invalid Opening Entry"))
        self.validate_duplicate_sales_invoices()
       
    def on_submit(self):
        frappe.get_doc("POS Opening List", self.pos_opening_entry)
        frappe.db.set_value("POS Opening List", self.pos_opening_entry, "status", "Closed")
        frappe.db.set_value("POS Opening List",self.pos_opening_entry,"period_end_date",self.period_end_date)
    
    def validate_duplicate_sales_invoices(self):
        pos_occurences = {}
        for idx, inv in enumerate(self.pos_transactions, 1):
            pos_occurences.setdefault(inv.pos_invoice, []).append(idx)

        error_list = []
        for key, value in pos_occurences.items():
            
            if len(value) > 1:
                error_list.append(
                    _("{} is added multiple times on rows: {}".format(frappe.bold(key), frappe.bold(value)))
                )
                print("Duplicate POS Invoice {} found on rows: {}".format(key, value))

        if error_list:
            frappe.throw(error_list, title=_("Duplicate POS Invoices found"), as_list=True)
   
   
@frappe.whitelist()
def get_sales_invoices(start, end, pos_profile,user,pos_opening_entry):
    
    sales_invoices = frappe.get_all(
        "Sales Invoice",
        filters={
            "docstatus": 1,
            "pos_profile":pos_profile,
            "status":'paid',
            'is_pos':1,
            "custom_pos_opening_entry": pos_opening_entry,
            "posting_date": (">=", start),
            "posting_date": ("<=", end)  
        },
        fields=["name", "posting_date", "posting_time", "grand_total","net_total", "customer", "total_qty","customer_name", "is_return", "return_against"]
    )
    return sales_invoices
@frappe.whitelist()
def get_tax_data(pos_opening_entry):
    tax_data = frappe.db.sql("""
        SELECT si.custom_pos_opening_entry, stc.account_head, stc.rate, stc.tax_amount 
        FROM `tabSales Invoice` si 
        INNER JOIN `tabSales Taxes and Charges` stc 
        ON si.name = stc.parent  
        WHERE si.custom_pos_opening_entry = %s
    """, pos_opening_entry, as_dict=True)
    return tax_data


