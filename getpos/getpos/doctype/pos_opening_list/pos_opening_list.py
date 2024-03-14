import frappe
from frappe import _
from frappe.utils import cint, get_link_to_form
from frappe.model.document import Document

class POSOpeningList(Document):
    def validate(self):
        self.validate_pos_profile_and_cashier()
        self.validate_payment_method_account()

    def on_submit(self):
        frappe.db.set_value("POS Opening List", self.name, "status", "Open")

    def validate_pos_profile_and_cashier(self):
        if self.company != frappe.db.get_value("POS Profile", self.pos_profile, "company"):
            frappe.throw(
                _("POS Profile {} does not belong to company {}").format(self.pos_profile, self.company)
            )

        if not cint(frappe.db.get_value("User", self.user, "enabled")):
            frappe.throw(_("User {} is disabled. Please select a valid user/cashier").format(self.user))

    def validate_payment_method_account(self):
        invalid_modes = []
        for d in self.balance_details:
            if d.mode_of_payment:
                account = frappe.db.get_value(
                    "Mode of Payment Account",
                    {"parent": d.mode_of_payment, "company": self.company},
                    "default_account",
                )
                if not account:
                    invalid_modes.append(get_link_to_form("Mode of Payment", d.mode_of_payment))

        if invalid_modes:
            if len(invalid_modes) == 1:
                msg = _("Please set a default Cash or Bank account in Mode of Payment {}")
            else:
                msg = _("Please set default Cash or Bank accounts in Mode of Payments {}")
            frappe.throw(msg.format(", ".join(invalid_modes)), title=_("Missing Account"))
