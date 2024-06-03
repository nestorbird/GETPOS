import frappe
from frappe import _
import re

def validate_item_description(doc, method):
    pattern = r'</?div>|</?p>'
    desc_data = doc.description
    cleaned_str = re.sub(pattern, '', desc_data)
    if len(cleaned_str)>20:
        frappe.throw("Description must be less than 20 characters")
