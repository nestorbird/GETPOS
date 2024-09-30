
__version__ = '0.0.1'

from frappe.core.doctype.user.user import User


from getpos.overrides.verification import custom_send_login_mail

User.send_login_mail=custom_send_login_mail
