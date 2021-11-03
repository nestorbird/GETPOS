import frappe
from frappe import auth
from frappe import _
from frappe.exceptions import Redirect
STANDARD_USERS = ("Guest", "Administrator")
from frappe.rate_limiter import rate_limit
from frappe.utils.password import update_password as _update_password, check_password, get_password_reset_limit
from frappe.utils import (cint, flt, has_gravatar, escape_html, format_datetime,
        now_datetime, get_formatted_email, today, add_days, cint)

# this is for login api
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


    api_generate = generate_keys(frappe.session.user)
    user = frappe.get_doc('User', frappe.session.user)

    frappe.response["message"] = {
        "success_key":1,
        "message":"success",
        "sid":frappe.session.sid,
        "api_key":user.api_key,
        "api_secret":api_generate,
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

    return api_secret
       

# this is email going for the password reset
@frappe.whitelist()
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
        
# this is for forgot-password message
@frappe.whitelist()
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

# this is your code
@frappe.whitelist(allow_guest=True)
def get_abbr(string):
    abbr = ''.join(c[0] for c in string.split()).upper()
    return abbr





# this id for terms and conditions api
@frappe.whitelist()
def terms_and_conditions():
        term = frappe.db.get_value("Terms and Conditions","Terms and Conditions for agribora","terms")
        return term

# this is for privacy policy api
@frappe.whitelist()
def privacy_policy():
        policy = frappe.db.get_value("Privacy Policy","Privacy Policy for agribora","privacy")
        return policy

#this is for customer list by hub manager
@frappe.whitelist()
def get_customer_list_by_hubmanager(hub_manager):
                return frappe.db.get_list('Customer',{'hub_manager': hub_manager},["customer_name","email_id","mobile_no","ward","name","creation"])
        
#this is for item list by hub manager
@frappe.whitelist()
def get_item_list_by_hubmanager(hub_manager):
        return frappe.db.sql("""select i.item_code,i.item_name,i.item_group,i.description,i.opening_stock,i.standard_rate,i.has_variants,i.variant_based_on,i.image from `tabItem` i JOIN `tabHub Manager Detail` h
                        ON h.parent = i.name and
                        h.parenttype = 'Item' and
                        h.hub_manager = %s""",hub_manager, as_dict=1)

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
        return sales_order

@frappe.whitelist()
def get_sales_order_list(hub_manager = None, page_no = 1):
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
        return order_list
