import frappe
from frappe.utils import today,getdate


def get_price_list(item_code):
    all_item_price = frappe.get_list('Item Price',filters={'item_code':item_code,'selling':1,'price_list':'Standard Selling',
                                    'valid_from':['<=',today()]},fields=['price_list_rate','valid_upto'],order_by='modified desc')
    if all_item_price:
                    for item_price in all_item_price:
                        if not item_price.valid_upto:
                            return item_price.price_list_rate

                        elif (item_price.valid_upto).strftime('%Y-%m-%d') >= today():
                            return item_price.price_list_rate
    return 

@frappe.whitelist()
def get_items():
    data = []
    all_groups = frappe.get_list('Item Group',filters={'is_group':0,'name':['not in',('Extra')]},fields=['name'])
    for group in all_groups:
        group_dict = {}
        all_extra_items = frappe.get_list('Item Group Multiselect',filters={'item_group':group.name},fields=['parent'])
        attributes = []
        if all_extra_items:
            for extra_item in all_extra_items:
                extra_item_price = get_price_list(extra_item.parent)
                attributes.append({'id':extra_item.parent,'name':frappe.db.get_value('Item',extra_item.parent,'item_name'),\
                                    'price':extra_item_price if extra_item_price else ''})
        all_items = frappe.get_list('Item',filters={'item_group':group.name,'disabled':0},fields=['*'])
        if all_items:
            group_dict.update({'item_group':group.name,'items':[]}) 
            for item in all_items:
                item_dict = {'id':item.name,'name':item.item_name,'attributes':attributes}
                item_price = get_price_list(item.name)
                if item_price:
                    item_dict.update({'product_price':item_price})
                
                group_dict.get('items').append(item_dict)
            data.append(group_dict)
    return data
        