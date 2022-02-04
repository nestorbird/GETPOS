# Copyright (c) 2022, swapnil and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Ward(Document):
	pass

@frappe.whitelist(allow_guest=True)
def get_assigned_ward():
	assigned_ward_list = []
	ward_list=frappe.db.sql(""" 
		SELECT 
			distinct(ward)
		FROM `tabWard Detail`
		WHERE parenttype = 'Hub Manager'""",as_dict = 1)
	for item in ward_list:
		assigned_ward_list.append(item.ward)
	return assigned_ward_list

@frappe.whitelist(allow_guest=True)
def get_ward_by_hub_manager(hub_manager):
	assigned_ward_list = []
	ward_list=frappe.db.sql(""" 
		SELECT 
			distinct(ward)
		FROM `tabWard Detail` where parent =%s""",(hub_manager),as_dict = 1)
	for item in ward_list:
		assigned_ward_list.append(item.ward)
	return assigned_ward_list