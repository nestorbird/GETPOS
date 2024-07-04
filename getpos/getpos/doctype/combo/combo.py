# Copyright (c) 2024, Nestorbird and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class Combo(Document):
	def validate(doc, method=None):
		"""
		Validate the document to count the number of selected attribute items.

		Args:
		doc (Document): The document containing attribute items.
		method (str, optional): The method being validated. Defaults to None.

		Sets:
		doc.count (int): The count of attribute items where 'select' is 1.
		"""
		# Count the number of selected attribute items
		selected_count = sum(1 for item in doc.combo_item if item.select == 1)
		
		# Assign the count to the document's 'count' field
		doc.count = selected_count