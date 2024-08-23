import frappe
from erpnext.accounts.doctype.account.account import RootNotEditable
from frappe import _

def execute():
    create_demo_company()

def create_demo_company():
	company = frappe.db.get_all("Company")[0].name
	company_doc = frappe.get_doc("Company", company)

	# Make a dummy company
	new_company = frappe.new_doc("Company")
	new_company.company_name = company_doc.company_name + " (Demo)"
	new_company.abbr = company_doc.abbr + "D"
	new_company.enable_perpetual_inventory = 1
	new_company.default_currency = company_doc.default_currency
	new_company.country = company_doc.country
	new_company.chart_of_accounts_based_on = "Standard Template"
	new_company.chart_of_accounts = company_doc.chart_of_accounts	
	new_company.insert()

	# Set Demo Company as default to
	frappe.db.set_single_value("Global Defaults", "demo_company", new_company.name)
	frappe.db.set_default("company", new_company.name)

	bank_account = create_bank_account({"company_name": new_company.name})
	frappe.db.set_value("Company", new_company.name, "default_bank_account", bank_account.name)
	create_demo_CostCenter(company_doc.company_name + " (Demo)",company_doc.country)	
	

def create_demo_CostCenter(company_name,country):
	cost_center = frappe.get_doc("Cost Center", {"cost_center_name":company_name})	
	# Make a dummy cost center
	new_cost_center = frappe.new_doc("Cost Center")
	new_cost_center.cost_center_name = "Store (Demo)"
	new_cost_center.is_group = 0
	new_cost_center.custom_location = "Location (Demo)"
	new_cost_center.company = company_name
	new_cost_center.parent_cost_center = cost_center.name
	new_cost_center.insert()
	create_demo_warehouse(new_cost_center.name,company_name)
	create_demo_item_group()
	income_account_name = frappe.get_doc("Account", {"company":company_name,"account_type":"Income Account","account_name":"Sales"})	
	create_demo_item(new_cost_center.name,country,company_name,income_account_name.name,"item 1")
	create_demo_item(new_cost_center.name,country,company_name,income_account_name.name,"item 2")
	create_demo_item(new_cost_center.name,country,company_name,income_account_name.name,"item 3")
	create_demo_customer()

def create_demo_warehouse(cost_center,company_name):	
	# Make a dummy warehouse
	new_warehouse = frappe.new_doc("Warehouse")
	new_warehouse.warehouse_name = "Store (Demo)"
	new_warehouse.custom_cost_center = cost_center
	new_warehouse.company=company_name
	new_warehouse.insert()

def create_demo_item_group():
	# Make a dummy item group
	new_item_group=frappe.new_doc("Item Group")
	new_item_group.item_group_name="Item Group 01"
	new_item_group.parent_item_group="All Item Groups"
	new_item_group.insert()

def create_demo_item(cost_center,country,company,income_account_name,item_name):
	# Make a dummy item
	new_item=frappe.new_doc("Item")
	new_item.item_code= item_name
	new_item.item_name= item_name
	new_item.item_group= "Item Group 01"
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
	new_item.description= item_name
	new_item.is_purchase_item= 1
	new_item.country_of_origin= country
	new_item.grant_commission= 1
	new_item.is_sales_item= 1 
	new_item.variant_based_on="Item Attribute"
	new_item.append("item_defaults",{"company": company,"default_warehouse":cost_center,"parenttype":"Item","parent":item_name,"parentfield":"item_defaults","income_account":income_account_name})
	new_item.insert()

def create_demo_customer():
	new_customer = frappe.new_doc("Customer")
	new_customer.customer_name = "Customer (Demo)"
	new_customer.mobile_no = "9898989898"
	new_customer.email_id = "customer_demo@yopmail.com"
	new_customer.customer_group = 'All Customer Groups'
	new_customer.territory = 'All Territories'
	new_customer.save(ignore_permissions=True)


def create_bank_account(args):
	if not args.get("bank_account"):
		args["bank_account"] = _("Bank Account")

	company_name = args.get("company_name")
	bank_account_group = frappe.db.get_value(
		"Account",
		{"account_type": "Bank", "is_group": 1, "root_type": "Asset", "company": company_name},
	)
	if bank_account_group:
		bank_account = frappe.get_doc(
			{
				"doctype": "Account",
				"account_name": args.get("bank_account"),
				"parent_account": bank_account_group,
				"is_group": 0,
				"company": company_name,
				"account_type": "Bank",
			}
		)
		try:
			doc = bank_account.insert()

			if args.get("set_default"):
				frappe.db.set_value(
					"Company",
					args.get("company_name"),
					"default_bank_account",
					bank_account.name,
					update_modified=False,
				)

			return doc

		except RootNotEditable:
			frappe.throw(_("Bank account cannot be named as {0}").format(args.get("bank_account")))
		except frappe.DuplicateEntryError:
			# bank account same as a CoA entry
			pass