import frappe

def update_theme_settings(doc,method=None):
    default_currency =doc.default_currency
    theme_settings =frappe.get_doc("Theme Settings")
    theme_settings.default_currency =default_currency
    theme_settings.save()
