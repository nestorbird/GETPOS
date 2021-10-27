# Copyright (c) 2021, www.nestorbird.com and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class HubManager(Document):
	def autoname(self):
		full_name = frappe.db.sql("""SELECT full_name FROM tabUser WHERE email = %s""",(self.hub_manager),as_dict=True)
		self.name = make_autoname(full_name + "-.DD." + "-.MM." + "-.YYYY." + "####")
	def on_update(self):
		self.add_hub_manager_to_customer()
		self.remove_hub_manager_from_customer()

	def add_hub_manager_to_customer(self):
		for item in self.wards:
			customer_list = frappe.get_list('Customer', {
				'ward': item.ward, 
				'hub_manager': ["!=", self.hub_manager],
				'disabled': 0, 
				},
				['name'])
			if customer_list:
				for customer in customer_list:
					doc = frappe.get_doc('Customer', customer.name)
					doc.hub_manager = self.hub_manager
					doc.save()

	def remove_hub_manager_from_customer(self):
		ward_list = []
		for item in self.wards:
			ward_list.append(item.ward)
		customer_list = frappe.get_list('Customer', {
			'ward': ["not in", ward_list],
			'hub_manager': self.hub_manager,
			'disabled': 0
			},
			["name"])
		if customer_list:
			for customer in customer_list:
				doc = frappe.get_doc('Customer', customer.name)
				doc.hub_manager = ''
				doc.save()

@frappe.whitelist(allow_guest=True)
def get_assigned_hub_manager():
	assigned_hub_manager = []
	hub_manager_list = frappe.db.sql("""SELECT hub_manager
		FROM `tabAccount`
		""",as_dict = 1)
	print("---------------------------")
	print(type(hub_manager_list))
	for items in hub_manager_list:
		print("---------------------------")
		print(items.hub_manager)
		assigned_hub_manager.append(items.hub_manager)
	return assigned_hub_manager