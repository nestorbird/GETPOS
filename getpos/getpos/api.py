
import requests
import frappe
import json
from frappe import _
import json
from frappe.utils import cint
STANDARD_USERS = ("Guest", "Administrator")
from frappe.utils.pdf import get_pdf
from frappe.rate_limiter import rate_limit
from frappe.utils.password import get_password_reset_limit
from frappe.utils import (cint,get_formatted_email, nowdate, nowtime, flt)
from erpnext.accounts.utils import get_balance_on
from erpnext.stock.utils import get_stock_balance
from erpnext.stock.stock_ledger import get_previous_sle, get_stock_ledger_entries
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
from frappe.utils import add_to_date, now
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
from datetime import datetime, timedelta, time
from erpnext.selling.doctype.customer.customer import get_customer_outstanding
from getpos.controllers import frappe_response,handle_exception




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
                        if(image LIKE 'http%%', image, concat(%(base_url)s, image))) as image ,loyalty_program
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
                sales_order = add_items_in_order(sales_order, order_list.get("items"), order_list)
                sales_order.status = order_list.get("status")
                sales_order.mode_of_payment = order_list.get("mode_of_payment")
                sales_order.mpesa_no = order_list.get("mpesa_no")
                sales_order.coupon_code = order_list.get("coupon_code")
                
                sales_order.save()
                sales_order.submit()

                res['success_key'] = 1
                res['message'] = "success"
                res["sales_order"] ={
                       "name" : sales_order.name,
                        "doc_status" : sales_order.docstatus
                        }
                if frappe.local.response.get("exc_type"):
                        del frappe.local.response["exc_type"]
                return res

        except Exception as e:
                if frappe.local.response.get("exc_type"):
                        del frappe.local.response["exc_type"]

                frappe.clear_messages()
                
                frappe.local.response["message"] ={
                "success_key":0,
                "message":e
                        }

def add_items_in_order(sales_order, items, order_list):
        sales_taxes = {}
        for item in items:
                item_tax_template = ""
                if item.get('tax'):
                        item_tax_template = item.get('tax')[0].get('item_tax_template')
                        for tax in item.get('tax'):
                                if sales_taxes.get(tax.get('tax_type')):
                                        sales_taxes[f"{tax.get('tax_type')}"] = flt(sales_taxes[f"{tax.get('tax_type')}"]) + tax.get('tax_amount')
                                else:
                                        sales_taxes.update({f"{tax.get('tax_type')}": tax.get('tax_amount')})

                sales_order.append("items", {
                        "item_code": item.get("item_code"),
                        "qty": item.get("qty"),
                        "rate": item.get("rate"), 
                        "discount_percentage":100 if item.get("rate")==0 else 0,  
                        "custom_parent_item":item.get("custom_parent_item"),
                        "custom_is_attribute_item":item.get("custom_is_attribute_item"),
                        "custom_is_combo_item":item.get("custom_is_combo_item"),
                        "allow_zero_evaluation_rate":item.get("allow_zero_evaluation_rate"),                    
                        "item_tax_template": item_tax_template if item_tax_template else "" ,
                        "custom_ca_id":item.get("custom_ca_id")                
                })

                # if item.get("sub_items"):
                #         for extra_item in item.get("sub_items"):
                #               if extra_item.get('tax'):
                #                      extra_item_tax_template = extra_item.get('tax')[0].get('item_tax_template')
                #               sales_order.append("items", {
                #                 "item_code": extra_item.get("item_code"),
                #                 "qty": extra_item.get("qty"),
                #                 "rate": extra_item.get("rate"),
                #                 "associated_item": item.get('item_code'),
                #                 "item_tax_template": extra_item_tax_template if extra_item_tax_template else "" 
                #                })
        
        for key,value in sales_taxes.items():
               sales_order.append("taxes", {"charge_type": "On Net Total", "account_head": key, "tax_amount": value, "description": key, })


        if order_list.get('tax'):
               for tax in order_list.get('tax'):
                        sales_order.append("taxes", {"charge_type": "On Net Total", "account_head": tax.get('tax_type'), "tax_amount": tax.get('tax_amount'),
                                                      "description": tax.get('tax_type'), "rate": tax.get('tax_rate')})
        
         

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
def get_sales_order_list(hub_manager = None, page_no = 1, from_date = None, to_date = nowdate() , mobile_no = None,name=None):
        res= frappe._dict()
        base_url = frappe.db.get_single_value('nbpos Setting', 'base_url')
        filters = {'hub_manager': hub_manager, 'base_url': base_url}
        sales_history_count = frappe.db.get_single_value('nbpos Setting', 'sales_history_count')
        limit = cint(sales_history_count)
        conditions = ""
        if mobile_no:
                conditions += f" and s.contact_mobile like '%{str(mobile_no).strip()}%'"
        if name:
                conditions += f" and s.customer_name like '%{str(name).strip()}%'"
        
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
                        s.hub_manager, s.creation, s.loyalty_points,s.loyalty_amount,s.discount_amount,
                        s.additional_discount_percentage as discount_percentage,
                        u.full_name as hub_manager_name,
                        if((c.image = null or c.image = ''), null, 
                        if(c.image LIKE 'http%%', c.image, concat({base_url}, c.image))) as image,
                        s.custom_return_order_status as return_order_status,
                        CASE WHEN s.coupon_code = null THEN '' ELSE (select coupon_type from `tabCoupon Code` co where co.name=s.coupon_code) END  as coupon_type,
                        CASE WHEN s.coupon_code = null THEN '' ELSE (select coupon_code from `tabCoupon Code` co where co.name=s.coupon_code) END  as coupon_code,
                        s.custom_gift_card_code as gift_card_code           
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
                tax_details = frappe.db.sql("""SELECT st.charge_type, st.account_head, st.tax_amount, st.description, st.rate 
                                   FROM `tabSales Order` s, `tabSales Taxes and Charges` st 
                                   WHERE st.parent = %s and st.parenttype = 'Sales Order' """,
                                   (item.name,), as_dict=True)
                item['tax_detail'] = tax_details
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
def get_customer(mobile_no=None, name=None):
    res = frappe._dict()
    sql = frappe.db.sql(
        """SELECT EXISTS(SELECT * FROM `tabCustomer` WHERE mobile_no = %s OR name = %s)""",
        (mobile_no, name)
    )
    result = sql[0][0]

    if result == 1:
        customer_detail = frappe.db.sql(
            """SELECT name, customer_name, customer_primary_contact, mobile_no, email_id,
            primary_address, hub_manager, loyalty_program FROM `tabCustomer`
            WHERE mobile_no = %s OR name = %s""",
            (mobile_no, name), as_dict=True
        )

        loyalty_point_details = frappe._dict(
            frappe.get_all(
                "Loyalty Point Entry",
                filters={
                    "customer": name,
                    "expiry_date": (">=", frappe.utils.getdate()),
                },
                group_by="company",
                fields=["company", "sum(loyalty_points) as loyalty_points"],
                as_list=1,
            )
        )
        companies = frappe.get_all(
            "Sales Invoice", filters={"docstatus": 1, "customer": name}, distinct=1, fields=["company"]
        )
        loyalty_points = 0
        for d in companies:
            if loyalty_point_details:
                loyalty_points = loyalty_point_details.get(d.company)

        conversion_factor = None
        if customer_detail:
            conversion_factor = frappe.db.get_value(
                "Loyalty Program", {"name": customer_detail[0].loyalty_program}, ["conversion_factor"], as_dict=True
            )

        # Credit limit and outstanding amount logic
        credit_limit = 0
        outstanding_amount = 0

        try:
            # Fetch the customer document
            customer = frappe.get_doc('Customer', customer_detail[0].name)
            credit_limit=customer.custom_credit_limit    
         

            # Fetch the total outstanding amount (total unpaid invoices)
           
            outstanding_amount =  get_customer_outstanding(
			name, frappe.get_doc("Global Defaults").default_company, ignore_outstanding_sales_order=False
		)

        except frappe.DoesNotExistError:
            message = _("Customer not found.")
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Error fetching credit limit"))
            message = _("An error occurred while fetching the credit limit.")

        res['success_key'] = 1
        res['message'] = "success"
        res['customer'] = customer_detail
        res['loyalty_points'] = loyalty_points
        res['conversion_factor'] = conversion_factor.conversion_factor if conversion_factor else 0
        res['loyalty_amount'] = loyalty_points * conversion_factor.conversion_factor if conversion_factor else 0
        res['credit_limit'] = credit_limit
        res['outstanding_amount'] = outstanding_amount
        return res
    else:
        res["success_key"] = 0
        res['mobile_no'] = mobile_no
        res["message"] = "Mobile Number/Customer Does Not Exist"
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
                        customer.custom_pos_shift = customer_detail.get("pos_opening_shift")
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

 
@frappe.whitelist(allow_guest=True)
def get_web_theme_settings():
    theme_settings = frappe.get_doc("Web Theme Settings")
    theme_settings_dict = {}
    theme = frappe.get_meta("Web Theme Settings")
    
    nbpos_setting = frappe.get_doc("nbpos Setting")
    instance_url = nbpos_setting.base_url

    image_fields = [
        "web_logo_image", 
        "web_banner_image", 
        "web_outlet_details_banner_image", 
        "web_footer_logo"
    ]
    
    for field in theme.fields:
        value = theme_settings.get(field.fieldname)
        
        if field.fieldname in image_fields and value:
            if not value.startswith(instance_url):
                value = f"{instance_url.rstrip('/')}/{value.lstrip('/')}"
        
        theme_settings_dict[field.fieldname] = value
    currency = frappe.get_doc("Global Defaults").default_currency
    currency_symbol=frappe.get_doc("Currency",currency).symbol
    theme_settings_dict['default_currency']=currency
    theme_settings_dict['currency_symbol']=currency_symbol    
    theme_settings_dict['default_company']=frappe.get_doc("Global Defaults").default_company    
    res = {
        "data": theme_settings_dict
    }
    return res

@frappe.whitelist(allow_guest=True)
def get_theme_settings():
    theme_settings = frappe.get_doc("Theme Settings")
    theme_settings_dict = {}
    theme = frappe.get_meta("Theme Settings")
    
    nbpos_setting = frappe.get_doc("nbpos Setting")
    instance_url = nbpos_setting.base_url

    image_fields = [
        "app_background_image", 
        "merchant_background_image", 
        "banner_image"
    ]
    
    for field in theme.fields:
        value = theme_settings.get(field.fieldname)
        
        if field.fieldname in image_fields and value:
            if not value.startswith(instance_url):
                value = f"{instance_url.rstrip('/')}/{value.lstrip('/')}"
        
        theme_settings_dict[field.fieldname] = value
    currency = frappe.get_doc("Global Defaults").default_currency
    currency_symbol=frappe.get_doc("Currency",currency).symbol
    theme_settings_dict['default_currency']=currency
    theme_settings_dict['currency_symbol']=currency_symbol    
    theme_settings_dict['default_company']=frappe.get_doc("Global Defaults").default_company
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


@frappe.whitelist()
def review_rating_order():
        review_order = frappe.request.data
        review_order = json.loads(review_order)
        review_order = review_order["review_order"]
        try:
                res = frappe._dict()
                sales_order = frappe.get_doc("Sales Order", review_order.get("name"))
                sales_order.custom_rating = review_order.get("rating")
                sales_order.custom_review = review_order.get("review")
                sales_order.save(ignore_permissions=True)
                sales_order.submit()
                
                res['success_key'] = 1
                res['message'] = "success"
                res["sales_order"] ={
                "name" : sales_order.name,
                "doc_status" : sales_order.docstatus
                }
                if frappe.local.response.get("exc_type"):
                        del frappe.local.response["exc_type"]
                return res

        except Exception as e:
                if frappe.local.response.get("exc_type"):
                        del frappe.local.response["exc_type"]

                frappe.clear_messages()
                frappe.local.response["message"] ={
                "success_key":0,
                "message":e
                        }

@frappe.whitelist()
def update_status(order_status):
        try:
                doc=frappe.get_doc("Kitchen-Kds",{"order_id":order_status.get('name')})
                doc.status= order_status.get('status')
                doc.save(ignore_permissions=True)

                send_order_ready_email(order_status)
                return {"success_key":1, "message": "success"}

        except Exception as e:
                return {"success_key":0, "message": e}

def send_order_ready_email(order_status):
        order = frappe.get_doc("Sales Order", order_status.get('name'))
        customer = frappe.get_doc("Customer", order.customer)
        cost_center =order.cost_center
        restaurant_name = frappe.db.get_value("Cost Center", cost_center, "cost_center_name")

        subject = "Your Order is Ready for Pickup"
        message = f"""
        Dear {customer.customer_name}, <br><br>

        Good news! Your order from {restaurant_name} is prepared and ready for pickup. <br><br>

        <b>Order ID</b>: {order.name} <br> <br>

        We look forward to serving you. <br> <br>

        Thank you for choosing {restaurant_name}! <br><br><br>

        Best regards, <br> <br>
        The {restaurant_name} Team<br><br>

        <b>Disclaimer</b>:
        Please note that email is auto generated and the inbox is unmonitored. For any cancellation requests or inquiries regarding your order, kindly contact the business directly.
        """
        frappe.sendmail(
                recipients=customer.email_id,
                subject=subject,
                message=message,
                now=True
        )


@frappe.whitelist(allow_guest=True)
def get_all_location_list():
       return frappe.db.sql("""
        SELECT DISTINCT custom_location 
        FROM `tabCost Center` 
        WHERE disabled=0 and custom_location IS NOT NULL
        ORDER BY custom_location ASC;
                """,as_dict=True)




@frappe.whitelist(allow_guest=True)
def get_kitchen_kds(status, cost_center=None):
    try:

        start_datetime = add_to_date(now(), hours=-24)
        end_datetime = now()

        start_datetime_str = str(start_datetime)
        end_datetime_str = str(end_datetime)

        cost_center_condition = ""
        if cost_center:
            cost_center_condition = "AND cost_center = %s"

        all_order = frappe.db.sql(f"""
            SELECT 
                name, 
                order_id, 
                custom_order_request, 
                status, 
                cost_center,                 
                estimated_time, 
                type, 
                CONCAT(creation1, ' ', time) AS creation1, 
                source
            FROM `tabKitchen-Kds`
            WHERE CONCAT(creation1, ' ', time) BETWEEN %s AND %s
            AND status = %s {cost_center_condition}
            ORDER BY CONCAT(creation1, ' ', time) DESC
        """, (start_datetime_str, end_datetime_str, status) + ((cost_center,) if cost_center else ()), as_dict=True)

        for orders in all_order:
            try:
               
                        
                orders['items'] =grouping_combo_attr(orders.order_id)

            except Exception as e:
                return {"message": str(e)}

        # frappe.publish_realtime('realtime_update', message=all_order)

        return all_order

    except Exception as e:
        return {"message": str(e)}


def grouping_combo_attr(order_id):
                query =  """
                                        SELECT 
                                        soi.item_code,
                                        soi.item_name,
                                        soi.custom_ca_id,
                                        soi.rate,
                                        soi.custom_is_combo_item,
                                        soi.custom_is_attribute_item,
                                        soi.custom_parent_item,
                                        soi.qty
                                        FROM 
                                        `tabSales Order Item` soi,`tabSales Order` s
                                        WHERE 
                                        soi.parent=s.name and 
                                        soi.parent = %s
                                        """

                items = frappe.db.sql(query, (order_id,), as_dict=True)
                                
                
                grouped_items = {}

                for item in items:
                        ca_id = item['custom_ca_id']
                        parent_item = item['custom_parent_item']
                        
                        if ca_id not in grouped_items:
                                grouped_items[ca_id] = []

                        if parent_item is None:

                                grouped_items[ca_id].append({
                                "item_code": item["item_code"],
                                "item_name": item["item_name"],
                                "custom_ca_id": item["custom_ca_id"],
                                'price':item['rate'],
                                "custom_is_combo_item": item["custom_is_combo_item"],
                                "custom_is_attribute_item": item["custom_is_attribute_item"],
                                "qty": item["qty"],
                                "child_items": []
                                })
                        
                for item in items:
                        ca_id = item['custom_ca_id']
                        parent_item = item['custom_parent_item']
                        if parent_item is not None:
                                for parent in grouped_items.get(ca_id, []):
                                        if parent["item_code"] == parent_item:
                                                parent["child_items"].append({
                                                "item_code": item["item_code"],
                                                "item_name": item["item_name"],
                                                'price':item['rate'],
                                                "custom_ca_id": item["custom_ca_id"],
                                                "custom_is_combo_item": item["custom_is_combo_item"],
                                                "custom_is_attribute_item": item["custom_is_attribute_item"],
                                                "custom_parent_item": item["custom_parent_item"],
                                                "qty": item["qty"]
                                                })


                output = []

                for items_list in grouped_items.values():
                        output.extend(items_list)
                        
                        
                return output


def after_request(whitelisted, response):
    try:
        kdsurl = frappe.db.get_single_value("Web Theme Settings", "kdsurl")
        if kdsurl:
            response.headers['Access-Control-Allow-Origin'] = kdsurl
        else:
                pass
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS,DELETE,PUT'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "CORS Middleware Error")
    
    return response               


def get_warehouse_for_cost_center(cost_center):
    warehouse = frappe.db.get_value('Warehouse', {'custom_cost_center': cost_center}, 'name')
    return warehouse


@frappe.whitelist(allow_guest=True)
def create_sales_order_kiosk():
    order_list = frappe.request.data
    order_list = json.loads(order_list)
    order_list = order_list["order_list"]
    
    try:
        frappe.set_user("Administrator")
        res = frappe._dict()
        sales_order = frappe.new_doc("Sales Order")
        sales_order.hub_manager = order_list.get("hub_manager")
        sales_order.custom_source = order_list.get("source")
        sales_order.ward = order_list.get("ward")
        sales_order.custom_order_request = order_list.get("order_request")
        
        if order_list.get("source") == "WEB":
            phone_no = frappe.db.sql("""SELECT phone FROM `tabContact Phone` WHERE phone = %s """, (order_list.get('mobile')))
            if phone_no:
                parent = frappe.db.get_value('Contact Phone', {'phone': order_list.get('mobile')}, 'parent')
                customer = frappe.db.get_value('Dynamic Link', {'parent': parent, 'link_doctype': 'Customer'}, 'link_name')
                if customer:
                    sales_order.customer = customer
            else:
                new_customer = frappe.new_doc("Customer")
                new_customer.customer_name = order_list.get("name")
                new_customer.customer_group = "Individual"
                new_customer.territory = "All Territories"
                new_customer.email_id = order_list.get("email")
                new_customer.mobile_no = order_list.get("mobile")
                new_customer.insert(ignore_permissions=True)
                sales_order.customer = new_customer.name
        else:
            sales_order.customer = order_list.get("customer")
        
        arr = order_list.get("transaction_date").split(" ")
        sales_order.transaction_date = arr[0]
        sales_order.delivery_date = order_list.get("delivery_date")
        sales_order = add_items_in_order(sales_order, order_list.get("items"), order_list)
        sales_order.status = order_list.get("status")
        sales_order.mode_of_payment = order_list.get("mode_of_payment")
        sales_order.mpesa_no = order_list.get("mpesa_no")
        if order_list.get("coupon_code"):
                coupon_name = frappe.db.get_value("Coupon Code", {"coupon_code": order_list.get("coupon_code")},"name")
                sales_order.coupon_code = coupon_name
        if order_list.get("gift_card_code"):
                sales_order.custom_gift_card_code = order_list.get("gift_card_code")
                sales_order.apply_discount_on="Grand Total"
                sales_order.discount_amount=order_list.get("discount_amount")

        sales_order.disable_rounded_total = 1
        cost_center = order_list.get("cost_center")
        
       
        # Set custom payment status
        if order_list.get("mode_of_payment") == "Card":
            sales_order.custom_payment_status = "Pending"
        else:
            sales_order.custom_payment_status = "Paid"
        
        # Set cost center and warehouse
        sales_order.cost_center = order_list.get("cost_center")
        warehouse = get_warehouse_for_cost_center(order_list.get("cost_center"))
        if warehouse:
            sales_order.set_warehouse = warehouse
        if order_list.get("redeem_loyalty_points") == 1 :
               sales_order.custom_redeem_loyalty_points = 1
               sales_order.loyalty_points = order_list.get("loyalty_points")
               sales_order.loyalty_amount = order_list.get("loyalty_amount")               
               sales_order.custom_redemption_account = order_list.get("loyalty_redemption_account")   
        if order_list.get("loyalty_program") :
               sales_order.custom_loyalty_program = order_list.get("loyalty_program")        
        if order_list.get("pos_opening_shift") :              
               sales_order.custom_pos_shift=order_list.get("pos_opening_shift")

        sales_order.save(ignore_permissions=True)
        sales_order.rounded_total=sales_order.grand_total
        if order_list.get("redeem_loyalty_points") == 1 :
               sales_order.outstanding_amount=sales_order.grand_total-sales_order.loyalty_amount

        sales_order.submit()               
        # if order_list.get("gift_card_code"):
        #         frappe.db.sql("""
        #                 UPDATE `tabSales Order`
        #                 SET `grand_total` = %s,
        #                 `discount_amount`=%s,
        #                 `net_total`=%s
        #                 WHERE name = %s
        #         """, (sales_order.grand_total -float(order_list.get("discount_amount")) ,float(order_list.get("discount_amount")),sales_order.net_total -float(order_list.get("discount_amount")), sales_order.name))           
                  
        create_sales_invoice_from_sales_order(sales_order,order_list.get("gift_card_code"),order_list.get("discount_amount"))

        latest_order = frappe.get_doc('Sales Order', sales_order.name)

        times = [item.get("estimated_time") for item in order_list.get("items")]
        times = [time if time is not None else 0 for time in times]
        max_time = max(times)

        if order_list.get("source") != "WEB":
            kds=frappe.get_doc({
                "doctype": "Kitchen-Kds",
                "order_id": latest_order.get('name'),
                "type": order_list.get("type"),
                "estimated_time": max_time,
                "status": "Open",
                "creation1": now(),
                "custom_order_request": order_list.get('order_request'),
                "source": order_list.get('source'),
                "cost_center": order_list.get("cost_center")
            })
            kds.insert(ignore_permissions=1)


        res['success_key'] = 1
        res['message'] = "success"
        res["sales_order"] = {
            "name": sales_order.name,
            "doc_status": sales_order.docstatus
        }

        if frappe.local.response.get("exc_type"):
            del frappe.local.response["exc_type"]
        
        return res

    except Exception as e:
        if frappe.local.response.get("exc_type"):
            del frappe.local.response["exc_type"]

        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success_key": 0,
            "message": str(e)
        }

@frappe.whitelist(methods="POST")
def create_web_sales_invoice():
    import json
    data = frappe.request.data
    data = json.loads(data)
    data = data["message"]
    try:
        frappe.set_user("Administrator")
        res = frappe._dict()
        if data.get('status') == "F":
                doc = frappe.get_doc("Sales Order", data.get('order_id'))
                total_time=[]
                sales_order_items = frappe.db.get_all('Sales Order Item', filters={'parent': doc.name}, fields=['item_code'])
                for item in sales_order_items:
                        time = frappe.get_value("Item", {"item_code": item.get('item_code')}, 'custom_estimated_time')
                        total_time.append(time)
                max_time = max(total_time)

                sales_invoice = make_sales_invoice(doc.name)
                sales_invoice.posting_date = doc.transaction_date
                sales_invoice.posting_time = doc.transaction_time
                sales_invoice.due_date = data.get('transaction_date')
                sales_invoice.update_stock = 1
                sales_invoice.save(ignore_permissions=1)
                sales_invoice.submit()

                frappe.get_doc({
                    "doctype": "Kitchen-Kds",
                    "order_id": doc.name,
                    "type": "Takeaway",   
                    "estimated_time": max_time, 
                    "status": "Open",
                    "creation1": data.get('transaction_date'),
                    "custom_order_request": doc.custom_order_request,
                    "source": "WEB"
                }).insert(ignore_permissions=1)

                res['success_key'] = 1
                res['message'] = "success"
                res["sales_order"] = {
                    "name": sales_invoice.name,
                    "doc_status": sales_invoice.docstatus
                }

                if frappe.local.response.get("exc_type"):
                    del frappe.local.response["exc_type"]

                return res
 
    except Exception as e:
        if frappe.local.response.get("exc_type"):
            del frappe.local.response["exc_type"]

        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success_key": 0,
            "message": str(e)
        }

@frappe.whitelist()
def get_sales_order_item_details(order_id=None):
    try:
        if order_id:
                doc = frappe.get_doc("Sales Order", order_id)
                address = frappe.db.sql("""
                SELECT CONCAT(cost_center_name, ", ", custom_address, ", ", custom_location) as address 
                FROM `tabCost Center`
                WHERE name = %s
                """, (doc.cost_center,), as_dict=True)

                item_list = grouping_combo_attr(order_id)
                data = {}
                max_time = []
                for item in doc.items:
                    estimated_time =frappe.db.get_value("Item", {"item_code" : item.item_code}, 'custom_estimated_time')
                    max_time.append(estimated_time)


                data["order_request"] = doc.custom_order_request
                data["item_details"] = item_list
                if address:
                        data['address'] = address[0]['address']
                data["estimated_time"] = max(max_time)
                return data

    except Exception as e:
        if frappe.local.response.get("exc_type"):
            del frappe.local.response["exc_type"]

        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success_key": 0,
            "message": str(e)
        }


                
@frappe.whitelist(methods="POST")
def payment_request(payment_list={}):
        try:
                auth_url = f'{payment_list.get("auth_token_url")}/connect/token'
                post_data = {
                "grant_type": "client_credentials",
                "client_id": payment_list.get("client_id"),
                "client_secret":payment_list.get("client_secret")
                }
                response = requests.post(auth_url, data=post_data)
                o_auth_authentication_response = response.json()

                api_client = requests.Session()
                base_address = payment_list.get("base_payment_url")
                api = "/checkout/v2/isv/orders?merchantid=" 
                merchantId=  payment_list.get("merchant_id")            
                api_client.headers.update({
                "Accept": "application/json",
                "Authorization": f"Bearer {o_auth_authentication_response['access_token']}"
                })


                customer = {
                        "Email":  payment_list.get("customer_email"),
                        "FullName": payment_list.get("customer_name"),
                        "Phone": payment_list.get("customer_phone"),
                        "CountryCode":  payment_list.get("country_code"),
                        "RequestLang":  payment_list.get("request_lang")
                }
                isvamount= payment_list.get("amount") * payment_list.get("isv_percentage") / 100
                request = {
                        "Amount": payment_list.get("amount"),
                        "CustomerTrns": payment_list.get("customer_trans"),
                        "Customer": customer,
                        "PaymentTimeout": 300,
                        "Preauth": False,
                        "AllowRecurring": False,
                        "MaxInstallments": 12,
                        "PaymentNotification": True,
                        "TipAmount": 0,
                        "DisableExactAmount": False,
                        "DisableWallet": True,
                        "SourceCode": payment_list.get("source_code"),
                        "isvamount": isvamount
                }
                post_request_data = json.dumps(request)
                content_data = post_request_data.encode('utf-8')
                headers = {'Content-Type': 'application/json'}

                api_response = api_client.post(f"{base_address}{api}{merchantId}", data=content_data, headers=headers)

                viva_wallet_order_response = api_response.json()
                
                if api_response.status_code == 200:
                        # post_process_payment_request['Order']['OrderCode'] = viva_wallet_order_response['OrderCode']
                        # await _order_service.update_order_async(post_process_payment_request['Order'])
                        redirect_url = f'{payment_list.get("checkout_url")}/web/checkout?ref={viva_wallet_order_response["orderCode"]}'
                return redirect_url
        except Exception as e:
                if frappe.local.response.get("exc_type"):
                        del frappe.local.response["exc_type"]

                frappe.clear_messages()
                
                frappe.local.response["message"] ={
                "success_key":0,
                "message":e
                        }




@frappe.whitelist()
def transaction_status(payment_list={}, transaction_id=None, merchant_id=None):
    try:
        auth_url = f'{payment_list.get("auth_token_url")}/connect/token'
        post_data = {
            "grant_type": "client_credentials",
            "client_id": payment_list.get("client_id"),
            "client_secret": payment_list.get("client_secret")
        }
        
        response = requests.post(auth_url, data=post_data)
        response.raise_for_status() 
        o_auth_authentication_response = response.json()
        api_client = requests.Session()
        base_address = payment_list.get("base_payment_url")
        api_client.headers.update({
            "Accept": "application/json",
            "Authorization": f"Bearer {o_auth_authentication_response['access_token']}"
        })

        api_url = f"{base_address}/checkout/v2/isv/transactions/{transaction_id}?merchantId={merchant_id}"
        
        api_response = api_client.get(api_url)

        if api_response.status_code == 200:
            transaction_response = api_response.json()
            return transaction_response
        else:
            return {
                "success_key": 0,
                "message": f"Failed to retrieve transaction status. Status code: {api_response.status_code}, Response: {api_response.text}"
            }

    except Exception as e:
        return {
            "success_key": 0,
            "message": str(e)
        }


@frappe.whitelist()
def update_payment_status(update_paymentstatus):
        try:
                frappe.db.set_value("Sales Order", {"name":update_paymentstatus.get('order_id')}, {'custom_payment_status': update_paymentstatus.get('paymentstatus')
                })

                return {"success_key":1, "message": "success"}

        except Exception as e:
                return {"success_key":0, "message": e}
        

@frappe.whitelist(allow_guest=True)
def get_filters():
        filters = frappe.db.sql(''' Select 
        it.item_type
        from `tabItem Type` it
        ''', as_dict = True)
     
        return filters



@frappe.whitelist(allow_guest=True)
def get_location():
    body = frappe.local.form_dict
    if body.get("search_location"):
        filter_condition = f'%{body.get("search_location")}%'
        return frappe.db.sql("""
            SELECT DISTINCT custom_location
            FROM `tabCost Center` WHERE disabled=0 and custom_location LIKE %s
            ORDER BY custom_location ASC;
            """, (filter_condition,) ,as_dict=1)


    elif (body.get("custom_location")):
        base_url = frappe.db.get_single_value('nbpos Setting', 'base_url')
        return frappe.db.sql("""
                SELECT custom_location, custom_address, cost_center_name, name,
                CONCAT(%(base_url)s, custom_attach_image) AS custom_attach_image,
                CONCAT(%(base_url)s, custom_web_outlet_details_banner_image) AS web_outlet_details_banner_image
                FROM `tabCost Center`
                WHERE disabled = 0 AND custom_location = %(custom_location)s
                ORDER BY creation DESC
                """, {
                    'base_url': base_url,
                    'custom_location': body.get("custom_location")
                }, as_dict=1)


    else:
        return frappe.db.sql("""
            SELECT Distinct(custom_location)
            FROM `tabCost Center` WHERE custom_location is NOT NULL and disabled=0
            ORDER BY custom_location ASC;
            """,as_dict=1)



@frappe.whitelist(allow_guest=True)
def get_cost_center_by_pin():  
        body = frappe.local.form_dict
        pin = body.get("custom_pin")
        cost_center = body.get("cost_center")
        
        if not pin or not cost_center:
                missing_param = "custom_pin" if not pin else "cost_center"
                return frappe_response(400, f"{missing_param} is missing")

        custom_pin = frappe.db.get_value("Cost Center",cost_center,'custom_pin')
        if int(custom_pin) == int(pin):
                return frappe_response(200, {"is_verified": True})
        
        else:
                return frappe_response(200, {"is_verified": False})
                

@frappe.whitelist(methods="POST")
def return_sales_order(sales_invoice):
    try:
        frappe.set_user("Administrator")
        res = frappe._dict()
        # Fetch the sales invoice number
        sales_order_number = sales_invoice.get("sales_order_number")
        sales_invoice_doc = frappe.db.get_value("Sales Invoice Item",
                                                filters={"sales_order": sales_order_number},
                                                fieldname=["parent"])
        if sales_invoice_doc:
            invoice = frappe.get_doc("Sales Invoice", sales_invoice_doc)
            return_order_items = sales_invoice.get("return_items")
            # Update invoice fields for return
            invoice.is_return = 1
            invoice.update_outstanding_for_self = 1
            invoice.return_against = sales_invoice_doc
            invoice.update_billed_amount_in_delivery_note = 1
            invoice.total_qty = -sales_invoice.get("total_qty")
            invoice.mode_of_payment = ''
            invoice.redeem_loyalty_points = 0
            invoice.loyalty_points = 0
            invoice.loyalty_amount = 0
            invoice.loyalty_program = ''
            invoice.loyalty_redemption_account = ''            
            invoice.coupon_code=''
            invoice.discount_amount=-invoice.discount_amount
            returned_items = []
            # Adjust quantities for returned items
            for item in invoice.items:
                if return_order_items.get(item.item_code, 0) > 0:
                    item.qty = -return_order_items[item.item_code]
                    item.stock_qty = -return_order_items[item.item_code]
                    returned_items.append(item)
            invoice.items = returned_items
            invoice.insert(ignore_permissions=1)
            # Update sales order custom status
            frappe.db.sql("""
                UPDATE `tabSales Order`
                SET `custom_return_order_status` = %s
                WHERE name = %s
            """, (sales_invoice.get("return_type"), sales_order_number))
            res["success_key"] = 1
            res["message"] = "Success"
            res['invoice'] = invoice.name
            res['amount'] = invoice.grand_total
            try:
                # Send email to customer with the sales invoice return attached
                send_credit_note_email(invoice)  
            except Exception as e:
                   pass            
            return res
        else:
            res["success_key"] = 0
            res["message"] = "Sales invoice not found for this order."
            res['invoice'] = ""
            res['amount'] = 0
            return res
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "return_sales_order Error")
        return {"success_key": 0, "message": "An unexpected error occurred. Please try again later.", "invoice": "", "amount": 0}
    
@frappe.whitelist()
def edit_customer():
        customer_detail = frappe.request.data
        customer_detail = json.loads(customer_detail)
        frappe.set_user("Administrator")
        res = frappe._dict()
        existing_customer = frappe.db.get_value("Customer", {"mobile_no": customer_detail.get("mobile_no")}, ["name", "customer_name", "mobile_no", "email_id"], as_dict=True)
        if existing_customer and existing_customer.name !=customer_detail.get("name") :                
                res["success_key"] = 0
                res["message"] = "Customer already present with this mobile no."
                res["customer"] = existing_customer
                return res 
        else:
                update_customer = frappe.get_doc("Customer",customer_detail.get("name"))
                frappe.db.sql("update `tabContact` set `mobile_no` =%s  where name=%s",(customer_detail.get("mobile_no"), update_customer.customer_primary_contact))
                update_customer.customer_name = customer_detail.get("customer_name")  
                update_customer.mobile_no = customer_detail.get("mobile_no")  
                if customer_detail.get("email_id"):
                                frappe.db.sql("update `tabContact` set `email_id` =%s  where name=%s",(customer_detail.get("email_id"), update_customer.customer_primary_contact))
                                update_customer.email_id=customer_detail.get("email_id")
                update_customer.save(ignore_permissions=True)                
                res['success_key'] = 1
                res['message'] = "Customer updated successfully"
                res["customer"] ={"name" : customer_detail.get("name") ,
                                "customer_name": customer_detail.get("customer_name") ,
                                "mobile_no" : customer_detail.get("mobile_no") ,
                                "email_id" : customer_detail.get("email_id") 
                                }
                return res


@frappe.whitelist()
def coupon_code_details():
    current_date = datetime.now().date()
    def get_details(entity, fields):
        return {field:entity.get(field) for field in fields}
    def fetch_coupon_and_pricing_rule(coupon_code):
        # Fetch details related to the coupon and its associated pricing rule
        coupon = frappe.db.get_value("Coupon Code", {"coupon_code": coupon_code},
                                     ["name", "used", "maximum_use", "valid_from", "valid_upto", "pricing_rule","description"], as_dict=True)
        if not coupon:
            return None, {"status": "error", "message": _("Coupon code does not exist.")}
        pricing_rule = frappe.get_doc("Pricing Rule", coupon.get("pricing_rule"))
        if not pricing_rule:
            return None, {"status": "error", "message": _("Pricing rule associated with coupon not found.")}
        return coupon, pricing_rule
    pricing_rule_fields = [
        # List of fields to fetch from Pricing Rule document
        "name", "title", "apply_on", "price_or_product_discount", "coupon_code_based", "selling", "buying",
        "applicable_for", "customer", "min_qty", "max_qty", "min_amt", "max_amt", "valid_from", "company",
        "currency", "rate_or_discount", "apply_discount_on", "rate", "discount_amount", "discount_percentage",
        "for_price_list", "doctype", "items", "item_groups", "customers", "customer_groups", "territories"
    ]   
    # Fetch all valid coupons based on current date and their respective pricing rules
    coupons = frappe.db.get_all("Coupon Code", filters={"valid_upto": (">=", current_date),"coupon_type": "Promotional"},
                                fields=["name", "coupon_code", "used", "maximum_use", "valid_from", "valid_upto", "pricing_rule","description"])
    valid_coupons = []
    for coupon in coupons:
        pricing_rule = frappe.get_doc("Pricing Rule", coupon.get("pricing_rule"))
        if coupon["description"] :
                coupon["description"]=frappe.utils.strip_html_tags(coupon["description"])
        # Check if the pricing rule is valid, coupon usage is within limit
        if pricing_rule and is_valid_pricing_rule(pricing_rule, current_date) and coupon["used"] < coupon["maximum_use"]:
            valid_coupons.append({
                **get_details(coupon, ["name","coupon_code", "used", "maximum_use", "valid_from", "valid_upto","description"]),
                "pricing_rule": get_details(pricing_rule, pricing_rule_fields)
            })
           
    # Return success status with valid coupons list
    return {"status": "success", "valid_coupons": valid_coupons}

@frappe.whitelist(methods=["POST"])
def validate_coupon_code(coupon_code=None):
    current_date = datetime.now().date()
    def get_details(entity, fields):
        return {field: entity.get(field) for field in fields}
    def fetch_coupon_and_pricing_rule(coupon_code):
        # Fetch details related to the coupon and its associated pricing rule
        coupon = frappe.db.get_value("Coupon Code", {"coupon_code": coupon_code},
                                     ["name", "used", "maximum_use", "valid_from", "valid_upto", "pricing_rule"], as_dict=True)
        if not coupon:
            return None, {"status": "error", "message": _("Coupon code does not exist.")}
        pricing_rule = frappe.get_doc("Pricing Rule", coupon.get("pricing_rule"))
        if not pricing_rule:
            return None, {"status": "error", "message": _("Pricing rule associated with coupon not found.")}
        return coupon, pricing_rule
    pricing_rule_fields = [
        # List of fields to fetch from Pricing Rule document
        "name", "title", "apply_on", "price_or_product_discount", "coupon_code_based", "selling", "buying",
        "applicable_for", "customer", "min_qty", "max_qty", "min_amt", "max_amt", "valid_from", "company",
        "currency", "rate_or_discount", "apply_discount_on", "rate", "discount_amount", "discount_percentage",
        "for_price_list", "doctype", "items", "item_groups", "customers", "customer_groups", "territories"
    ]
    if coupon_code:
        coupon, pricing_rule = fetch_coupon_and_pricing_rule(coupon_code)
        if not coupon:
            return pricing_rule
        # Validate if the pricing rule associated with the coupon is valid
        if not is_valid_pricing_rule(pricing_rule, current_date):
            return {"status": "invalid", "message": _("Associated pricing rule is invalid.")}
        # Check if the coupon has exceeded its maximum usage limit
        if coupon["used"] >= coupon["maximum_use"]:
            return {"status": "invalid", "message": _("Coupon code has reached its maximum use limit.")}
        # Return valid status with coupon and pricing rule details
        return {
            "status": "valid",
            "message": _("Coupon code and associated pricing rule are valid."),
            "coupon": {
                **get_details(coupon, ["name", "used", "maximum_use", "valid_from", "valid_upto"]),
                "pricing_rule": get_details(pricing_rule, pricing_rule_fields)
            }
        }
    # If no coupon code provided, return an error message
    return {"status": "error", "message": _("Coupon code is required.")}

def is_valid_pricing_rule(pricing_rule, current_date):
    def parse_date(date_str):
        return datetime.strptime(date_str, "%Y-%m-%d").date() if isinstance(date_str, str) else date_str
    # Parse valid_from and valid_upto dates from the pricing rule
    rule_valid_from = parse_date(pricing_rule.get("valid_from"))
    rule_valid_upto = parse_date(pricing_rule.get("valid_upto"))
    # Check if the current date falls within the valid range of the pricing rule
    return (not rule_valid_from or current_date >= rule_valid_from) and (not rule_valid_upto or current_date <= rule_valid_upto)

def send_credit_note_email(invoice):
        customer = frappe.get_doc("Customer", invoice.customer)
        contact_doc = frappe.get_doc("Contact", customer.customer_primary_contact)
        email = contact_doc.email_id
        subject = "Credit Note: {}".format(invoice.name)
        message = "Please find attached the Credit Note {}.".format(invoice.name)
        # Use Frappe's PDF generation tool to create the PDF
        pdf_content = frappe.utils.pdf.get_pdf(frappe.render_template(
            'getpos/templates/pages/credit_note_email.html', {"doc": invoice}
        ))
        attachments = [{
            "fname": "Credit_Note_{}.pdf".format(invoice.name.replace(" ", "_")),
            "fcontent": pdf_content
        }]
        frappe.sendmail(
            recipients=email,
            subject=subject,
            message=message,
            attachments=attachments,
            now=True
        )

@frappe.whitelist()
def get_shift_transaction(pos_opening_shift):
    data = {}

    pos_opening_shift_doc = frappe.get_doc("POS Opening Shift", pos_opening_shift)
    amt = sum(i.get('amount') for i in pos_opening_shift_doc.balance_details)

    sales_orders = frappe.get_all(
        "Sales Order",
        filters={
            "custom_pos_shift": pos_opening_shift,
            "docstatus": 1
        },
        fields=["name", "customer", "grand_total", "status"]
    )

    customers = {order.customer for order in sales_orders}
    customer_first_order_dates = frappe.get_all(
        "Sales Order",
        filters={
            "customer": ["in", list(customers)],
            "docstatus": 1
        },
        fields=["customer", "min(creation) as first_order_date"],
        group_by="customer"
    )
    
    customer_first_order_dates = {entry.customer: entry.first_order_date for entry in customer_first_order_dates}

    old_customers = set()
    new_customers = set()
    sales_order_amount = 0
    return_order_amount = 0
    num_transactions = 0
    cash_collected = 0

    for order in sales_orders:
        amount = order.grand_total

        if order.status == "Return":
            return_order_amount += amount
        else:
            sales_order_amount += amount

        num_transactions += 1
        cash_collected += amount

        # Check if the customer is new or old
        if customer_first_order_dates[order.customer] == order.creation:
            new_customers.add(order.customer)
        else:
            old_customers.add(order.customer)

    data["opening_amount"] = amt
    data["old_customers"] = list(old_customers)
    data["new_customers"] = list(new_customers)
    data["sales_order_amount"] = sales_order_amount
    data["return_order_amount"] = return_order_amount
    data["num_transactions"] = num_transactions
    data["cash_collected"] = cash_collected

    return data

@frappe.whitelist()
def resend_sales_invoice_email(sales_order):
    res={}
    sales_invoice_doc = frappe.db.get_value("Sales Invoice Item",
                                                filters={"sales_order": sales_order},
                                                fieldname=["parent"])
    if sales_invoice_doc:
        sales_invoice = frappe.get_doc("Sales Invoice", sales_invoice_doc)        
        recipient = sales_invoice.contact_email
        # Check if the recipient email is present
        if recipient:
                # Generate PDF content
                pdf_content = get_sales_invoice_pdf(sales_invoice)
                # Prepare the email content
                email_subject = f"Sales Invoice {sales_invoice}"
                email_message = f"Dear {sales_invoice.customer_name},\n\nPlease find attached your sales invoice.\n\nBest regards,\nYour Company Name"
                # Create an attachment
                attachment = {
                        'fname': f"{sales_order}.pdf",
                        'fcontent': pdf_content
                }
                try:
                        # Send the email
                        make(
                                recipients=[recipient],
                                subject=email_subject,
                                content=email_message,
                                attachments=[attachment],
                                send_email=True
                        )
                        res["success_key"]=1
                        return res
                except Exception as e:
                        res["success_key"]=0
                        res['message'] = "Unable to send mail."    
                        return res
        else:
              res["success_key"]=0
              res['message'] = "Email not found."    
              return res
    else:
          res["success_key"]=0
          res['message'] = "Invoice not found."    
          return res

def get_sales_invoice_pdf(sales_invoice):
    html = frappe.render_template('getpos/templates/pages/sales_invoice_email.html', context={'doc': sales_invoice})
    pdf_content = get_pdf(html)
    return pdf_content

@frappe.whitelist(methods=["POST"])
def validate_gift_card(gift_card):   
        frappe.set_user("Administrator")
        res = frappe._dict()
        current_date = datetime.now().date()
        gift_card_details = frappe.db.get_all("Gift Card", filters={"valid_upto": (">=", current_date),"code": gift_card.get("code"),"customer":gift_card.get("customer")},
                                        fields=["gift_card_name", "discount_amount", "amount_balance", "valid_from", "valid_upto", "description"])
        if gift_card_details:
                if gift_card_details[0].amount_balance > 0:
                        res['success_key'] = 1
                        res['message'] = "success"
                        res['gift_card']=gift_card_details
                else:
                        res['success_key'] = 1
                        res['message'] = "Code is invalid"    
        else:
                res['success_key'] = 1
                res['message'] = "Code is invalid"    
        return res

def create_sales_invoice_from_sales_order(doc,gift_card_code,discount_amount):
    if (doc.custom_source == "WEB"):
        pass
    else:
        sales_invoice = make_sales_invoice(doc.name)
        sales_invoice.posting_date = doc.transaction_date
        sales_invoice.posting_time = doc.transaction_time
        sales_invoice.due_date = doc.transaction_date        
        sales_invoice.update_stock = 1
        if doc.custom_redeem_loyalty_points:
            sales_invoice.redeem_loyalty_points = doc.custom_redeem_loyalty_points
            sales_invoice.loyalty_points = doc.loyalty_points
            sales_invoice.loyalty_amount = doc.loyalty_amount
            sales_invoice.loyalty_program = doc.custom_loyalty_program
            sales_invoice.loyalty_redemption_account = doc.custom_redemption_account
        if doc.coupon_code:
            sales_invoice.coupon_code=doc.coupon_code
        if doc.custom_gift_card_code:
            sales_invoice.discount_amount=doc.discount_amount
            sales_invoice.apply_discount_on="Grand Total"
            sales_invoice.grand_total=sales_invoice.grand_total -float(discount_amount)
        sales_invoice.save(ignore_permissions=1)
        sales_invoice.submit()
        if doc.custom_gift_card_code:
                company_name = frappe.get_doc("Global Defaults").default_company
                company=frappe.get_doc("Company",company_name)             
                journal_entry = frappe.new_doc("Journal Entry")
                journal_entry.voucher_type="Journal Entry"
                journal_entry.company=company.name
                journal_entry.posting_date=frappe.utils.getdate()	
                journal_entry.user_remark="customer redeemed the gift card in partial amount that is for $" + str(discount_amount) + " for the purchase of the good"		
                journal_entry.append(
                        "accounts",
                        {
                        'account': "Gift card Revenue - " + company.abbr,
                        'debit_in_account_currency': float(discount_amount),
                        'credit_in_account_currency': float(0),
                        # 'reference_type':"Sales Invoice",
                        # 'reference_name':sales_invoice.name,
                        'party_type':'Customer',
                        'party':doc.customer
                        })
                journal_entry.append(
                        "accounts",
                        {
                        'account': "Sales - " + company.abbr,
                        'debit_in_account_currency': float(0),
                        'credit_in_account_currency':float(discount_amount),
                        # 'reference_type':"Sales Invoice",
                        # 'reference_name':sales_invoice.name,
                        'party_type':'Customer',
                        'party':doc.customer
                })	
                journal_entry.save(ignore_permissions=True)
                journal_entry.submit() 
                gift_card_doc=frappe.db.get_value("Gift Card", {"code": gift_card_code}, ["name", "amount_balance", "amount_used"], as_dict=True)  
                frappe.set_value('Gift Card', gift_card_doc.name, 'amount_balance', gift_card_doc.amount_balance - float(discount_amount))            
                frappe.set_value('Gift Card', gift_card_doc.name, 'amount_used', gift_card_doc.amount_used + float(discount_amount))  
        # if gift_card_code:
        #         frappe.db.sql("""
        #                 UPDATE `tabSales Invoice`
        #                 SET `grand_total` = %s,
        #                 `discount_amount`=%s,
        #                 `net_total`=%s,
        #                 `outstanding_amount`=%s
        #                 WHERE name = %s
        #         """, (sales_invoice.grand_total -float(discount_amount),discount_amount,sales_invoice.net_total - float(discount_amount),sales_invoice.outstanding_amount -float(discount_amount), sales_invoice.name))           
        grand_total=frappe.db.get_value('Sales Invoice', {'name': sales_invoice.name}, 'grand_total')
        if grand_total > 0:
              create_payment_entry(sales_invoice) 
        else:
              frappe.db.sql("""
                        UPDATE `tabSales Invoice`
                        SET `status` = %s                        
                        WHERE name = %s
                """, ("Paid",sales_invoice.name))      
                           
        # if gift_card_code and float(sales_invoice.grand_total) -float(discount_amount) > 0:
        #       create_payment_entry(sales_invoice)
        # elif doc.coupon_code and sales_invoice.grand_total > 0:
        #       create_payment_entry(sales_invoice)
        # else:
        #       create_payment_entry(sales_invoice) 

        resend_sales_invoice_email(doc.name)

def create_payment_entry(doc):
    if doc.mode_of_payment != 'Credit':
        payment_entry = get_payment_entry("Sales Invoice", doc.name)
        payment_entry.posting_date = doc.posting_date
        payment_entry.mode_of_payment = doc.mode_of_payment
        if doc.mode_of_payment == 'Cash':
                account = frappe.db.get_value('Account', 
                        {
                                'disabled': 0,
                                'account_type': 'Cash',
                                'account_name': 'Cash'
                        },
                        'name')
                payment_entry.paid_to = account
        if doc.mode_of_payment == 'M-Pesa':
                payment_entry.reference_no = doc.mpesa_no
                payment_entry.reference_date = doc.posting_date
        payment_entry.save()
        payment_entry.submit()


@frappe.whitelist()
def clear_demo_data():
        res = frappe._dict()
        company = frappe.db.get_single_value("Global Defaults", "demo_company")
        try:
                tdr = frappe.new_doc("Transaction Deletion Record")
                tdr.company=company
                tdr.process_in_single_transaction = True
                tdr.save(ignore_permissions=True)
                tdr.submit()
                tdr.start_deletion_tasks()
                frappe.db.commit()
                frappe.db.set_single_value("Global Defaults", "demo_company", "")
                frappe.delete_doc("Company", company, ignore_permissions=True)
                frappe.db.commit()
                res['success_key'] = 1
                res['message'] = "Demo company and transactional data deleted successfully."  
        except Exception as e:
                res['success_key'] = 0
                res['message'] = e 
        return res






