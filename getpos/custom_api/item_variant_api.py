import frappe
from frappe.utils import today,getdate,flt

settings = frappe.get_cached_doc('nbpos Setting')
base_url = settings.get('base_url')


def get_price_list(item_code):
    all_item_price = frappe.get_all('Item Price',filters={'item_code':item_code,'selling':1,'price_list':'Standard Selling',
                                    'valid_from':['<=',today()]},fields=['price_list_rate','valid_upto'],order_by='modified desc', limit=1)
    if all_item_price:
                    for item_price in all_item_price:
                        if not item_price.valid_upto:
                            return item_price.price_list_rate

                        elif (item_price.valid_upto).strftime('%Y-%m-%d') >= today():
                            return item_price.price_list_rate
    return 
    

def get_stock_qty(item):
    bin_list = frappe.get_all('Bin',filters={'item_code':item.item_code,'warehouse':['like','Stores%']},
                            fields=['actual_qty','warehouse'],order_by='actual_qty desc',limit_start=0,
                            limit_page_length=21)
    if bin_list:
        return {"warehouse":bin_list[0].warehouse,'stock_qty':bin_list[0].actual_qty}
            
    else:
        return {'warehouse': '','stock_qty':0}
    

def get_combo_items(name):
    combo_items = frappe.db.sql(''' Select
    pbi.item_code , 
    pbi.description , 
    pbi.qty , 
    pbi.uom
    from `tabProduct Bundle` pb , `tabProduct Bundle Item`  pbi
    Where pbi.parent = pb.name and pbi.parent = %s
    ''',(name), as_dict = True)

    if combo_items:          
        return combo_items
    else:
        return []



@frappe.whitelist(allow_guest=True)
def get_items(from_date=None, item_group=None, extra_item_group=None, item_code=None, item_type=None, item_order_by=None, cost_center=None):
    data = []
    filters = {'is_group': 0, 'name': ['not in', ('Extra')],
               'parent_item_group': ['not in', ('Extra')]}
    
    if from_date:
        filters.update({'modified': ['>=', from_date]})

    if item_group:
        filters.update({'name': item_group})

    if extra_item_group:
        item_groups = get_related_item_groups(extra_item_group)
        filters.update({'name': ['in', item_groups]})

    all_groups = frappe.get_all('Item Group', filters=filters, fields=['name', 'image'], order_by='name asc')

    all_items_data = {'items': []} if item_order_by else None

    for group in all_groups:
        group_dict = {'item_group': group.name, 'item_group_image': f"{base_url}{group.get('image')}" if group.get('image') else '', 'items': []}

        attributes = get_attributes_items(group)

        #### Getting Items ####
        item_filters = {'item_group': group.name, 'disabled': 0}

        if item_code and not extra_item_group:
            item_filters.update({'name': ['like', '%' + item_code + '%']})

        if item_type:
            item_filters.update({'custom_item_type': item_type})

        all_items = frappe.get_all('Item', filters=item_filters, fields=['*'])

        for item in all_items:
            # Check if the item is available in the specified cost center
            if cost_center:
                cost_center_exists = frappe.db.exists('Item Cost Center', {
                    'parent': item.name,
                    'cost_center': cost_center,
                    'is_available': 1
                })
                if not cost_center_exists:
                    continue
            image = f"{base_url}{item.image}" if item.get('image') else ''
            item_taxes = get_item_taxes(item.name)
            combo_items = get_combo_items(item.name)

            related_items = []
            allergens = []
            item_dict = {'id': item.name, 'name': item.item_name, 'combo_items': combo_items, 'attributes': attributes, 'image': image,
                         "tax": item_taxes, 'description': item.description, 'related_items': related_items, 'estimated_time': item.custom_estimated_time, 'item_type': item.custom_item_type, 'allergens': allergens}
            item_price = flt(get_price_list(item.name))
            if item_price:
                item_dict.update({'product_price': item_price})
            related_items.append(get_related_items(item.name))
            allergens.append(get_allergens(item.name))

            # Checking Stock
            item_stock = {'warehouse': -1, 'stock_qty': -1}
            bundle_bin_qty = 1000000
            if item.is_stock_item:
                item_stock = get_stock_qty(item)
                item_dict.update(item_stock)
            # getting the reserve qty of child items in bundle so that end product can be calculated as per the ready-to-use qty
            elif len(item_dict.get("combo_items")) > 0:
                for combo_item in item_dict.get("combo_items"):
                    item_bin_qty = get_stock_qty(combo_item)
                    combo_item.update(item_bin_qty)
                    available_qty = item_bin_qty.get("stock_qty") / combo_item.get("qty")
                    if bundle_bin_qty > available_qty and frappe.get_value("Item", combo_item.item_code, "is_stock_item"):
                        bundle_bin_qty = available_qty
                item_stock["warehouse"] = item_dict.get("combo_items")[0].get("warehouse")
                item_stock["stock_qty"] = bundle_bin_qty
                item_dict.update(item_stock)

            if item_order_by:
                all_items_data['items'].append(item_dict)
            else:
                group_dict['items'].append(item_dict)

        # Exclude empty item groups when item_code or item_type filter is applied individually
        if not item_order_by and (item_code or item_type):
            if group_dict['items']:
                data.append(group_dict)
        elif not item_order_by:
            data.append(group_dict)

    if item_order_by:
        all_items_data['items'] = sorted(all_items_data['items'], key=lambda x: x['name'], reverse=(item_order_by == 'desc'))
        data.append(all_items_data)

    return data



    
# @frappe.whitelist()
# def get_items(from_date=None, item_group=None, extra_item_group=None, item_code=None,item_type=None,item_order_by=None,cost_center=None):
   
#     data = []
#     filters = {'is_group':0,'name':['not in',('Extra')],
#                                 'parent_item_group':['not in',('Extra')]}
#     if item_order_by=='desc':
#         item_order_by='item_name desc'
#     else:
#         item_order_by='item_name asc'
#     if from_date:
#         filters.update({'modified':['>=',from_date]})

#     if item_group:
#         filters.update({'name': item_group})
    
#     if extra_item_group:
#         item_groups = get_related_item_groups(extra_item_group)
#         filters.update({'name':['in', item_groups]})

#     all_groups = frappe.get_all('Item Group',filters=filters,fields=['name','image'],order_by='name asc')
#     for group in all_groups:
#         group_dict = {}
#         item_group_image = f"{base_url}{group.get('image')}" if group.get('image') else ''


#         attributes = get_attributes_items(group)
                    
#         #### Getting Items ####
#         filters = {'item_group':group.name,'disabled':0}
        
#         if item_code and not extra_item_group :
#             # filters.update({'name': item_code})
#             filters.update({ 'name': ['like', '%' + item_code +'%']})
        
#         if item_type :
#             filters.update({ 'custom_item_type': item_type })
            

#         all_items = frappe.get_all('Item',filters = filters, fields=['*'],order_by=item_order_by)

#         if all_items:
#             group_dict.update({'item_group':group.name,
#             'item_group_image':item_group_image, 'items':[]}) 
#             for item in all_items:
#                  # Check if the item is available in the specified cost center
#                 if cost_center:
#                     cost_center_exists = frappe.db.exists('Item Cost Center', {
#                         'parent': item.name,
#                         'cost_center': cost_center,
#                         'is_available': 1  
#                     })
#                     if not cost_center_exists:
#                         continue
#                 image = f"{base_url}{item.image}" if item.get('image') else ''
#                 item_taxes = get_item_taxes(item.name)
#                 combo_items = get_combo_items(item.name)
                
#                 related_items=[]
#                 allergens=[]
#                 item_dict = {'id':item.name,'name':item.item_name, 'combo_items': combo_items, 'attributes':attributes, 'image': image
#                 ,"tax":item_taxes,'descrption':item.description,'related_items':related_items, 'estimated_time': item.custom_estimated_time,'item_type':item.custom_item_type,'allergens':allergens}
#                 item_price = flt(get_price_list(item.name))                
#                 if item_price:
#                     item_dict.update({'product_price':item_price})
#                 related_items.append(get_related_items(item.name))
#                 allergens.append(get_allergens(item.name)) 
                
                        
#                 # Checking Stock
#                 item_stock = {'warehouse':-1,'stock_qty':-1}
#                 bundle_bin_qty = 1000000
#                 if item.is_stock_item:
#                     item_stock = get_stock_qty(item)
#                     item_dict.update(item_stock)
#                 # getting the reserve qty of child items in bundle so that end product can be calcuate as per the ready to use qty
#                 elif len(item_dict.get("combo_items")) > 0:
#                     for item in item_dict.get("combo_items"):
#                         item_bin_qty = get_stock_qty(item)
#                         item.update(item_bin_qty)
#                         available_qty = item_bin_qty.get("stock_qty") / item.get("qty")
#                         if bundle_bin_qty > available_qty and frappe.get_value("Item", item.item_code, "is_stock_item"):
#                             bundle_bin_qty = available_qty
#                     item_stock["warehouse"] = item_dict.get("combo_items")[0].get("warehouse")
#                     item_stock["stock_qty"] = bundle_bin_qty
#                     item_dict.update(item_stock)
                
#                 # item_dict.update(item_stock)
                    
#                 group_dict.get('items').append(item_dict)
#             data.append(group_dict)
#     return data




def get_related_items(item_name):
    related_items=[]
    get_related_items_=frappe.get_all('Related Item',filters={"parent": item_name},fields=['item'])
    if get_related_items_:
        for related_item in get_related_items_:
            sub_related_items=[]
            allergens=[]
            item_detail=frappe.get_value('Item',related_item.get('item'),['name','description','image','custom_estimated_time','item_name','custom_item_type'])
            if item_detail:
                related_item_price = flt(get_price_list(related_item.get('item'))) 
                allergens.append(get_allergens(item_detail[4]))
                related_group_items={'id':item_detail[0],'name':item_detail[4],'description':item_detail[1],'image':f"{base_url}{item_detail[2]}",'estimated_time': item_detail[3],'item_type':item_detail[5],'product_price':related_item_price,'allergens':allergens,'related_items':sub_related_items}
                sub_related_items.append(get_related_items(item_detail[0]))       
            
            related_items.append(related_group_items)

    return related_items

def get_allergens(item_name):
    allergens=[]
    get_allergens_=frappe.get_all('Item Allergens',filters={"parent": item_name},fields=['allergens']) 
    if get_allergens_:
        for allergens_item in get_allergens_:           
            allergens_item_detail=frappe.get_value('Allergens',allergens_item.get('allergens'),['allergens','icon'])
            if allergens_item_detail:
                allergens_items={'allergens':allergens_item_detail[0],'icon':f"{base_url}{allergens_item_detail[1]}"}
            allergens.append(allergens_items)
    return allergens

def get_related_item_groups(extra_item_group):
    item_groups = frappe.db.sql('''select distinct igm.item_group from `tabItem` i , `tabItem Group Multiselect`igm  
                                where igm.parent = i.name and i.item_group = %(item_group)s''',{'item_group':extra_item_group}, as_dict=1)
    
    
    return [item_group.item_group for item_group in item_groups]



def get_attributes_items(group=None):
     # For Adding Extra Items in Item
    all_extra_items = frappe.get_all('Item Group Multiselect',parent_doctype="Item",filters={'item_group':group.name},fields=['parent'])
    attributes = []
    attributes_dict = {}
    product_price_addition = 0
    if all_extra_items:
        for extra_item in all_extra_items:
            extra_item_doc = frappe.get_cached_doc('Item',extra_item.parent)
            extra_item_price = get_price_list(extra_item.parent)
            item_tax = get_item_taxes(extra_item.parent)

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
                                'tax':item_tax if item_tax  else '',
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
    return attributes


        

def get_item_taxes(name):
    filters={'name': name}
    tax = frappe.db.sql("""
    SELECT
        it.item_tax_template , 
        ittd.tax_type, 
        ittd.tax_rate,
        ittd.custom_tax_percentage
    FROM `tabItem` i , `tabItem Tax` it , `tabItem Tax Template` itt , `tabItem Tax Template Detail` ittd
    WHERE i.name = it.parent and i.name = %(name)s and
    it.item_tax_template = itt.name and itt.name = ittd.parent
    """,values=filters ,  as_dict = True)
    
    return tax
    
        
        
        
        
        
        
        
        
        
