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
    

def get_stock_qty(item,cost_center=None):
    if not cost_center:
        bin_list = frappe.get_all('Bin', filters={'item_code': item.get('item_code')},
                                fields=['actual_qty', 'warehouse'], order_by='actual_qty desc')
    else:
        bin_list = frappe.get_all('Bin', filters={'item_code': item.get('item_code'),'warehouse':cost_center},
                                fields=['actual_qty', 'warehouse'], order_by='actual_qty desc')
        
    if bin_list:
        return [{"warehouse": bin.warehouse, 'stock_qty': bin.actual_qty} for bin in bin_list]
    else:
        return [{'warehouse': '', 'stock_qty': 0}]

    

# def get_combo_items(name):
#     combo_items = frappe.db.sql(''' Select
#     pbi.item_code , 
#     pbi.description , 
#     pbi.qty , 
#     pbi.uom
#     from `tabProduct Bundle` pb , `tabProduct Bundle Item`  pbi
#     Where pbi.parent = pb.name and pbi.parent = %s
#     ''',(name), as_dict = True)

#     if combo_items:          
#         return combo_items
#     else:
#         return []
    
# def get_combo_items(item_code,cost_center=None):
#     # For Adding Extra Items in Item
#     all_combo_items=frappe.db.sql(""" SELECT c.combo_heading as name,c.count,ci.item,ci.item_name,ci.item_price from `tabCombo Item` ci LEFT JOIN `tabCombo` c ON ci.parent=c.name WHERE c.parent_combo_item = '{}'  GROUP BY c.name,ci.name
# """.format(item_code),as_dict=1)
    
#     # Initialize an empty list for the output
#     output_data = []

#     # Create a dictionary to group items by 'name'
#     grouped_data = {}
#     for entry in all_combo_items:
#         name = entry['name']
#         item = entry['item']
#         heading="Select {}".format(entry['count'] if entry['count'] else 0)
#         if name not in grouped_data:
#             grouped_data[name] = {'name': name, 'description':heading,'options': []}
#         grouped_data[name]['options'].append(
#             {
#                 'item': item,'item_name':entry['item_name'],'price':entry.price if entry.price else get_price_list(item),
#                 'stock_qty':get_stock_qty({'item_code':item},cost_center) if get_stock_qty({'item_code':item},cost_center) else 0,
#                 'item_tax':get_item_taxes(item)})

#     output_data = list(grouped_data.values())
    
#     return output_data

def get_combo_items(item_code, cost_center=None):
    base_url = frappe.db.get_single_value('nbpos Setting', 'base_url')
    all_combo_items = frappe.db.sql("""
        SELECT 
            c.combo_heading as name,
            c.mandatory,
            c.count,
            ci.item,
            ci.item_name,
            ci.item_price,
            i.image as item_image
        FROM 
            `tabCombo Item` ci 
        LEFT JOIN 
            `tabCombo` c ON ci.parent = c.name 
        LEFT JOIN 
            `tabItem` i ON ci.item = i.name 
        WHERE 
            c.parent_combo_item = '{}'  
        GROUP BY 
            c.name, ci.name
    """.format(item_code), as_dict=1)
    
    # Initialize an empty list for the output
    output_data = []

    # Create a dictionary to group items by 'name'
    grouped_data = {}
    for entry in all_combo_items:
        name = entry['name']
        item = entry['item']
        heading = "Select {}".format(entry['count'] if entry['count'] else 0)
        if name not in grouped_data:
            grouped_data[name] = {'name': name,'mandatory':entry['mandatory'],'description': heading, 'options': []}
        grouped_data[name]['options'].append(
            {
                'item': item,
                'item_name': entry['item_name'],
                'price': entry['item_price'] if entry['item_price'] else get_price_list(item),
                'stock_qty': get_stock_qty({'item_code': item}, cost_center) if get_stock_qty({'item_code': item}, cost_center) else 0,
                'item_tax': get_item_taxes(item),
                'item_image': "{}/{}".format(base_url, entry['item_image']) if entry['item_image'] else None
            }
        )

    output_data = list(grouped_data.values())
    
    return output_data


    
# @frappe.whitelist()
# def get_updated_items(from_date=None, item_group=None, extra_item_group=None, item_code=None,item_type=None,item_order_by=None,cost_center=None,source=None):
   
#     data = []
#     filters = {'is_group':0,'name':['not in',('Extra')],
#                                 'parent_item_group':['not in',('Extra')]}
    # if item_order_by=='desc':
    #     item_order_by='item_name desc'
    # else:
    #     item_order_by='item_name asc'
#     if from_date:
#         filters.update({'modified':['>=',from_date]})

#     if item_group:
#         filters.update({'name': item_group})
    

#     all_groups = frappe.get_all('Item Group',filters=filters,fields=['name','image'],order_by='name asc')
#     for group in all_groups:
#         group_dict = {}
#         item_group_image = f"{base_url}{group.get('image')}" if group.get('image') else ''
                    

#         item_filters = {'item_group':group.name,'disabled':0,'custom_item':['not in',('Attribute/Modifier')]}
        
#         if item_code and not extra_item_group :

#             item_filters.update({ 'name': ['like', '%' + item_code +'%']})
        
#         if item_type :
#             item_filters.update({ 'custom_item_type': item_type })
            
#         if source:
#             if source=="WEB":
#                 item_filters.update({ 'custom_web': 1 })
#             elif source=="KIOSK":
#                 item_filters.update({ 'custom_kiosk': 1 })
#             elif source=="POS":
#                 item_filters.update({ 'custom_pos': 1 })
        

#         all_items = frappe.get_all('Item',filters = item_filters, fields=['*'],order_by=item_order_by)

#         if all_items:
#             group_dict.update({'item_group':group.name,
#             'item_group_image':item_group_image, 'items':[]}) 
#             for item in all_items:
#                 attributes = get_attributes_items(item.name,cost_center)

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
                

#                 allergens=[]
#                 item_dict = {'id':item.name,'name':item.item_name, 'combo_items': combo_items, 'attributes':attributes, 'image': image
#                 ,"tax":item_taxes,'descrption':item.description, 'estimated_time': item.custom_estimated_time,'item_type':item.custom_item_type,'allergens':allergens}
#                 item_price = flt(get_price_list(item.name))                
#                 if item_price:
#                     item_dict.update({'product_price':item_price})
#                 allergens.append(get_allergens(item.name)) 
                

#                 if item.is_stock_item:
#                     item_stock = get_stock_qty(item,cost_center)
#                     item_dict.update({'stock':item_stock})
                    
#                 group_dict.get('items').append(item_dict)
#             data.append(group_dict)
#     return data



@frappe.whitelist(allow_guest=True)
def get_items(from_date=None, item_group=None, extra_item_group=None, item_code=None, item_type=None, item_order_by=None, cost_center=None,source=None):
    data = []
    filters = {'is_group': 0, 'name': ['not in', ('Extra')],
               'parent_item_group': ['not in', ('Extra')]}
    
    if item_order_by=='desc':
        item_order_by='item_name desc'
    else:
        item_order_by='item_name asc'
    
    if from_date:
        filters.update({'modified': ['>=', from_date]})

    if item_group:
        filters.update({'name': item_group})


    all_groups = frappe.get_all('Item Group', filters=filters, fields=['name', 'image'], order_by='name asc')


    for group in all_groups:
        group_dict = {'item_group': group.name, 'item_group_image': f"{base_url}{group.get('image')}" if group.get('image') else '', 'items': []}

        #### Getting Items ####
        item_filters = {'item_group':group.name,'disabled':0,'custom_item':['not in',('Attribute/Modifier')]}

        if item_code and not extra_item_group:
            item_filters.update({'name': ['like', '%' + item_code + '%']})

        if item_type:
            item_filters.update({'custom_item_type': item_type})
        if cost_center:
                item_filters.update({'custom_cost_center': cost_center})
            
        if source:
            if source=="WEB":
                item_filters.update({ 'custom_web': 1 })
            elif source=="KIOSK":
                item_filters.update({ 'custom_kiosk': 1 })
            elif source=="POS":
                item_filters.update({ 'custom_pos': 1 })

        all_items = frappe.get_all('Item', filters=item_filters, fields=['*'],order_by=item_order_by)
        for item in all_items:
            attributes = get_attributes_items(item.name,cost_center)
            image = f"{base_url}{item.image}" if item.get('image') else ''
            item_taxes = get_item_taxes(item.name)
            combo_items = get_combo_items(item.name,cost_center)

            related_items = []
            allergens = []
            item_dict = {
                'id': item.name, 
                'name': item.item_name, 
                'combo_items': combo_items, 
                'attributes': attributes if item.custom_enable_attributesmodifiers==1 else [], 
                'image': image,
                "tax": item_taxes, 
                'description': item.description, 
                'related_items': [related_items], 
                'estimated_time': item.custom_estimated_time, 
                'item_type': item.custom_item_type,
                'allergens': [allergens]
            }
            item_price = flt(get_price_list(item.name))
            if item_price:
                item_dict.update({'product_price': item_price})

            # Get related items and their taxes
            related_items_data = get_related_items(item.name)
            nested_related_items_list = []

            for related_item in related_items_data:
                related_item_taxes = get_item_taxes(related_item['name'])
                related_item['tax'] = related_item_taxes

                # Get nested related items and their taxes
                nested_related_items_data = get_related_items(related_item['name'])
                nested_related_items = []

                for nested_related_item in nested_related_items_data:
                    nested_related_item_taxes = get_item_taxes(nested_related_item['name'])
                    nested_related_item['tax'] = nested_related_item_taxes
                    nested_related_items.append(nested_related_item)

                if not nested_related_items:
                    related_item['related_items'] = [[]]
                else:
                    related_item['related_items'] = [nested_related_items]

                nested_related_items_list.append(related_item)

            if not nested_related_items_list:
                item_dict['related_items'] = [[]]
            else:
                item_dict['related_items'] = [nested_related_items_list]

            allergens.extend(get_allergens(item.name))
            
            if item.is_stock_item:
                    item_stock = get_stock_qty(item,cost_center)
                    item_dict.update({'stock':item_stock})
                    
            group_dict.get('items').append(item_dict)
        if len(group_dict.get('items'))>0:
            data.append(group_dict)
    return data

    #         # # Checking Stock
    #         item_stock = {'warehouse': -1, 'stock_qty': -1}
    #         bundle_bin_qty = 1000000
    #         if item.is_stock_item:
    #             item_stock = get_stock_qty(item)
    #             item_dict.update(item_stock)
    #         # getting the reserve qty of child items in bundle so that end product can be calculated as per the ready-to-use qty
    #         elif len(item_dict.get("combo_items")) > 0:
    #             for combo_item in item_dict.get("combo_items"):
    #                 item_bin_qty = get_stock_qty(combo_item)
    #                 combo_item.update(item_bin_qty)
    #                 available_qty = item_bin_qty.get("stock_qty") / combo_item.get("qty")
    #                 if bundle_bin_qty > available_qty and frappe.get_value("Item", combo_item.item_code, "is_stock_item"):
    #                     bundle_bin_qty = available_qty
    #             item_stock["warehouse"] = item_dict.get("combo_items")[0].get("warehouse")
    #             item_stock["stock_qty"] = bundle_bin_qty
    #             item_dict.update(item_stock)

    #         if item_order_by:
    #             all_items_data['items'].append(item_dict)
    #         else:
    #             group_dict['items'].append(item_dict)

    #     # Exclude empty item groups when item_code or item_type filter is applied individually
    #     if not item_order_by and (item_code or item_type):
    #         if group_dict['items']:
    #             data.append(group_dict)
    #     elif not item_order_by:
    #         data.append(group_dict)

    # if item_order_by:
    #     all_items_data['items'] = sorted(all_items_data['items'], key=lambda x: x['name'], reverse=(item_order_by == 'desc'))
    #     data.append(all_items_data)

    # return data



def get_related_items_with_tax(item_name):
    related_items_data = get_related_items(item_name)
    related_items = []

    for related_item in related_items_data:
        related_item_taxes = get_item_taxes(related_item['name'])
        related_item['tax'] = related_item_taxes

        # Fetch related items for the related item recursively
        related_item['related_items'] = get_related_items_with_tax(related_item['name'])

        related_items.append(related_item)

    return related_items


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



def get_attributes_items(item_code,cost_center=None):
    # For Adding Extra Items in Item
    all_extra_items=frappe.db.sql(""" SELECT a.attribute_heading as name,a.mandatory,a.count,ai.item,ai.item_name,ai.price from `tabAttribute Items` ai LEFT JOIN `tabAttributes` a ON ai.parent=a.name WHERE a.parent_item = '{}'  GROUP BY a.name,ai.name
""".format(item_code),as_dict=1)
    
    # Initialize an empty list for the output
    output_data = []

    # Create a dictionary to group items by 'name'
    grouped_data = {}
    for entry in all_extra_items:
        name = entry['name']
        item = entry['item']
        heading="Select {}".format(entry['count'] if entry['count'] else 0)
        if name not in grouped_data:
            grouped_data[name] = {'name': name,'mandatory':entry['mandatory'],'description':heading,'options': []}
        grouped_data[name]['options'].append(
            {
                'item': item, 'item_name':entry['item_name'],'price':entry.price if entry.price else get_price_list(item),
                'stock_qty':get_stock_qty({'item_code':item},cost_center) if get_stock_qty({'item_code':item},cost_center) else 0,
                'item_tax':get_item_taxes(item)})

    # Convert grouped data to the desired output format
    output_data = list(grouped_data.values())
    
    # attributes = []
    # attributes_dict = {}
    # product_price_addition = 0
    # if all_extra_items:
    #     for extra_item in all_extra_items:
    #         extra_item_doc = frappe.get_cached_doc('Item',extra_item.item)
    #         extra_item_price = get_price_list(extra_item.item)
    #         item_tax = get_item_taxes(extra_item.item)

    #         #Checking Stock
    #         extra_item_stock = ''
    #         if extra_item_doc.is_stock_item:
    #             extra_item_stock = get_stock_qty(extra_item_doc)
    #         # print(attributes_dict,"====888")
    #         if not attributes_dict.get(extra_item_doc.name):
    #             # Checking item group
    #             moq, select_type = frappe.db.get_value('Item Group',extra_item_doc.item_group,['moq','select_type'])

    #             attributes_dict.update({
    #                             'type': select_type,'moq':moq,
    #                             'options': [{ 'id':  extra_item_doc.name, 'name':extra_item_doc.item_name,
    #                             'tax':item_tax if item_tax  else '',
    #                             'price': extra_item_price if extra_item_price else '','selected':True,
    #                             'warehouse':extra_item_stock.get('warehouse') if extra_item_stock else -1,
    #                             'stock_qty':extra_item_stock.get('stock_qty') if extra_item_stock else -1}],
    #                             })
    #             product_price_addition += flt(extra_item_price)
    #         else:
    #             attributes_dict.get(extra_item_doc.item_group).get('options').append({'id': extra_item_doc.name,
    #                                 'name': extra_item_doc.item_name, 'selected': False, 
    #                                 'price':extra_item_price if extra_item_price else '',
    #                                 'warehouse':extra_item_stock.get('warehouse'),'stock_qty':extra_item_stock.get('stock_qty')
    #                                 })
            
    # if attributes_dict:
    #     print(attributes_dict)
    #     # print(attributes_dict,"88888")
    #     for x in attributes_dict.items():
    #         attributes.append(x[1])
    # print(attributes,"++++++++++")
    return output_data



    
        
def get_item_taxes(name):
    from datetime import datetime
    
    filters = {'name': name, 'today': datetime.today().strftime('%Y-%m-%d')}
    
    tax = frappe.db.sql("""
    SELECT
        it.item_tax_template,
        ittd.tax_type,
        CONCAT(FORMAT(ittd.tax_rate, 2), '%%') AS custom_tax_percentage,
        it.valid_from
    FROM
        `tabItem` i,
        `tabItem Tax` it,
        `tabItem Tax Template` itt,
        `tabItem Tax Template Detail` ittd
    WHERE
        i.name = it.parent AND
        i.name = %(name)s AND
        it.item_tax_template = itt.name AND
        itt.name = ittd.parent AND
        it.valid_from <= %(today)s
    """, values=filters, as_dict=True)
    
    return tax

        
        
        
        
        
        
        
