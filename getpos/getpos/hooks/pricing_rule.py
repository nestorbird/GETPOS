import frappe
from frappe import _

@frappe.whitelist()
def coupon_code_email(pricing_rule, coupon_code_based, customer, discount_rate, discount_amount, discount_percentage):
    
    coupon_code_data = frappe.db.sql("""
                    SELECT coupon_code, valid_from, valid_upto, maximum_use, used
                    FROM `tabCoupon Code`
                    WHERE pricing_rule = %s
                        """, (pricing_rule),as_dict=True)
    parent = frappe.get_value("Dynamic Link", {"link_name": customer, "parenttype": "Contact"},"parent")
    if parent is None:
        return  frappe.throw("No Email Found For Customer = {}".format(customer))
    else:
        user_email_list = frappe.db.get_all("Contact Email", {"parent": parent, "parenttype" : "Contact"},"email_id")
    default_email_id = frappe.get_value("Email Account", {"default_outgoing": 1}, "email_id")

    if default_email_id:
        sent_emails = []
        for user_email in user_email_list:
            if (user_email["email_id"]):
                email_template = frappe.get_value("Email Template",{"custom_default_coupon_code_notification": 1 }, ["subject", "response"])
                context=dict(
                        code = coupon_code_data[0]
                            )  
                if (email_template):
                    subject=frappe.render_template(email_template[0], context)
                    message=frappe.render_template(email_template[1], context)
                else:
                    subject= _("You Got Coupon Code")
                    code = []
                    for i in coupon_code_data:
                        code.append = i["coupon_code"]
                    message= _("Here is your Coupon Code Details  :  ",code) 


                if (default_email_id):
                    frappe.sendmail(
                        recipients= user_email["email_id"],
                        subject=subject,
                        message=message,
                        now=True,
                         )

                    communication = frappe.get_doc({
                        "doctype": "Communication",
                        "communication_medium": "Email",
                        "sender": default_email_id,
                        "recipients": user_email["email_id"],
                        "subject": subject,
                        "content": message,
                        "reference_doctype": "Pricing Rule",
                        "reference_name": pricing_rule,
                        "sent_or_received": "Sent"
                    })
                    communication.insert(ignore_permissions=True)
                    sent_emails.append(user_email['email_id'])

            else:
                frappe.throw("No Email Found For Customer = {}".format(customer))
        return sent_emails
    else:
        frappe.throw("No Default Outgoing Email Account Found")

@frappe.whitelist()
def default_coupon_code_email_template(doc):
    frappe.db.sql("""
        UPDATE `tabEmail Template`              
        SET custom_default_coupon_code_notification = CASE
            WHEN name = %s THEN 1
            ELSE 0
            END;   
        """, (doc))