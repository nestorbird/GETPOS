import frappe
from frappe import auth
from frappe import _
STANDARD_USERS = ("Guest", "Administrator")
from frappe.rate_limiter import rate_limit
from frappe.utils.password import update_password as _update_password, check_password, get_password_reset_limit
from frappe.utils import (cint, flt, has_gravatar, escape_html, format_datetime,
        now_datetime, get_formatted_email, today)

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
            "message":"Recheck the credentials and enter again to proceed"
        }

        return

    api_generate = generate_keys(frappe.session.user)
    user = frappe.get_doc('User', frappe.session.user)

    frappe.response["message"] = {
        "success_key":1,
        "message":"Authentication success",
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
        
# this is for forgot-password message
@frappe.whitelist( allow_guest=True )
def reset_password( user,send_email=False, password_expired=False):
                from frappe.utils import random_string, get_url

                key = random_string(32)
                # user.db_set("reset_password_key", key)

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











                 



		




       
       

    
  






   




