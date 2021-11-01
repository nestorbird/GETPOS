from . import __version__ as app_version

app_name = "agribora"
app_title = "Agribora"
app_publisher = "www.nestorbird.com"
app_description = "data driven agribusiness"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@nestorbird.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/agribora/css/agribora.css"
# app_include_js = "/assets/agribora/js/agribora.js"

# include js, css files in header of web template
# web_include_css = "/assets/agribora/css/agribora.css"
# web_include_js = "/assets/agribora/js/agribora.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "agribora/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Sales Order" : "public/js/doctype_js/sales_order.js",
<<<<<<< HEAD

	"Account" : "public/js/doctype_js/account.js",

	"Warehouse" : "public/js/doctype_js/warehouse.js"

=======
	"Warehouse" : "public/js/doctype_js/warehouse.js",
	"Account" : "public/js/doctype_js/account.js"
>>>>>>> a429c1f7e4b44c1a9d3225c51ed6b36e6db91e6c
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "agribora.install.before_install"
# after_install = "agribora.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "agribora.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.eveprint(type(hub_manager))nt.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Warehouse": {
		"validate": "agribora.agribora.hooks.warehouse.validate_hub_manager"
	},
<<<<<<< HEAD
	"Sales Order": {
		"validate" : "agribora.agribora.hooks.sales_order.autoname"
	},
	"Customer" : {
		"validate" : "agribora.agribora.hooks.customer.validate"
=======
	"Sales Order":{
		"on_submit": "agribora.agribora.hooks.sales_order.on_submit",
		"validate": "agribora.agribora.hooks.sales_order.validate"
	},
	"Sales Invoice":{
		"on_submit": "agribora.agribora.hooks.sales_invoice.on_submit"
>>>>>>> a429c1f7e4b44c1a9d3225c51ed6b36e6db91e6c
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"agribora.tasks.all"
# 	],
# 	"daily": [
# 		"agribora.tasks.daily"
# 	],
# 	"hourly": [
# 		"agribora.tasks.hourly"
# 	],
# 	"weekly": [
# 		"agribora.tasks.weekly"
# 	]
# 	"monthly": [
# 		"agribora.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "agribora.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "agribora.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "agribora.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"agribora.auth.validate"
# ]

