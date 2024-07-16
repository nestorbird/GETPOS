import frappe


def execute():
    frappe.db.sql("""delete from `tabCustom Field` where name = 'Item-custom_fetch_cost_center' 
                    and dt='Item' and fieldname='custom_fetch_cost_center' """)
    
    frappe.db.sql("""delete from `tabCustom Field` where name = 'Item-custom_cost_center_details' 
                    and dt='Item' and fieldname='custom_cost_center_details' """)
    
    frappe.db.sql("""delete from `tabCustom Field` where name = 'Item Tax Template Detail-custom_tax_percentage' 
                    and dt='Item Tax Template Detail' and fieldname='custom_tax_percentage' """)
    
    frappe.db.sql("""delete from `tabCustom Field` where name = 'Item-custom_section_break_6cf4b' 
                    and dt='Item' and fieldname='custom_section_break_6cf4b' """)
    
    frappe.db.sql("""delete from `tabCustom Field` where name = 'Item-custom_related_items' 
                    and dt='Item' and fieldname='custom_related_items' """)