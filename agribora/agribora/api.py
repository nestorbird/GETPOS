import frappe

@frappe.whitelist(allow_guest=True)
def get_abbr(string):
    abbr = ''.join(c[0] for c in string.split()).upper()
    return abbr