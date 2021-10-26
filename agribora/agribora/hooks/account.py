import frappe

def set_account_hub_manager(doc,method):
    print(doc.name)
    print("--------------------------------------------")
    if doc.hub_manager:
        Hub_manager = frappe.get_doc('Hub Manager', doc.hub_manager)
        print(Hub_manager)
        print(Hub_manager.account)
        print("--------------------------------------------")
        Hub_manager.account = doc.name
        Hub_manager.save()
        print("---------------------Success-----------------------")
#     elif doc.hub_manager == "":
#         Hub_manager = frappe.get_doc({
#     'doctype': 'Hub Manager',
#     'account': 'doc.name'
# })
#         print("--------------------------------------------")
#         print(Hub_manager)
#         print("--------------------------------------------")
#         Hub_manager.account = ""
#         Hub_manager.save()