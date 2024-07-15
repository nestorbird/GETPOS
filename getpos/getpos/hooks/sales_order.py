import frappe
from frappe.model.naming import make_autoname
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
from erpnext.controllers.accounts_controller import get_taxes_and_charges
from frappe.utils.pdf import get_pdf
from frappe.core.doctype.communication.email import make

def on_submit(doc, method):
    create_sales_invoice_from_sales_order(doc)

def validate(doc, method):
    set_warehouse(doc)
    # if doc.is_new():
    #     hub_manager_series = frappe.db.get_value('Hub Manager', doc.hub_manager, 'series')
    #     doc.name = make_autoname(hub_manager_series)


def create_sales_invoice_from_sales_order(doc):
    if (doc.custom_source == "WEB"):
        pass
    else:
        sales_invoice = make_sales_invoice(doc.name)
        sales_invoice.posting_date = doc.transaction_date
        sales_invoice.posting_time = doc.transaction_time
        sales_invoice.due_date = doc.transaction_date        
        sales_invoice.update_stock = 1
        if doc.custom_redeem_loyalty_points:
            sales_invoice.redeem_loyalty_points = doc.custom_redeem_loyalty_points
            sales_invoice.loyalty_points = doc.loyalty_points
            sales_invoice.loyalty_amount = doc.loyalty_amount
            sales_invoice.loyalty_program = doc.custom_loyalty_program
            sales_invoice.loyalty_redemption_account = doc.custom_redemption_account
        if doc.coupon_code:
            sales_invoice.coupon_code=doc.coupon_code
        if doc.custom_gift_card_code:
            sales_invoice.discount_amount=doc.discount_amount
            sales_invoice.apply_discount_on="Grand Total"
        sales_invoice.save(ignore_permissions=1)
        sales_invoice.submit()
        send_sales_invoice_email(sales_invoice.name)

def set_warehouse(doc):
    if not doc.set_warehouse:
        doc.set_warehouse = frappe.db.get_value('Warehouse', {'warehouse_name': 'Stores'}, 'name')
        for item in doc.items:
            item.warehouse = doc.set_warehouse


@frappe.whitelist()
def send_sales_invoice_email(sales_invoice_name):
    sales_invoice = frappe.get_doc("Sales Invoice", sales_invoice_name)    
    recipient = sales_invoice.contact_email
    # Check if the recipient email is present
    if recipient:        
        # Generate PDF content
        pdf_content = get_sales_invoice_pdf(sales_invoice_name)
        # Prepare the email content
        email_subject = f"Sales Invoice {sales_invoice_name}"
        email_message = f"Dear {sales_invoice.customer_name},\n\nPlease find attached your sales invoice.\n\nBest regards,\nYour Company Name"
        # Create an attachment
        attachment = {
                'fname': f"{sales_invoice_name}.pdf",
                'fcontent': pdf_content
        }
        try:
            # Send the email
              make(
                    recipients=[recipient],
                    subject=email_subject,
                    content=email_message,
                    attachments=[attachment],
                    send_email=True
            )
        except Exception as e:
             frappe.local.response["message"] = {
            "success_key": 0,
            "message": str(e)
        }


def get_sales_invoice_pdf(sales_invoice_name):
    sales_invoice = frappe.get_doc("Sales Invoice", sales_invoice_name)
    html = frappe.render_template('getpos/templates/pages/sales_invoice_email.html', context={'doc': sales_invoice})
    pdf_content = get_pdf(html)
    return pdf_content

