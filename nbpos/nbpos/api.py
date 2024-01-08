import frappe
import json
from frappe import _
STANDARD_USERS = ("Guest", "Administrator")
from frappe.rate_limiter import rate_limit
from frappe.utils.password import get_password_reset_limit
from frappe.utils import (cint,get_formatted_email, nowdate, nowtime)
from erpnext.accounts.utils import get_balance_on
from erpnext.stock.utils import get_stock_balance
from erpnext.stock.stock_ledger import get_previous_sle, get_stock_ledger_entries


@frappe.whitelist( allow_guest=True )
def login(usr, pwd):
    try:
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(user=usr, pwd=pwd)
        login_manager.post_login()

        user = frappe.get_doc('User', frappe.session.user)
        
        if user.api_key and user.api_secret:
                user.api_secret = user.get_password('api_secret')
        else:
                api_generate = generate_keys(frappe.session.user)     


        frappe.response["message"] = {
                "success_key":1,
                "message":"success",
                "sid":frappe.session.sid,
                "api_key":user.api_key if user.api_key else api_generate[1],
                "api_secret": user.api_secret if user.api_secret else api_generate[0],
                "username":user.username,
                "email":user.email
        }
    except Exception as e:
        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success_key":0,
            "message":"Incorrect username or password",
            "error":e
        }
        
        return 


def generate_keys(user):
    user_details = frappe.get_doc('User', user)
    api_secret = frappe.generate_hash(length=15)

    # if not user_details.api_key:
    api_key = frappe.generate_hash(length=15)
    user_details.api_key = api_key

    user_details.api_secret = api_secret
    user_details.save(ignore_permissions=True)

    if frappe.request.method == "GET":
        frappe.db.commit()
    

    return user_details.get_password("api_secret"), user_details.api_key
       


@frappe.whitelist(allow_guest=True)
@rate_limit(key='user', limit=get_password_reset_limit, seconds = 24*60*60, methods=['POST'])
def forgot_password(user):
        if user=="Administrator":
                return 'not allowed'

        try:
                user = frappe.get_doc("User", user)
                if not user.enabled:
                        return 'disabled'

                user.validate_reset_password()
                user.reset_password(send_email=True)

                return  {
                        "success_key":1,
                        "message":"Password reset instructions have been sent to your email"
                        }
                
        except frappe.DoesNotExistError:
                frappe.clear_messages()
                del frappe.local.response["exc_type"]
                frappe.local.response["message"] = {
                        "success_key":0,
                        "message":"User not found"
                        }

@frappe.whitelist(allow_guest=True)
def reset_password( user,send_email=False, password_expired=False):
                from frappe.utils import random_string, get_url

                key = random_string(32)
                

                url = "/update-password?key=" + key
                if password_expired:
                        url = "/update-password?key=" + key + '&password_expired=true'

                link = get_url(url)
                if send_email:
                        user.password_reset_mail(link)
                return link

@frappe.whitelist( allow_guest=True )
def password_reset_mail(user, link):
                user.send_login_mail(("Password Reset"),
                        "password_reset", {"link": link}, now=True)

@frappe.whitelist()
def change_password(usr, pwd):
        username = frappe.db.get_value("User", usr, 'name')
        if username:
                user_doc = frappe.get_doc("User", usr)
                user_doc.new_password = pwd
                user_doc.save()
                frappe.db.commit()
                frappe.local.response["message"] = {
                "success_key":1,
                "message":"success"
                }
        else:
                frappe.local.response["message"] = {
                "success_key":1,
                "message":"User not found"
                }

@frappe.whitelist( allow_guest=True )                
def send_login_mail(user, subject, template, add_args, now=None):
                """send mail with login details"""
                from frappe.utils.user import get_user_fullname
                from frappe.utils import get_url

                created_by = get_user_fullname(frappe.session['user'])
                if created_by == "Guest":
                        created_by = "Administrator"

                args = {
                        'first_name': user.first_name or user.last_name or "user",
                        'user': user.name,
                        'title': subject,
                        'login_url': get_url(),
                        'created_by': created_by
                }

                args.update(add_args)

                sender = frappe.session.user not in STANDARD_USERS and get_formatted_email(frappe.session.user) or None

                frappe.sendmail(recipients=user.email, sender=sender)


@frappe.whitelist(allow_guest=True)
def get_abbr(string):
    abbr = ''.join(c[0] for c in string.split()).upper()
    return abbr

@frappe.whitelist(allow_guest=True)
def terms_and_conditions():
        terms_and_condition = frappe.db.sql("""
                SELECT terms
                FROM `tabTerms and Conditions`
                WHERE disabled = 0
        """)[0][0]
        return terms_and_condition


@frappe.whitelist(allow_guest=True)
def privacy_policy_and_terms():
        privacy_policy_and_terms = frappe.db.sql("""
                SELECT privacy_policy,terms_and_conditions
                FROM `tabPrivacy Policy and Terms`
                WHERE disabled = 0
        """)
        res = {"success_key":1,
                "message":"success",
                "Privacy_Policy":privacy_policy_and_terms[0][0],
                "Terms_and_Conditions":privacy_policy_and_terms[0][1]}
        if res["Privacy_Policy"]=="" or res["Terms_and_Conditions"]=="":
                return {
            "success_key":0,
            "message":"no value found for privacy policy and terms"
        }
        return res

@frappe.whitelist()
def get_customer_list_by_hubmanager(hub_manager, last_sync = None):
        res = frappe._dict()
        base_url = frappe.db.get_single_value('nbpos Setting', 'base_url')
        filters = {'hub_manager': hub_manager, "base_url": base_url}
        conditions = "hub_manager = %(hub_manager)s "
        if last_sync:
                filters['last_sync'] = last_sync
                conditions += "and modified >= %(last_sync)s"
        customer_list = frappe.db.sql("""
                SELECT
                        customer_name, email_id, mobile_no,
                        ward, ward_name, name, creation,
                        modified,disabled,
                        if((image = null or image = ''), null, 
                        if(image LIKE 'http%%', image, concat(%(base_url)s, image))) as image
                FROM `tabCustomer`
                WHERE {conditions}
                """.format(conditions=conditions), values=filters, as_dict=1)
        if len(customer_list) == 0:
                frappe.clear_messages()
                frappe.local.response["message"] = {
                        "success_key":1,
                        "message":"No values found for this hub manager"
                        }
        else:
                res["success_key"] = 1
                res["message"] = "success"
                res["customer_list"] = customer_list          
                return res 

# Not using for Mobile App
@frappe.whitelist()
def get_item_list_by_hubmanager(hub_manager, last_sync = None):
        res = frappe._dict()
        item_list_based_stock_sync = []
        if last_sync:
                arr =last_sync.split(" ")
                last_sync_date = arr[0]
                if len(arr) < 2:
                        last_sync_time = '00:00:00'
                else:
                        last_sync_time = arr[1]
        base_url = frappe.db.get_single_value('nbpos Setting', 'base_url')
        filters = {'hub_manager': hub_manager, "base_url": base_url}
        conditions = "h.hub_manager = %(hub_manager)s "
        item_list = get_item_list(filters, conditions)
        for item in item_list:
                if last_sync:
                        stock_detail = get_item_stock_balance(hub_manager, item.item_code, last_sync_date, last_sync_time)
                        if stock_detail:
                                item_list_based_stock_sync.append(item)
                else:
                        stock_detail = get_item_stock_balance(hub_manager, item.item_code)
                        item.available_qty = stock_detail.get("available_qty")
                        item.stock_modified = str(stock_detail.get("posting_date"))+" "+str(stock_detail.get("posting_time"))
        if last_sync:
                filters['last_sync'] = last_sync
                conditions += "and (i.modified >= %(last_sync)s or p.modified >= %(last_sync)s)"
                item_list_syn_based = get_item_list(filters, conditions)
                for i in item_list_based_stock_sync:
                        if i in item_list_syn_based:
                                item_list_syn_based.remove(i)
                item_list = item_list_based_stock_sync + item_list_syn_based
                for item in item_list:
                        stock_detail = get_item_stock_balance(hub_manager, item.item_code)
                        item.available_qty = stock_detail.get("available_qty")
                        item.stock_modified = str(stock_detail.get("posting_date"))+" "+str(stock_detail.get("posting_time"))
                if len(item_list) == 0:
                        frappe.clear_messages()
                        frappe.local.response["message"] = {
                                "success_key":1,
                                "message":"No values found for this hub manager"
                        }
                else:
                        res["success_key"] = 1
                        res["message"] = "success"
                        res["item_list"] = item_list 
                        return res        
        else:
                if len(item_list) == 0:
                        frappe.clear_messages()
                        frappe.local.response["message"] = {
                                "success_key":1,
                                "message":"No values found for this hub manager"
                        }
                else:
                        res["success_key"] = 1
                        res["message"] = "success"
                        res["item_list"] = item_list
                        return res 

@frappe.whitelist()
def get_item_list(filters, conditions, item_code = None):
        return frappe.db.sql("""
                SELECT 
                        i.item_code, i.item_name, i.item_group, i.description,
                        i.has_variants, i.variant_based_on,
                        if((i.image = null or image = ''), null, 
                        if(i.image LIKE 'http%%', i.image, concat(%(base_url)s, i.image))) as image,
                        p.price_list_rate, i.modified as item_modified, p.modified as price_modified 
                FROM `tabItem` i, `tabHub Manager Detail` h,`tabItem Price` p
                WHERE   h.parent = i.name and h.parenttype = 'Item' 
                        and p.item_code = i.name and p.selling =1
                        and p.price_list_rate > 0 
                        and {conditions}
        """.format(conditions=conditions), values=filters, as_dict=1)
        
        
        
@frappe.whitelist()
def get_details_by_hubmanager(hub_manager):
    try:
        res = frappe._dict()
        base_url = frappe.db.get_single_value('nbpos Setting', 'base_url')
        filters = {'hub_manager': hub_manager, "base_url": base_url}
        currency = frappe.get_doc("Global Defaults").default_currency
        currency_symbol=frappe.get_doc("Currency",currency).symbol
        conditions = "email = %(hub_manager)s "
        hub_manager_detail = frappe.db.sql("""
                SELECT
                        u.name, u.full_name,
                        u.email , if(u.mobile_no,u.mobile_no,'') as mobile_no,
                        if(u.user_image, if(u.user_image LIKE 'http%%', u.user_image, concat(%(base_url)s, u.user_image)), '') as image
                FROM `tabUser` u
                WHERE
                {conditions}
                """.format(conditions=conditions), values=filters, as_dict=1)
        cash_balance = get_balance(hub_manager)
        last_txn_date = get_last_transaction_date(hub_manager)
       
        res["success_key"] = 1
        res["message"] = "success"
        res["name"] = hub_manager_detail[0]["name"]
        res["full_name"] = hub_manager_detail[0]["full_name"]
        res["email"] = hub_manager_detail[0]["email"]
        res["mobile_no"] = hub_manager_detail[0]["mobile_no"]
        res["hub_manager"] = hub_manager_detail[0]["name"]
        res["series"] = ""
        res["image"] = hub_manager_detail[0]["image"]
        res["app_currency"] = currency_symbol
        res["balance"] = cash_balance
        res["last_transaction_date"] =  last_txn_date if last_txn_date else ''
        res["wards"] = []
   
        return res
    except Exception as e:
        frappe.clear_messages()
        frappe.local.response["message"] = {
                "success_key":0,
                "message":"No values found for this hub manager"
        }



@frappe.whitelist()
def get_balance(hub_manager):
        account = frappe.db.get_value('Account', {'hub_manager': hub_manager}, 'name')
        account_balance = get_balance_on(account)
        return account_balance if account_balance else 0.0


@frappe.whitelist()
def create_sales_order():
        order_list = frappe.request.data
        order_list = json.loads(order_list)
        order_list = order_list["order_list"]
        try:
                res= frappe._dict()
                sales_order = frappe.new_doc("Sales Order")
                sales_order.hub_manager = order_list.get("hub_manager")
                sales_order.ward = order_list.get("ward")
                sales_order.customer = order_list.get("customer")
                arr = order_list.get("transaction_date").split(" ")
                sales_order.transaction_date = arr[0]
                sales_order.transaction_time = arr[1]
                sales_order.delivery_date = order_list.get("delivery_date")
                sales_order = add_items_in_order(sales_order, order_list.get("items"))
                sales_order.status = order_list.get("status")
                sales_order.mode_of_payment = order_list.get("mode_of_payment")
                sales_order.mpesa_no = order_list.get("mpesa_no")
                sales_order.coupon_code = order_list.get("coupon_code")
                # sales_order = add_taxes(sales_order) 
                sales_order.save()
                sales_order.submit()
                res['success_key'] = 1
                res['message'] = "success"
                res["sales_order"] ={"name" : sales_order.name,
                "doc_status" : sales_order.docstatus}
                if "exc_type" in frappe.local.response:
                        del frappe.local.response["exc_type"]
                return res

        except Exception as e:
                if "exc_type" in frappe.local.response:
                        del frappe.local.response["exc_type"]
                frappe.local.response["message"] ={
                "success_key":0,
                "message":e
                        }

def add_items_in_order(sales_order, items):
        for item in items:
                if item.get('tax'):
                        item_tax_template = item.get('tax')[0].get('item_tax_template')

                sales_order.append("items", {
                        "item_code": item.get("item_code"),
                        "qty": item.get("qty"),
                        "rate": item.get("rate"),
                        "item_tax_template": item_tax_template if item_tax_template else ""                
                })

                if item.get("sub_items"):
                        for extra_item in item.get("sub_items"):
                              if extra_item.get('tax'):
                                     extra_item_tax_template = extra_item.get('tax')[0].get('item_tax_template')
                              sales_order.append("items", {
                                "item_code": extra_item.get("item_code"),
                                "qty": extra_item.get("qty"),
                                "rate": extra_item.get("rate"),
                                "associated_item": item.get('item_code'),
                                "item_tax_template": extra_item_tax_template if extra_item_tax_template else "" 
                                })
        return sales_order


def add_taxes(doc):
        all_taxes = frappe.get_all('Account',filters={'account_name':["in",["Output Tax SGST","Output Tax CGST"]]},
                                fields=['name','account_name'])
        if all_taxes:
                for tax in all_taxes:
                        doc.append('taxes',{'charge_type':'On Net Total',
                                        'account_head': tax.name,
                                        'rate':0,
                                        'cost_center':'Main - NP',
                                        'description': tax.account_name
                                        })
        return doc
        
def get_item_tax_template(name):
    filters={'name': name}
    tax = frappe.db.sql("""
    SELECT
        it.item_tax_template
    FROM `tabItem` i , `tabItem Tax` it
    WHERE i.name = it.parent and i.name = %(name)s
    """,values=filters ,  as_dict = True)
    if tax:
        return tax
    else: 
        return []

def get_combo_items(name):
        print(name)
        combo_items = frappe.db.sql(''' Select 
        pi.parent_item,
        pi.item_code , 
        pi.item_name ,
        pi.qty , 
        pi.uom
        from `tabSales Order` so , `tabPacked Item`  pi
        Where 
        so.name = %s and
        so.name = pi.parent
        ''',(name), as_dict = True)
     
        return combo_items
        
@frappe.whitelist()
def get_sales_order_list(hub_manager = None, page_no = 1, from_date = None, to_date = nowdate() , mobile_no = None):
        res= frappe._dict()
        base_url = frappe.db.get_single_value('nbpos Setting', 'base_url')
        filters = {'hub_manager': hub_manager, 'base_url': base_url}
        sales_history_count = frappe.db.get_single_value('nbpos Setting', 'sales_history_count')
        limit = cint(sales_history_count)
        conditions = ""
        if mobile_no:
                conditions += f" and s.contact_mobile like '%{str(mobile_no).strip()}%'"
       
        if from_date:
                conditions += " and s.transaction_date between {} and {} order by s.creation desc".format(frappe.db.escape(from_date), frappe.db.escape(to_date))
        else:
                if page_no == 1:
                        row_no = 0
                        conditions += f" order by s.creation desc limit {row_no} , {limit}"
                else:
                        page_no = cint(page_no) - 1
                        row_no = cint(page_no * cint(sales_history_count))
                        conditions += f" order by s.creation desc limit {row_no} , {limit}"
                        
        order_list = frappe.db.sql("""SELECT 
                        s.name, s.transaction_date, TIME_FORMAT(s.transaction_time, '%T') as transaction_time, s.ward, s.customer,s.customer_name, 
                        s.ward, s.hub_manager, s.total , s.total_taxes_and_charges , s.grand_total, s.mode_of_payment, 
                        s.mpesa_no, s.contact_display as contact_name,
                        s.contact_phone, s.contact_mobile, s.contact_email,
                        s.hub_manager, s.creation,
                        u.full_name as hub_manager_name,
                        if((c.image = null or c.image = ''), null, 
                        if(c.image LIKE 'http%%', c.image, concat({base_url}, c.image))) as image
                FROM `tabSales Order` s, `tabUser` u, `tabCustomer` c
                WHERE s.hub_manager = u.name and s.customer = c.name 
                        and s.hub_manager = {hub_manager}  and s.docstatus = 1 
                         {conditions}
        """.format(conditions=conditions, hub_manager= frappe.db.escape(hub_manager),
        base_url= frappe.db.escape(base_url)), as_dict= True)
        for item in order_list:
                item_details = frappe.db.sql("""
                        SELECT
                                so.item_code, so.item_name, so.qty,
                                so.uom, so.rate, so.amount,
                                if((i.image = null or i.image = ''), null, 
                                if(i.image LIKE 'http%%', i.image, concat(%s, i.image))) as image
                        FROM 
                                `tabSales Order` s, `tabItem` i, `tabSales Order Item` so
                        WHERE 
                                so.parent = s.name and so.item_code = i.item_code 
                                and so.parent = %s and so.parenttype = 'Sales Order' 
                                and so.associated_item is null
                """, (base_url,item.name), as_dict = True)

                
                associate_items = get_sub_items(item.name)
                new_item_details = []
                if associate_items:
                        for so_item in item_details :
                                so_item['sub_items'] = list(filter( lambda x : x.get("associated_item")== so_item.get("item_code"), associate_items  ) )
                                
                                new_item_details.append(so_item)
                                
                combo_items = get_combo_items(item.name)

                if combo_items:
                        for item_detail in new_item_details :
                                item_detail["combo_items"] = list(filter( lambda x: x.get("parent_item") == item_detail.item_code , combo_items )) 
                                
                item['items'] = new_item_details
        if mobile_no:
                conditions += f" and s.contact_mobile like '%{str(mobile_no).strip()}%'"

                number_of_orders = frappe.db.sql(f"SELECT COUNT(*) FROM `tabSales Order` s WHERE s.hub_manager = {frappe.db.escape(hub_manager)} and s.docstatus = 1 and s.contact_mobile like '%{str(mobile_no).strip()}%'")[0][0]

        else:
                number_of_orders = get_sales_order_count(hub_manager)
                
        if from_date:
                number_of_orders = len(order_list)

        if len(order_list) == 0 and number_of_orders == 0:
            frappe.clear_messages()
            frappe.local.response["message"] = {
                "success_key":1,
                "message":"no values found for this hub manager "
            }
        else:
            res["success_key"] = 1
            res["message"] = "success"
            res['order_list'] = order_list
            res['number_of_orders'] = number_of_orders
            return res
       



@frappe.whitelist()
def get_sales_order_count(hub_manager):
        number_of_orders = frappe.db.sql("""
                SELECT 
                        count(s.name)
                FROM `tabSales Order` s, `tabUser` u
                WHERE s.hub_manager = u.name and s.hub_manager = %s
                        and s.docstatus = 1 
                        order by s.creation desc
        """, (hub_manager))[0][0]
        return number_of_orders




@frappe.whitelist()
def get_last_transaction_date(hub_manager):
        account = frappe.db.get_value('Account', {'hub_manager': hub_manager, 'disabled': 0}, 'name')
        transaction_date = frappe.db.get_list("GL Entry",
                        filters={
                                'account': account,
                                'voucher_type': ["!=",'Period Closing Voucher'],
                                'is_cancelled': 0
                        },
                        fields= ['posting_date'],
                        order_by = "posting_date desc",
                        as_list = 1
        )
        if transaction_date:
                transaction_date = transaction_date[0][0]
        else:
                transaction_date = None
        return transaction_date

@frappe.whitelist()
def get_item_stock_balance(hub_manager, item_code, last_sync_date=None, last_sync_time="00:00"):
        res = frappe._dict()
        warehouse = frappe.db.get_value('Warehouse', {'hub_manager': hub_manager}, 'name')
        if last_sync_date and last_sync_time:
                args = {
		"item_code": item_code,
		"warehouse":warehouse,
		"posting_date": last_sync_date,
		"posting_time": last_sync_time
                }
                last_entry = get_stock_ledger_entries(args, ">", "desc", "limit 1", for_update=False, check_serial_no=False)
                if last_entry:
                        res['available_qty'] = get_stock_balance(item_code, warehouse, last_entry[0].posting_date, last_entry[0].posting_time)
                        res['posting_date'] = last_entry[0].posting_date
                        res['posting_time'] = last_entry[0].posting_time

        else:
                res['available_qty'] = get_stock_balance(item_code, warehouse)
                args = {
		"item_code": item_code,
		"warehouse":warehouse,
		"posting_date": nowdate(),
		"posting_time": nowtime()
                }
                last_entry = get_previous_sle(args)
                if last_entry:
                        res['posting_date'] = last_entry.get("posting_date")
                        res['posting_time'] = last_entry.get("posting_time")
        
        return res

@frappe.whitelist()
def get_customer(mobile_no):
        res=frappe._dict()
        sql = frappe.db.sql(""" SELECT EXISTS(SELECT * FROM `tabCustomer` where mobile_no = '{0}')""".format(mobile_no))
        result = sql[0][0]
        if result == 1:
                customer_detail = frappe.db.sql("""SELECT name,customer_name,customer_primary_contact,
                        mobile_no,email_id,primary_address,hub_manager FROM `tabCustomer` WHERE 
                        mobile_no = '{0}'""".format(mobile_no),as_dict=True)
                res['success_key'] = 1
                res['message'] = "success"
                res['customer'] = customer_detail
                return res        
        else:
                res["success_key"] = 0
                res['mobile_no'] = mobile_no
                res["message"] = "Mobile Number Does Not Exist"
                return res

@frappe.whitelist()
def get_all_customer(search=None, from_date=None):
    res=frappe._dict()
    customer = frappe.qb.DocType('Customer')
    if search:
        query = """SELECT name, customer_name, mobile_no, email_id
        FROM `tabCustomer`
        WHERE disabled = 0 AND mobile_no LIKE %s"""
        params = ("%"+search+"%",)
    else:
        query = """SELECT name, customer_name, mobile_no, email_id
        FROM `tabCustomer`
        WHERE disabled = 0 """
        params = ()
    if from_date:
        query += "AND modified >= %s"
        params += (from_date,)
    customer = frappe.db.sql(query, params, as_dict=1)
    if customer:
        res['success_key'] = 1
        res['message'] = "success"
        res['customer'] = customer
        return res
    else:
        res["success_key"] = 0
        res["message"] = "No customer found"
        res['customer']= customer
        return res


@frappe.whitelist()
def create_customer():
        customer_detail = frappe.request.data
        customer_detail = json.loads(customer_detail)
        res = frappe._dict()
        try:
                if customer_detail.get("mobile_no") and frappe.db.exists({"doctype":"Customer" , 'mobile_no': customer_detail.get("mobile_no") } ):
                                existing_customer = frappe.db.get_value("Customer", {"mobile_no": customer_detail.get("mobile_no")}, ["name", "customer_name", "mobile_no", "email_id"], as_dict=True)
                                res["success_key"] = 0
                                res["message"] = "Customer already present with this mobile no."
                                res["customer"] = existing_customer
                                return res
                else: 
                        customer = frappe.new_doc("Customer")
                        customer.customer_name = customer_detail.get("customer_name")
                        customer.mobile_no = customer_detail.get("mobile_no")
                        customer.email_id = customer_detail.get("email_id")
                        customer.customer_group = 'All Customer Groups'
                        customer.territory = 'All Territories'
                        customer.save(ignore_permissions=True)
                        frappe.db.commit()
                        res['success_key'] = 1
                        res['message'] = "success"
                        res["customer"] ={"name" : customer.name,
                                "customer_name": customer.customer_name,
                                "mobile_no" : customer.mobile_no,
                                "email_id":customer.email_id
                                }
                        return res

        except Exception as e:
                frappe.clear_messages()
                frappe.local.response["message"] ={
                        "success_key":0,
                        "message":"Invalid values please check your request parameters"  
                }
                
def get_sub_items(name):
        base_url = frappe.db.get_single_value('nbpos Setting', 'base_url')
        filters={'name': name ,  'base_url': base_url}
        sub_items = frappe.db.sql("""
                SELECT
                soi.item_code , soi.item_name, soi.qty,soi.uom , soi.rate , 
                soi.amount, soi.associated_item ,
                if((image = NULL or image = ''), "", 
                if(image LIKE 'http%%', image, concat(%(base_url)s, image))) as image
                FROM `tabSales Order` so , `tabSales Order Item` soi
                WHERE so.name = soi.parent and so.name = %(name)s
                """,values=filters ,  as_dict = True)
        if sub_items:
                return sub_items
        else:
                return ""

             
        
                
        

@frappe.whitelist()
def get_promo_code():
        res = frappe._dict() 
        coupon_code = frappe.qb.DocType('Coupon Code') 
        pricing_rule = frappe.qb.DocType('Pricing Rule')
        coupon_code =(
        frappe.qb.from_(coupon_code).inner_join(pricing_rule) .on(coupon_code.pricing_rule == pricing_rule.name) 
        .select(coupon_code.name , coupon_code.coupon_code, coupon_code.pricing_rule,
        coupon_code.maximum_use, coupon_code.used, coupon_code.description, 
        pricing_rule.valid_from , pricing_rule.valid_upto, pricing_rule.apply_on, 
        pricing_rule.price_or_product_discount, pricing_rule.min_qty,
        pricing_rule.max_qty, pricing_rule.min_amt, pricing_rule.max_amt, 
        pricing_rule.rate_or_discount, pricing_rule.apply_discount_on, 
        pricing_rule.discount_amount, pricing_rule.rate, pricing_rule.discount_percentage )
        .where( (pricing_rule.apply_on == 'Transaction') 
        & (pricing_rule.rate_or_discount == 'Discount Percentage') &
        (pricing_rule.apply_discount_on == 'Grand Total') & 
        (pricing_rule.price_or_product_discount == "Price")
        )
        ).run(as_dict=1)
        
        if coupon_code:
                res['success_key'] = 1
                res['message'] = "success"
                res['coupon_code'] = coupon_code
                return res
        else:
                res["success_key"] = 0
                res["message"] = "No Coupon Code in DB"
                res['coupon_code']= coupon_code
                return res


@frappe.whitelist(allow_guest=True)
def get_theme_settings():
    theme_settings = frappe.get_doc("Theme Settings")
    theme_settings_dict = {}
    theme = frappe.get_meta("Theme Settings")
    for field in theme.fields:
        if field.fieldtype == "Color":
            theme_settings_dict[field.fieldname] = theme_settings.get(field.fieldname)

    res = {
        "data": theme_settings_dict
    }
    return res

@frappe.whitelist()
def get_sales_taxes():
        taxes_data = frappe.db.sql("""
                SELECT
        stct.name AS name,stct.title AS title,stct.is_default AS is_default,stct.disabled AS disabled,stct.company AS company,stct.tax_category AS tax_category
                FROM `tabSales Taxes and Charges Template` AS stct 
        
                """, as_dict=1)

        tax = frappe.db.sql("""
        SELECT stct.name as name , stct.name as item_tax_template,
        stc.charge_type AS charge_type , stc.account_head AS tax_type , stc.description AS description , stc.cost_center AS cost_denter ,stc.rate as tax_rate, 
        stc.account_currency as account_currency , stc.tax_amount as tax_amount ,stc.total as total FROM `tabSales Taxes and Charges` AS stc INNER JOIN `tabSales Taxes and Charges Template`
        as stct ON
        stct.name=stc.parent 
        """, as_dict=1)
       
        for i in taxes_data:
                i['tax'] = [j for j in tax if i['name'] == j['name']]
        return taxes_data
