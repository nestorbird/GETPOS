import frappe

def create_warehouse(self, method=None):
    new_warehouse = frappe.new_doc("Warehouse")
    new_warehouse.warehouse_name = self.cost_center_name
    new_warehouse.custom_cost_center = self.name
    new_warehouse.insert()