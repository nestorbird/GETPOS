import frappe
from frappe import auth
from frappe import _
from frappe.exceptions import Redirect
STANDARD_USERS = ("Guest", "Administrator")
from frappe.rate_limiter import rate_limit
from frappe.utils.password import update_password as _update_password, check_password, get_password_reset_limit
from frappe.utils import (cint, flt, has_gravatar, escape_html, format_datetime,
        now_datetime, get_formatted_email, today, add_days, nowdate, nowtime)
from erpnext.accounts.utils import get_balance_on
from erpnext.stock.utils import get_stock_balance
from erpnext.stock.stock_ledger import get_previous_sle, get_stock_ledger_entries


@frappe.whitelist( allow_guest=True )
def login(usr, pwd):
    try:
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(user=usr, pwd=pwd)
        login_manager.post_login()
    except frappe.exceptions.AuthenticationError:
        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success_key":0,
            "message":"Incorrect Username or Password"
        }
        
        return



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


def generate_keys(user):
    user_details = frappe.get_doc('User', user)
    api_secret = frappe.generate_hash(length=15)

    if not user_details.api_key:
        api_key = frappe.generate_hash(length=15)
        user_details.api_key = api_key

    user_details.api_secret = api_secret
    user_details.save()
    return api_secret, user_details.api_key
       


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
        base_url = frappe.db.get_single_value('Agribora Setting', 'base_url')
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
        base_url = frappe.db.get_single_value('Agribora Setting', 'base_url')
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
                base_url = frappe.db.get_single_value('Agribora Setting', 'base_url')
                filters = {'hub_manager': hub_manager, "base_url": base_url}
                conditions = "hub_manager = %(hub_manager)s "
                hub_manager_detail = frappe.db.sql("""
                        SELECT
                                u.name, u.full_name,
                                u.email, u.mobile_no,
                                h.hub_manager, h.series,
                                if((u.user_image = null or u.user_image = ''), null, 
                                if(u.user_image LIKE 'http%%', u.user_image, concat(%(base_url)s, u.user_image))) as image
                        FROM `tabUser` u, `tabHub Manager` h
                        WHERE h.hub_manager = u.name and
                        {conditions}
                        """.format(conditions=conditions), values=filters, as_dict=1)
                cash_balance = get_balance(hub_manager)
                wards = frappe.db.sql("""
                SELECT
                        ward, is_assigned
                FROM `tabWard Detail`
                WHERE parent = %s
                and parenttype = 'Hub Manager'
        """,hub_manager, as_dict=1)

                res["success_key"] = 1
                res["message"] = "success" 
                res["name"] = hub_manager_detail[0]["name"]
                res["full_name"] = hub_manager_detail[0]["full_name"]
                res["email"] = hub_manager_detail[0]["email"]
                res["mobile_no"] = hub_manager_detail[0]["mobile_no"]
                res["hub_manager"] = hub_manager_detail[0]["hub_manager"]
                res["series"] = hub_manager_detail[0]["series"]
                res["image"] = hub_manager_detail[0]["image"]
                res["balance"] = cash_balance
                res["last_transaction_date"] = get_last_transaction_date(hub_manager)
                res["wards"] = wards
                return res
        except Exception as e:
                print(frappe.get_traceback())
                frappe.clear_messages()
                frappe.local.response["message"] = {
                        "success_key":0,
                        "message":"No values found for this hub manager"
                }

@frappe.whitelist()
def get_balance(hub_manager):
        account = frappe.db.get_value('Account', {'hub_manager': hub_manager}, 'name')
        account_balance = get_balance_on(account)
        return account_balance

@frappe.whitelist()
def create_sales_order(order_list = {}):
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
                for item in order_list.get("items"):
                        sales_order.append("items", {
                                "item_code": item.get("item_code"),
                                "qty": item.get("qty"),
                                "rate": item.get("rate")
                        })
                sales_order.status = order_list.get("status")
                sales_order.mode_of_payment = order_list.get("mode_of_payment")
                sales_order.mpesa_no = order_list.get("mpesa_no")
                sales_order.save()
                sales_order.submit()
                frappe.db.commit()
                res['success_key'] = 1
                res['message'] = "success"
                res["sales_order"] ={"name" : sales_order.name,
                 "doc_status" : sales_order.docstatus}
                return res
        except Exception as e:
             frappe.clear_messages()
             del frappe.local.response["exc_type"]
             frappe.local.response["message"] ={
                "success_key":0,
                "message":"Invalid values please check your request parameters"
        }


@frappe.whitelist()
def get_sales_order_list(hub_manager = None, page_no = 1, from_date = None, to_date = nowdate()):
        res= frappe._dict()
        base_url = frappe.db.get_single_value('Agribora Setting', 'base_url')
        filters = {'hub_manager': hub_manager, 'from_date': from_date, 'to_date': to_date, 'base_url': base_url}
        sales_history_count = frappe.db.get_single_value('Agribora Setting', 'sales_history_count')
        limit = cint(sales_history_count)
        if from_date:
                conditions = " and s.transaction_date between %(from_date)s and %(to_date)s order by s.creation desc"
        else:
                if page_no == 1:
                        row_no = 0
                        conditions = " order by s.creation desc limit %(row_no)s , %(limit)s"
                else:
                        page_no = cint(page_no) - 1
                        row_no = cint(page_no * cint(sales_history_count))
                        conditions = " order by s.creation desc limit %(row_no)s , %(limit)s"
                filters['limit'] = cint(limit)
                filters['row_no'] = cint(row_no)        
        order_list = frappe.db.sql("""
                SELECT 
                        s.name, s.transaction_date, s.transaction_time, s.ward, s.customer,s.customer_name, 
                        s.ward, s.hub_manager, s.grand_total, s.mode_of_payment, 
                        s.mpesa_no, s.contact_display as contact_name,
                        s.contact_phone, s.contact_mobile, s.contact_email,
                        s.hub_manager, s.creation,
                        u.full_name as hub_manager_name,
                        if((c.image = null or c.image = ''), null, 
                        if(c.image LIKE 'http%%', c.image, concat(%(base_url)s, c.image))) as image
                FROM `tabSales Order` s, `tabUser` u, `tabCustomer` c
                WHERE s.hub_manager = u.name and s.customer = c.name 
                        and s.hub_manager = %(hub_manager)s and s.docstatus = 1 
                        {conditions}
        """.format(conditions=conditions), values = filters, as_dict= True)
        for item in order_list:
                item_details = frappe.db.sql("""
                        SELECT
                                so.item_code, so.item_name, so.qty, 
                                so.uom, so.rate, so.amount,
                                if((i.image = null or i.image = ''), null, 
                                if(i.image LIKE 'http%%', i.image, concat(%s, i.image))) as image
                        FROM `tabSales Order Item` so, `tabSales Order` s, `tabItem` i
                        WHERE so.parent = s.name and so.item_code = i.item_code 
                                and so.parent = %s and so.parenttype = 'Sales Order' 
                """, (base_url,item.name), as_dict = True)
                item['items'] = item_details
        if from_date:
                number_of_orders = len(order_list)
        else:
                number_of_orders = get_sales_order_count(hub_manager)

        if len(order_list) == 0 and number_of_orders == 0:
                frappe.clear_messages()
                frappe.local.response["message"] = {
                        "success_key":1,
                        "message":"no values found for this hub manager"
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
