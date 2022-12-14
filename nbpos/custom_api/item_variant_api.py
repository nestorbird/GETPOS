import frappe
from frappe.utils import today,getdate,flt


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
    

def get_stock_qty(item):
    bin_list = frappe.get_list('Bin',filters={'item_code':item.item_code,'warehouse':['like','Stores%']},
                            fields=['actual_qty','warehouse'],order_by='actual_qty desc',limit_start=0,
                            limit_page_length=21)
    if bin_list:
        return {"warehouse":bin_list[0].warehouse,'stock_qty':bin_list[0].actual_qty}
            
    else:
        return {'warehouse': '','stock_qty':0}



@frappe.whitelist()
def get_items():
    data = []
    all_groups = frappe.get_list('Item Group',filters={'is_group':0,'name':['not in',('Extra')],
                                'parent_item_group':['not in',('Extra')]},
                                fields=['name'])
    for group in all_groups:
        group_dict = {}
        all_extra_items = frappe.get_list('Item Group Multiselect',filters={'item_group':group.name},fields=['parent'])
        attributes = []
        attributes_dict = {}
        product_price_addition = 0
        if all_extra_items:
            for extra_item in all_extra_items:
                extra_item_doc = frappe.get_doc('Item',extra_item.parent)
                extra_item_price = get_price_list(extra_item.parent)

                #Checking Stock
                extra_item_stock = ''
                if extra_item_doc.is_stock_item:
                    extra_item_stock = get_stock_qty(extra_item_doc)

                if not attributes_dict.get(extra_item_doc.item_group):
                    # Checking item group
                    moq, select_type = frappe.db.get_value('Item Group',extra_item_doc.item_group,['moq','select_type'])

                    attributes_dict.update({f'{extra_item_doc.item_group}':{'name':f'Choose {extra_item_doc.item_group}',
                                    'type': select_type,'moq':moq,
                                    'options': [{ 'id':  extra_item_doc.name, 'name':extra_item_doc.item_name,
                                    'price': extra_item_price if extra_item_price else '','selected':True,
                                    'warehouse':extra_item_stock.get('warehouse') if extra_item_stock else -1,
                                    'stock_qty':extra_item_stock.get('stock_qty') if extra_item_stock else -1}],
                                    }})
                    product_price_addition += flt(extra_item_price)
                else:
                    attributes_dict.get(extra_item_doc.item_group).get('options').append({'id': extra_item_doc.name,
                                        'name': extra_item_doc.item_name, 'selected': False, 
                                        'price':extra_item_price if extra_item_price else '',
                                        'warehouse':extra_item_stock.get('warehouse'),'stock_qty':extra_item_stock.get('stock_qty')
                                        })
                
        if attributes_dict:
            for x in attributes_dict.items():
                attributes.append(x[1])
                    
        
        #### Getting Items ####
        all_items = frappe.get_list('Item',filters={'item_group':group.name,'disabled':0},fields=['*'])
        if all_items:
            group_dict.update({'item_group':group.name,'items':[]}) 
            for item in all_items:
                image = get_image_from_item(item.name)
                item_dict = {'id':item.name,'name':item.item_name,'attributes':attributes, 'image': image}
                item_price = flt(get_price_list(item.name)) + product_price_addition
                if item_price:
                    item_dict.update({'product_price':item_price})
                
                # Checking Stock
                item_stock = {'warehouse':-1,'stock_qty':-1}
                if item.is_stock_item:
                    item_stock = get_stock_qty(item)
                item_dict.update(item_stock)
                
                group_dict.get('items').append(item_dict)
            data.append(group_dict)
    return data
def get_image_from_item(name):
    base_url = frappe.db.get_single_value('nbpos Setting', 'base_url')
    filters={'name': name, 'base_url': base_url}
    image = frappe.db.sql("""
        SELECT
                if((image = NULL or image = ''), null, 
                if(image LIKE 'http%%', image, concat(%(base_url)s, image))) as image
        FROM tabItem
        WHERE name = %(name)s
    """,values=filters)
    if image:
        return image[0][0]
    else: 
        return None
        
