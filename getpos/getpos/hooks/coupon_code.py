import frappe
from frappe.utils.pdf import get_pdf

def validate(doc,method):
    if doc.coupon_type=='Gift Card':
                
        customer = frappe.get_doc("Customer", doc.customer)
        contact_doc = frappe.get_doc("Contact", customer.customer_primary_contact)
        recipient = contact_doc.email_id

        # Check if the recipient email is present
        if recipient:
            subject = "Your Gift Card: {}".format(doc.name)
            message = "Dear {},\n\nPlease find attached your Gift Card: {}.\n\nBest regards,\nYour Company Name".format(customer.customer_name, doc.coupon_code)
            pdf_content = get_coupon_code_pdf(doc)
            attachment = {
                "fname": "Gift_Card_{}.pdf".format(doc.name.replace(" ", "_")),
                "fcontent": pdf_content
            }
            try:
                # Send the email
                frappe.sendmail(
                    recipients=[recipient],
                    subject=subject,
                    message=message,
                    attachments=[attachment],
                    now=True
                )
            except Exception as e:
                frappe.local.response["message"] = {
                    "success_key": 0,
                    "message": str(e)
                }
        else:
            frappe.throw("The customer does not have a primary contact email.")

def get_coupon_code_pdf(doc):
    html = frappe.render_template('getpos/templates/pages/gift_card_template.html', context={'doc': doc})
    pdf_content = get_pdf(html)
    return pdf_content