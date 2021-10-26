import frappe

def set_hub_manager(doc,method):
    for item in doc.items:
        # for source warehouse
        source_warehouse = frappe.get_doc('Warehouse',item.s_warehouse)
        print(source_warehouse.hub_manager)
        source_warehouse.hub_manager = ""
        source_warehouse.save()
       # for target warehouse
        target_warehouse = frappe.get_doc('Warehouse', item.t_warehouse)
        target_warehouse.hub_manager = item.hub_manager
        target_warehouse.save()
