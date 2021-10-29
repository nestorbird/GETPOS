import frappe
from frappe.model.naming import make_autoname


def autoname(doc,method):
    f_name, l_name = frappe.db.get_value('User', {'email': doc.hub_manager}, ['first_name', 'last_name'])
    doc.name = make_autoname(f_name[0] + l_name[0]  + "-.YYYY." + "-.MM." + "-." + "####")