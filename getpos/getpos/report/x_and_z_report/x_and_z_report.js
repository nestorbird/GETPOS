// Copyright (c) 2024, Nestorbird and contributors
// For license information, please see license.txt

frappe.query_reports["X and Z Report"] = {
	"filters": [
		{
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.month_start()
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.month_end()
        },
        {
            "fieldname": "pos_profile",
            "label": __("POS Profile"),
            "fieldtype": "Link",
            "options": "POS Profile"
        }
	]
};
