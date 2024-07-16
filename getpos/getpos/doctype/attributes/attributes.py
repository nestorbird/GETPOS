# Copyright (c) 2024, Nestorbird and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Attributes(Document):
	def after_insert(doc, method=None):
		selected_count = sum(1 for item in doc.attribute_items)
		doc.count = selected_count
  
	def validate(doc, method=None):
		if doc.count is None:
			doc.count = 0
		selected_count = sum(1 for item in doc.attribute_items)
		if int(doc.count)>int(selected_count):
			frappe.throw("Count can't be greater than Attribute Items")
		if doc.mandatory==1 and int(doc.count)<1:
			doc.count=1