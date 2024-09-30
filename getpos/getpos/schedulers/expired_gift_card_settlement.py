import frappe
from frappe.utils import add_days, nowdate, getdate
def create_gift_card_journal_entries():
    company_name = frappe.get_doc("Global Defaults").default_company
    company = frappe.get_doc("Company", company_name)
    previous_date = add_days(nowdate(), -1)
    expired_gift_cards = frappe.get_all("Gift Card",
                                        filters={
                                            'valid_upto': previous_date,
                                            'amount_balance': ['>', 0],
                                            'is_journal_entry': 0
                                        },
                                        fields=['name', 'amount_balance'])
    for card in expired_gift_cards:
        journal_entry = frappe.new_doc("Journal Entry")
        journal_entry.voucher_type = "Journal Entry"
        journal_entry.company = company.name
        journal_entry.posting_date = getdate()
        journal_entry.user_remark = (
            f"{card.amount_balance} $ gift card value remains unused and also surpasses the "
                "validity date of the gift card. Hence, gift card remaining value will be "
                "transferred to sales account to decrease the liability."
        )
        journal_entry.append(
            "accounts",
            {
                'account': "Gift card Revenue - " + company.abbr,
                'debit_in_account_currency': float(card.amount_balance),
                'credit_in_account_currency': 0.0
            }
        )
        journal_entry.append(
            "accounts",
            {
                'account': "Sales - " + company.abbr,
                'debit_in_account_currency': 0.0,
                'credit_in_account_currency': float(card.amount_balance)
            }
        )
        journal_entry.save(ignore_permissions=True)
        journal_entry.submit()
        frappe.db.set_value("Gift Card", card.name, "is_journal_entry", 1)
    frappe.db.commit()
