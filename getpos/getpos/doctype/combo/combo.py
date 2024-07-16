# Copyright (c) 2024, Nestorbird and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Combo(Document):
	def after_insert(doc, method=None):
		selected_count = sum(1 for item in doc.combo_item)
		doc.count = selected_count
	def validate(doc, method=None):
		if doc.count is None:
			doc.count = 0
		selected_count = sum(1 for item in doc.combo_item)
		if int(doc.count)>int(selected_count):
				frappe.throw("Count can't be greater than Combo Items")
		if doc.mandatory==1 and int(doc.count)<1:
			doc.count=1
			