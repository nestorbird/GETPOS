# Copyright (c) 2024, Nestorbird and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import nowdate

def execute(filters=None):
    columns, data = [], []

    columns = [
        {"label": "POS Profile", "fieldname": "pos_profile", "fieldtype": "Data", "width": 180},
        {"label": "Old Customers", "fieldname": "old_customers", "fieldtype": "Int", "width": 150},
        {"label": "New Customers", "fieldname": "new_customers", "fieldtype": "Int", "width": 150},
        {"label": "Sales Order Transactions", "fieldname": "sales_order_transactions", "fieldtype": "Int", "width": 180},
        {"label": "Return Order Transactions", "fieldname": "return_order_transactions", "fieldtype": "Int", "width": 180},
        {"label": "Sales Order Amount", "fieldname": "sales_order_amount", "fieldtype": "Currency", "width": 150},
        {"label": "Return Order Amount", "fieldname": "return_order_amount", "fieldtype": "Currency", "width": 150},
        {"label": "No. of Transactions", "fieldname": "no_of_transactions", "fieldtype": "Int", "width": 150},
        {"label": "Cash Collected", "fieldname": "cash_collected", "fieldtype": "Currency", "width": 150},
        {"label": "Credit Collected", "fieldname": "credit_collected", "fieldtype": "Currency", "width": 150},
        {"label": "Total Sales Order Amount", "fieldname": "total_sales_order_amount", "fieldtype": "Currency", "width": 180}
    ]

    pos_profile_filter = ""
    query_params = {
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date")
    }

    if filters.get("pos_profile"):
        pos_profile_filter = "AND pos.pos_profile = %(pos_profile)s"
        query_params["pos_profile"] = filters.get("pos_profile")

    # Subquery to get customer counts by POS profile, checking their creation dates
    customer_counts_query = f"""
        SELECT 
            pos.pos_profile,
            COUNT(DISTINCT CASE WHEN c.creation < %(from_date)s THEN c.name ELSE NULL END) AS old_customers,
            COUNT(DISTINCT CASE WHEN c.creation BETWEEN %(from_date)s AND %(to_date)s THEN c.name ELSE NULL END) AS new_customers
        FROM 
            `tabPOS Opening Shift` pos
            LEFT JOIN `tabCustomer` c ON pos.name = c.custom_pos_shift
        WHERE 
            c.creation BETWEEN %(from_date)s AND %(to_date)s
            {pos_profile_filter}
        GROUP BY 
            pos.pos_profile
    """
    customer_counts = frappe.db.sql(customer_counts_query, query_params, as_dict=True)
    customer_counts_dict = {row.pos_profile: row for row in customer_counts}

    query = f"""
        SELECT 
            pos.pos_profile,
            COUNT(DISTINCT CASE WHEN si.is_return = 0 THEN si.name END) AS sales_order_transactions,
            COUNT(DISTINCT CASE WHEN si.is_return = 1 THEN si.name END) AS return_order_transactions,
            SUM(CASE WHEN si.is_return = 0 THEN sii.base_net_amount ELSE 0 END) AS sales_order_amount,
            SUM(CASE WHEN si.is_return = 1 THEN sii.base_net_amount ELSE 0 END) AS return_order_amount,
            COUNT(DISTINCT si.name) AS no_of_transactions,
            SUM(CASE WHEN si.is_return = 0 and si.mode_of_payment="Cash" THEN si.base_net_total ELSE 0 END) + SUM(CASE WHEN si.is_return = 1 and si.mode_of_payment="Cash" THEN si.base_net_total ELSE 0 END) AS cash_collected,
            SUM(CASE WHEN si.is_return = 0 and si.mode_of_payment="Credit" THEN si.base_net_total ELSE 0 END) + SUM(CASE WHEN si.is_return = 1 and si.mode_of_payment="Credit" THEN si.base_net_total ELSE 0 END) AS credit_collected,
            SUM(CASE WHEN si.is_return = 0 THEN si.base_net_total ELSE 0 END) + SUM(CASE WHEN si.is_return = 1 THEN si.base_net_total ELSE 0 END) AS total_sales_order_amount
        FROM 
            `tabPOS Opening Shift` pos
            LEFT JOIN `tabSales Order` so ON pos.name = so.custom_pos_shift
            LEFT JOIN `tabSales Invoice Item` sii ON sii.sales_order = so.name
            LEFT JOIN `tabSales Invoice` si ON si.name = sii.parent
            LEFT JOIN `tabSales Invoice Payment` sip ON si.name = sip.parent
            LEFT JOIN `tabPOS Opening Shift Detail` posd ON pos.name = posd.parent
        WHERE
            si.posting_date BETWEEN %(from_date)s AND %(to_date)s
            {pos_profile_filter}
        GROUP BY 
            pos.pos_profile
    """
    result = frappe.db.sql(query, query_params, as_dict=True)

    for row in result:
        row.old_customers = customer_counts_dict.get(row.pos_profile, {}).get('old_customers', 0)
        row.new_customers = customer_counts_dict.get(row.pos_profile, {}).get('new_customers', 0)
        data.append(row)

    return columns, data
