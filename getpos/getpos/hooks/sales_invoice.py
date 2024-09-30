import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

def on_submit(doc, method):
    if doc.grand_total!=0:
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





def send_email_on_invoice(doc, method):
    # Get the Sales Order linked to this Sales Invoice
    if doc.items and doc.items[0].sales_order:
        sales_order = frappe.get_doc("Sales Order", doc.items[0].sales_order)
        # Check if custom_source == "WEB"
        if sales_order.custom_source == "WEB":
            customer = frappe.get_doc("Customer", sales_order.customer)
            customer_name = customer.customer_name
            cost_center=sales_order.cost_center

            restaurant_name = frappe.db.get_value("Cost Center", cost_center, "cost_center_name")
            restaurant_address = frappe.db.get_value("Cost Center", cost_center, "custom_address")

            email_content = format_email_content(sales_order, customer_name, restaurant_name, restaurant_address)
            send_email(customer.email_id, email_content, restaurant_name)

def format_email_content(sales_order, customer_name, restaurant_name, restaurant_address):
    items_detail = ""
    for item in sales_order.items:
        items_detail += "<br>"+f"{item.item_name} - Quantity: {item.qty} - Price: £{item.rate}\n"

    subtotal = sales_order.total
    vat = sales_order.total_taxes_and_charges
    total = sales_order.grand_total
    recipient = sales_order.customer
    email_id =frappe.db.get_value("Customer",recipient,"email_id")
    max_time = max(frappe.db.get_value("Item",item.item_code,"custom_estimated_time") for item in sales_order.items)
    email_template = f"""
    Dear {customer_name}, <br> <br>
    
    Thank you for your order! Here are your order details: <br><br>
    
    <b>Order ID</b>: {sales_order.name} <br>
    <b>Order Date</b>: {sales_order.transaction_date}<br>
    <b>Estimated Time </b>:{max_time} minutes <br>
    
    <b>Your Order</b>:
    {items_detail} <br> <br>
    
    <b>Order Request</b>:{sales_order.custom_order_request}<br>
    <b>Subtotal</b>: £{subtotal} <br>
    <b>VAT </b>: £{vat} <br>
    <b>Total Amount </b>: £{total} <br>
    
    <b>Restaurant Address</b>: {restaurant_address} <br>
    
    Thank you for choosing {restaurant_name}! <br><br>
    
    Best regards,<br>
    The {restaurant_name} Team <br><br>
    
    <b>Disclaimer</b>:
    Please note that email is auto generated and the inbox is unmonitored. For any cancellation requests or inquiries regarding your order, kindly contact the business directly.
    """
    return email_template

def send_email(email_id, email_template, restaurant_name):
    subject = f"Order Confirmation - {restaurant_name}"
    frappe.sendmail(
        recipients=email_id,
        subject=subject,
        message=email_template,
        now=True
    )
