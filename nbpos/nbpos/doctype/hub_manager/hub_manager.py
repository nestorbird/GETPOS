# Copyright (c) 2022, swapnil and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cstr


class HubManager(Document):
	def validate(self):
		self.set_naming_series()

	def on_update(self):
		self.add_hub_manager_to_customer()
		self.remove_hub_manager_from_customer()


	def set_naming_series(self):
		if not self.series:
			first_name, last_name = frappe.db.get_value('User', self.hub_manager, ['first_name', 'last_name'])
			if not last_name:
				abbr = first_name[0].upper()
			else:
				abbr = first_name[0].upper() + last_name[0].upper()
			hub_manager_list = frappe.db.get_list('Hub Manager',
					filters={
						'series': ['like', abbr + '%']
					},
					fields=['name'])
			if hub_manager_list:
				self.series = abbr + '-' + cstr(len(hub_manager_list)) + "-.YYYY." + "-.MM." + "-." + "#"
			else:
				self.series = abbr + "-.YYYY." + "-.MM." + "-." + "#"
				

	def add_hub_manager_to_customer(self):
		for item in self.wards:
			if item.is_assigned == 1:
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
			if item.is_assigned == 1:
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
def get_hub_manager(ward):
	hub_manager = frappe.db.get_value('Ward Detail', 
					{
						'ward': ward,
						'is_assigned': 1,
						'parenttype': 'Hub Manager'},
					['parent'])
	return hub_manager

@frappe.whitelist(allow_guest=True)
def get_hub_manager_list():
	hub_managers = []
	hub_manager_list=frappe.db.sql(""" 
		SELECT 
			name
		FROM `tabHub Manager`""",as_dict = 1)
	for item in hub_manager_list:
		hub_managers.append(item.name)
	return hub_managers