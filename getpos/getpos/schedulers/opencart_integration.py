import requests
import json
import frappe
from frappe.utils import (flt,nowdate)


def order_integration():
	platform_setting=frappe.db.get_value("Platform Settings",{"platform_name": "opencart"},["api_key", "store_key", "cost_center", "user"], as_dict=True)
	if not platform_setting:
		print('Please set up keys for platform opencart')
	print('Start process')
	# URL = "https://api.api2cart.com/v1.1/order.list.json?api_key=deceaf85a856a8f07250b889e53f6329&store_key=ed58a22dfecb405a50ea3ea56979360d&customer_email=anil.tiwari%40yopmail.com&start=0&count=10&params=order_id%2Ccustomer%2Ctotals%2Caddress%2Citems%2Cbundles%2Cstatus%2Ccurrency"
	URL = "https://api.api2cart.com/v1.1/order.list.json?api_key=" + platform_setting.api_key + "&store_key=" + platform_setting.store_key + "&created_from=" + nowdate() +"&start=0&count=10&params=order_id%2Ccustomer%2Ctotals%2Caddress%2Citems%2Cbundles%2Cstatus%2Ccurrency"
	response = requests.get(URL)
    
	if response.status_code == 200:
		order_data = response.json()
		if order_data.get("return_code") == 0:
			order_result=order_data.get("result")
			orders=order_result.get("order")
			company = frappe.db.get_all("Company")[0].name
			company_doc = frappe.get_doc("Company", company)
			cost_center = platform_setting.cost_center #frappe.get_doc("Cost Center", {"cost_center_name":company_doc.company_name})	
			income_account_name = frappe.get_doc("Account", {"company":company_doc.company_name,"account_type":"Income Account","account_name":"Sales"})
			for o in orders:
				get_order=frappe.db.get_value("Sales Order",{"custom_order_id": o.get('order_id')},["name"], as_dict=True) 
				if not get_order:
					billing_address=customer=o.get("billing_address")
					phone=billing_address.get("phone")
					currency=o.get("currency")
					customer=get_customer(o.get("customer"),phone)				               
					status=o.get("status")               
					totals=o.get("totals")                
					products=o.get("order_products")
					items=[]
					
					for product in products:
						item={}						
						item_code=""
						item_code=frappe.db.get_value("Item",{"custom_product_id": product.get('product_id')},["name"], as_dict=True)                    
						if not item_code:
							item['item_code']=create_item(cost_center,company_doc.country,company_doc.company_name,income_account_name,product,platform_setting)
						else:
							item['item_code']=item_code

						item['qty']= product.get('quantity')
						item['rate']= product.get('price')
						items.append(item)

					create_sales_order_kiosk(status,"Cash","Store 01 - GP",customer,items,o.get("order_id"),currency.get("iso3"))	

								
	else:
		print('Error in the request, details:', response.text)
	
	print('End successfully')
	

def get_customer(customer,phone):
	customer_doc = frappe.db.get_value("Customer",{"custom_customer_id": customer.get('id')},["name", "customer_name", "mobile_no", "email_id"], as_dict=True)
	if not customer_doc:
		# Create Customer
		new_customer = frappe.new_doc("Customer")
		new_customer.customer_name = customer.get("first_name") + " " + customer.get("last_name")
		new_customer.mobile_no = phone
		new_customer.email_id = customer.get("email")
		new_customer.customer_group = 'All Customer Groups'
		new_customer.territory = 'All Territories'
		new_customer.custom_customer_id=customer.get("id")
		new_customer.custom_platform="opencart"
		new_customer.save(ignore_permissions=True)
		return new_customer.name
	else:
		return customer_doc.name

def create_item_group(item_group_name,category_id):	
	# Create item group
	new_item_group=frappe.new_doc("Item Group")
	new_item_group.item_group_name=item_group_name
	new_item_group.parent_item_group="All Item Groups"
	new_item_group.custom_category_id=category_id
	new_item_group.custom_platform="opencart"
	new_item_group.insert()
	return new_item_group
     
def get_platform_product(product_id,platform_setting):
    URL = "https://api.api2cart.com/v1.1/product.info.json?api_key=" + platform_setting.api_key + "&store_key=" + platform_setting.store_key + "&id=" + product_id + "&params=id%2Cname%2Cdescription%2Cprice%2Ccategories_ids"

    response = requests.get(URL)

    
    if response.status_code == 200:
        product_data = response.json()
        return product_data
    
def get_platform_category(cat_id):
    URL = "https://api.api2cart.com/v1.1/category.info.json?api_key=deceaf85a856a8f07250b889e53f6329&store_key=ed58a22dfecb405a50ea3ea56979360d&id="+ cat_id +"&params=id%2Cparent_id%2Cname%2Cdescription"

    response = requests.get(URL)

    
    if response.status_code == 200:
        category_data = response.json()
        return category_data

     
def create_item(cost_center,country,company,income_account_name,product,platform_setting):
	platform_product=get_platform_product(product.get('product_id'),platform_setting)
	if platform_product.get("return_code") == 0:
		product_result=platform_product.get("result")
		category_id=''
		for cat_id in product_result.get("categories_ids"):
			category_id=cat_id
			item_group=''
		item_group_name=frappe.db.get_value("Item Group",{"custom_category_id": category_id},["name"], as_dict=True)
		if not item_group_name:
			platform_category=get_platform_category(category_id)
			category_result=platform_category.get("result")			
			get_item_group=create_item_group(category_result.get("name"),category_id)
			item_group=get_item_group.name
		else:
			item_group=item_group_name       
		 
		# Create item
		new_item=frappe.new_doc("Item")
		new_item.item_code= product_result.get("name")
		new_item.item_name= product_result.get("name")
		new_item.item_group= item_group
		new_item.custom_item= "Standard Item"
		new_item.custom_enable_attributesmodifiers= 0
		new_item.is_stock_item= 1
		new_item.disabled= 0
		new_item.include_item_in_manufacturing= 1
		new_item.stock_uom= "Nos"
		new_item.custom_estimated_time= 0
		new_item.opening_stock= 100
		new_item.standard_rate= 150
		new_item.custom_web= 1
		new_item.custom_pos= 1
		new_item.custom_kiosk= 1
		new_item.custom_cost_center= cost_center
		new_item.description= product_result.get("name")
		new_item.is_purchase_item= 1
		new_item.country_of_origin= country
		new_item.grant_commission= 1
		new_item.is_sales_item= 1 
		new_item.variant_based_on="Item Attribute"
		new_item.append("item_defaults",{"company": company,"default_warehouse":get_warehouse_for_cost_center(platform_setting.cost_center),"parenttype":"Item","parent":product_result.get("name"),"parentfield":"item_defaults","income_account":income_account_name})
		new_item.custom_product_id=product.get('product_id')
		new_item.custom_platform="opencart"
		new_item.insert()
		return new_item.name 
      

def create_sales_order_kiosk(status,mode_of_payment,cost_center,customer,items,platform_order_id,currency):
	frappe.set_user("Administrator")
	res = frappe._dict()
	sales_order = frappe.new_doc("Sales Order")
	sales_order.hub_manager = "test@yopmail.com"
	sales_order.custom_source = "POS"
	sales_order.ward = ""
	sales_order.custom_order_request =""
	sales_order.customer = customer
	sales_order.transaction_date = nowdate()
	sales_order.delivery_date = nowdate()
	sales_order = add_items_in_order(sales_order, items)
	# sales_order.status = status
	sales_order.mode_of_payment = mode_of_payment
	sales_order.mpesa_no = ""
	sales_order.custom_order_id=platform_order_id
	sales_order.custom_platform="opencart"
	sales_order.currency=currency
	# if order_list.get("coupon_code"):
	# 	coupon_name = frappe.db.get_value("Coupon Code", {"coupon_code": order_list.get("coupon_code")},"name")
	# sales_order.coupon_code = coupon_name
	# if order_list.get("gift_card_code"):
	# 	sales_order.custom_gift_card_code = order_list.get("gift_card_code")
	sales_order.apply_discount_on="Grand Total"
	# sales_order.discount_amount=order_list.get("discount_amount")

	sales_order.disable_rounded_total = 1

	# Set custom payment status
	if mode_of_payment == "Card":
		sales_order.custom_payment_status = "Pending"
	else:
		sales_order.custom_payment_status = "Paid"

	# Set cost center and warehouse
	sales_order.cost_center = cost_center
	warehouse = get_warehouse_for_cost_center(cost_center)
	if warehouse:
		sales_order.set_warehouse = warehouse        

	sales_order.save(ignore_permissions=True)
	sales_order.rounded_total=sales_order.grand_total
	sales_order.submit()  
        
def get_warehouse_for_cost_center(cost_center):
	warehouse = frappe.db.get_value('Warehouse', {'custom_cost_center': cost_center}, 'name')
	return warehouse

def add_items_in_order(sales_order, items):
	sales_taxes = {}
	for item in items:
		item_tax_template = ""
		# if item.get('tax'):
		# 	item_tax_template = item.get('tax')[0].get('item_tax_template')
	# for tax in item.get('tax'):
	# 	if sales_taxes.get(tax.get('tax_type')):
	# 		sales_taxes[f"{tax.get('tax_type')}"] = flt(sales_taxes[f"{tax.get('tax_type')}"]) + tax.get('tax_amount')
	# 	else:
	# 		sales_taxes.update({f"{tax.get('tax_type')}": tax.get('tax_amount')})

		sales_order.append("items", {
			"item_code": item.get("item_code"),
			"qty": item.get("qty"),
			"rate": item.get("rate"), 
			"discount_percentage":100 if item.get("rate")==0 else 0,  
			# "custom_parent_item":item.get("custom_parent_item"),
			# "custom_is_attribute_item":item.get("custom_is_attribute_item"),
			# "custom_is_combo_item":item.get("custom_is_combo_item"),
			# "allow_zero_evaluation_rate":item.get("allow_zero_evaluation_rate"),                    
			#"item_tax_template": item_tax_template if item_tax_template else "" ,
			"custom_ca_id":"" #item.get("custom_ca_id")                
		})

	# for key,value in sales_taxes.items():
	# 	sales_order.append("taxes", {"charge_type": "On Net Total", "account_head": key, "tax_amount": value, "description": key, })


	# if order_list.get('tax'):
	# 	for tax in order_list.get('tax'):
	# 		sales_order.append("taxes", {"charge_type": "On Net Total", "account_head": tax.get('tax_type'), "tax_amount": tax.get('tax_amount'),
	# 			"description": tax.get('tax_type'), "rate": tax.get('tax_rate')})



	return sales_order