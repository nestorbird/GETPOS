import frappe

def frappe_response(http_status_code, message):
    frappe.local.response["http_status_code"] = http_status_code
    return message



def handle_exception(e):
    frappe.clear_messages()
    frappe.log_error(f"Error: {e}")
    return frappe_response(500, f"Error: {e}")