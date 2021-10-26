# Copyright (c) 2021, www.nestorbird.com and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document

class HubManager(Document):
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