import frappe, json
from getpos.custom_api.item_variant_api import get_items
from frappe.utils import now

def after_insert(doc, event=None):
    if doc.get('ref_doctype') in ['Item', 'Item Group','Item Tax Template','Item Price',
                                  'Stock Entry', 'Purchase Receipt', 'Delivery Note','Sales Invoice']:
        
        if doc.get('ref_doctype') == 'Item Group':
            check_item_group(doc)
        
        elif doc.get('ref_doctype') == 'Item':
            check_item(doc)

        elif doc.get('ref_doctype') == 'Item Price':
            check_price(doc)

        elif doc.get('ref_doctype') == 'Item Tax Template':
            check_item_tax_template(doc)

        else:
            check_stock_items(doc)


def check_stock_items(doc):
    doc = frappe.get_doc(doc.get('ref_doctype'), doc.get('docname'))
    if doc.items:
        for item in doc.items:
            check_item(doc={'ref_doctype':'Item', 'docname': item.item_code})


def check_item_tax_template(doc):
    doc = frappe.get_doc(doc.get('ref_doctype'), doc.get('docname'))
    item_data = frappe.db.sql(''' select parent from `tabItem Tax` where parenttype='Item' and item_tax_template= %(name)s group by parent''',{'name': doc.name},
                                    as_dict=1 )
    for item in item_data:
        check_item(doc={'ref_doctype':'Item', 'docname': item.parent})
    


def check_price(doc):
    doc = frappe.get_doc(doc.get('ref_doctype'), doc.get('docname'))
    item_group = frappe.get_cached_value('Item', doc.item_code, 'item_group')
    parent_item_group = frappe.get_cached_value('Item Group', item_group, fieldname="parent_item_group")
    if not parent_item_group == 'Extra':
        data = get_items(item_group = doc.get('item_group'), item_code=doc.item_code)
    else:
        data = get_items(extra_item_group = doc.get('item_group'), item_code=doc.item_code)

    # create_sync_reg_log(data)

        

def check_item(doc):
    doc = frappe.get_doc(doc.get('ref_doctype'), doc.get('docname'))
    parent_item_group = frappe.get_cached_value('Item Group', doc.get('item_group'), fieldname="parent_item_group")
    if not parent_item_group == 'Extra':
        data = get_items(item_group = doc.get('item_group'), item_code=doc.name)
    else:
        data = get_items(extra_item_group = doc.get('item_group'), item_code=doc.name)

    # create_sync_reg_log(data)          


def check_item_group(doc):
    doc = frappe.get_doc(doc.get('ref_doctype'), doc.get('docname'))
    
    if doc.get('parent_item_group') != 'Extra':
        data = get_items(item_group = doc.get('name'))
    else:
        data = get_items(extra_item_group = doc.get('name'))

    # create_sync_reg_log(data)


def create_sync_reg_log(data):
    frappe.get_doc({'doctype':'Sync Register','sync_datetime': now(), 'force_update': 1, 'data':json.dumps(data) }).insert(ignore_permissions=True)       