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

                return frappe.msgprint(_("Password reset instructions have been sent to your email"))

        except frappe.DoesNotExistError:
                frappe.clear_messages()
                return 'not found'
        

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
def privacy_policy():
        privacy_policy = frappe.db.sql("""
                SELECT privacy_policy
                FROM `tabPrivacy Policy`
                WHERE disabled = 0
        """)[0][0]
        return privacy_policy
        
@frappe.whitelist()
def get_customer_list_by_hubmanager(hub_manager, last_sync = None):
        filters = {'hub_manager': hub_manager}
        if last_sync:
                filters['modified'] = [">=", last_sync]
        return frappe.db.get_list('Customer',
                filters = filters,
                fields = ["customer_name","email_id","mobile_no","ward","name","creation"])
        

@frappe.whitelist()
def get_item_list_by_hubmanager(hub_manager, last_sync = None):
        base_url = frappe.db.get_single_value('Agribora Setting', 'base_url')
        filters = {'hub_manager': hub_manager, "base_url": base_url}
        conditions = "h.hub_manager = %(hub_manager)s "
        if last_sync:
                filters['last_sync'] = last_sync
                conditions += "and (i.modified >= %(last_sync)s or p.modified >= %(last_sync)s)"

        return frappe.db.sql("""
                SELECT 
                        i.item_code, i.item_name, i.item_group, i.description,
                        i.has_variants, i.variant_based_on,
                        if(i.image = null, null, concat(%(base_url)s, i.image)) as image, p.price_list_rate
                FROM `tabItem` i, `tabHub Manager Detail` h,`tabItem Price` p
                WHERE   h.parent = i.name and h.parenttype = 'Item' 
                        and p.item_code = i.name and p.selling =1
                        and p.price_list_rate > 0 
                        and {conditions}
                        """.format(conditions=conditions), values=filters, as_dict=1)

@frappe.whitelist()
def get_details_by_hubmanager(hub_manager):
        hub_manager_detail = frappe.db.sql("""
                        SELECT
                                u.name, u.full_name,
                                u.email, u.mobile_no,
                                h.hub_manager, h.series
                        FROM `tabUser` u, `tabHub Manager` h
                        WHERE h.hub_manager = u.name and
                        h.hub_manager = %s
                        """,hub_manager, as_dict=1)
        cash_balance = get_balance(hub_manager)
        hub_manager_detail[0]['balance']  = cash_balance
        hub_manager_detail[0]['last_transaction_date']  = get_last_transaction_date(hub_manager)
        return hub_manager_detail

@frappe.whitelist()
def get_balance(hub_manager):

        account = frappe.db.get_value('Account', {'hub_manager': hub_manager}, 'name')
        account_balance = get_balance_on(account)
        return account_balance

@frappe.whitelist()
def create_sales_order(order_list = {}):
        sales_order = frappe.new_doc("Sales Order")
        sales_order.hub_manager = order_list.get("hub_manager")
        sales_order.ward = order_list.get("ward")
        sales_order.customer = order_list.get("customer")
        sales_order.transaction_date = order_list.get("transaction_date")
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
        res= frappe._dict()
        res['name'] = sales_order.name
        res['docstatus'] = sales_order.docstatus
        return res

@frappe.whitelist()
def get_sales_order_list(hub_manager = None, page_no = 1):
        sales_order_history= frappe._dict()
        sales_history_count = frappe.db.get_single_value('Agribora Setting', 'sales_history_count')
        limit = cint(sales_history_count)
        if page_no == 1:
                row_no = 0
        else:
                page_no = cint(page_no) - 1
                row_no = cint(page_no * cint(sales_history_count))

        filters = { 'hub_manager': hub_manager, 'limit': cint(limit), 'row_no': cint(row_no)}
        order_list = frappe.db.sql("""
                SELECT 
                        s.name, s.transaction_date, s.ward, s.customer,s.customer_name, 
                        s.ward, s.hub_manager, s.grand_total, s.mode_of_payment, 
                        s.mpesa_no, s.contact_display as contact_name,
                        s.contact_phone, s.contact_mobile, s.contact_email,
                        s.hub_manager, s.creation,
                        u.full_name as hub_manager_name
                FROM `tabSales Order` s, `tabUser` u
                WHERE s.hub_manager = u.name and s.hub_manager = %(hub_manager)s
                        and s.docstatus = 1 
                        order by s.creation desc limit %(row_no)s , %(limit)s
        """, values = filters, as_dict= True)
        for item in order_list:
                item_details = frappe.db.sql("""
                        SELECT
                                so.item_code, so.item_name, so.qty, 
                                so.uom, so.rate, so.amount
                        FROM `tabSales Order Item` so, `tabSales Order` s
                        WHERE so.parent = s.name and so.parent = %s and
                                so.parenttype = 'Sales Order' 
                """, (item.name), as_dict = True)
                item['items'] = item_details
        number_of_orders = get_sales_order_count(hub_manager)
        sales_order_history['order_list'] = order_list
        sales_order_history['number_of_orders'] = number_of_orders
        return sales_order_history

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
        )[0][0]
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
                        res['available_qty'] = "no updated stock"
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