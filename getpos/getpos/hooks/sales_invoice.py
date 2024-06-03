import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

def on_submit(doc, method):
    create_payment_entry(doc)

def create_payment_entry(doc):
    payment_entry = get_payment_entry("Sales Invoice", doc.name)
    payment_entry.posting_date = doc.posting_date
    payment_entry.mode_of_payment = doc.mode_of_payment
    if doc.mode_of_payment == 'Cash':
        account = frappe.db.get_value('Account', 
                    {
                        'disabled': 0,
                        'account_type': 'Cash',
                        'account_name': 'Cash'
                    },
                    'name')
        payment_entry.paid_to = account
    if doc.mode_of_payment == 'M-Pesa':
        payment_entry.reference_no = doc.mpesa_no
        payment_entry.reference_date = doc.posting_date
    payment_entry.save()
    payment_entry.submit()
