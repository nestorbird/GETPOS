import frappe 
from frappe import _
import random
import string
from frappe import STANDARD_USERS
from datetime import datetime
import frappe.exceptions
from passlib.context import CryptContext
from frappe.core.doctype.user.user import check_password
from frappe.core.doctype.user.user import User
from frappe.query_builder import Table
from frappe.utils import (
	now_datetime,
    get_formatted_email
)
from frappe.utils import get_url


Auth = Table("__Auth")
passlibctx = CryptContext(
	schemes=[
		"pbkdf2_sha256",
		"argon2",
	],
)

from frappe.core.doctype.user.user import check_password

def custom_send_login_mail(self, subject, template, add_args, now=None, custom_template=None):
    from frappe.utils.user import get_user_fullname
    from frappe.utils import cstr

    created_by = get_user_fullname(frappe.session["user"])
    if created_by == "Guest":
        created_by = "Administrator"

    pwd = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=6))
    update_password(self.name, pwd=pwd, doctype="User", fieldname="password", logout_all_sessions=False)
    
    args = {
        "first_name": self.first_name or self.last_name or "user",
        "user_id": self.name,
        "title": subject,
        "password": pwd,
        "created_by": created_by,
    }

    args.update(add_args)

    sender = (
        frappe.session.user not in STANDARD_USERS and get_formatted_email(frappe.session.user) or None
    )

    if custom_template:
        from frappe.email.doctype.email_template.email_template import get_email_template

        email_template = get_email_template(custom_template, args)
        subject = email_template.get("subject")
        content = email_template.get("message")
    
    url = get_url()
    
    message = f'''
        Hello {cstr(self.first_name) or "user"},<br><br>
        You have received an invitation to join as a Merchant user on the Platform.<br>
        To get started, please click on the link: <a href="{url}">{url}</a> to activate your account and create your password.<br><br>
        We have shared the temporary password, kindly change your password after login.<br><br>
        <b>User Id:</b> {cstr(self.name)}<br>
        <b>Password:</b> {pwd}<br><br>
        If you did not make this request, please ignore this email. No changes will be made to your account.<br><br>
        Thanks,<br>
        {cstr(created_by)}
    '''

    frappe.sendmail(
        recipients=[self.email],
        subject="Welcome to Kleo Cloud",
        message=message,
        delayed=False,
        header=["Welcome to Kleo Cloud"]
    )



def update_password(user, pwd, doctype="User", fieldname="password", logout_all_sessions=False):
    try:
        hashPwd = passlibctx.hash(pwd)

        query = (
            frappe.qb.into(Auth)
            .columns(Auth.doctype, Auth.name, Auth.fieldname, Auth.password, Auth.encrypted)
            .insert(doctype, user, fieldname, hashPwd, 0)
        )

        # TODO: Simplify this via aliasing methods in `frappe.qb`
        if frappe.db.db_type == "mariadb":
            query = query.on_duplicate_key_update(Auth.password, hashPwd).on_duplicate_key_update(
                Auth.encrypted, 0
            )
        elif frappe.db.db_type == "postgres":
            query = (
                query.on_conflict(Auth.doctype, Auth.name, Auth.fieldname)
                .do_update(Auth.password, hashPwd)
                .do_update(Auth.encrypted, 0)
            )

        query.run()
        frappe.local.response["message"] ={
            "success_key":1,
            "message":"New Password has been Set"
            } 
        frappe.local.response["http_status_code"] = 200

    except Exception as e:
        frappe.clear_messages()
        frappe.log_error(f"Error while updating Password: {str(e)}")
        frappe.local.response["message"] = {
            "success_key": 0,
            "message": "Error while updating Password"
        }
        frappe.local.response["http_status_code"] = 403 