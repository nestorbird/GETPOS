import frappe


def main():
    customize_website_settings()


def customize_website_settings():
    settings = frappe.get_doc("Website Settings")
    settings.footer_powered = "Powered by NestorBird"
    settings.copyright = " "
    settings.disable_signup = 1
    settings.hide_footer_signup = 1
    settings.save()