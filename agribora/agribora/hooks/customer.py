import frappe

def validate(doc,method):
    if not doc.hub_manager:
        hub_manager = frappe.db.get_value('Ward Detail', 
                        {
                            'ward': doc.ward, 
                            'is_assigned': 1,
                            'parenttype': 'Hub Manager'
                        }, 
                        ['parent'])
        doc.hub_manager = hub_manager

