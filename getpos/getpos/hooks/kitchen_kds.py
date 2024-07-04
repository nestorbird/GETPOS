import frappe

def send_order_ready_email(doc, method):
    if doc.status == "Completed":
        order = frappe.get_doc("Sales Order", doc.order_id)
        customer = frappe.get_doc("Customer", order.customer)
        cost_center =order.cost_center
        restaurant_name = frappe.db.get_value("Cost Center", cost_center, "cost_center_name")

        subject = "Your Order is Ready for Pickup"
        message = f"""
        Dear {customer.customer_name}, <br><br>
        
        Good news! Your order from {restaurant_name} is now cooked and ready for pickup. <br><br>
        
        <b>Order ID</b>: {order.name} <br> <br>
        
        We look forward to serving you. <br> <br>
        
        Thank you for choosing {restaurant_name}! <br><br><br>
        
        Best regards, <br> <br>
        The {restaurant_name} Team
        """
        
        frappe.sendmail(
            recipients=[customer.email_id],
            subject=subject,
            message=message,
            now=True
        )