from . import __version__ as app_version

app_name = "nbpos"
app_title = "nbpos"
app_publisher = "swapnil"
app_description = "nbpos"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "swapnil.pawar"
app_license = "MIT"

# Includes in <head>
# ------------------

fixtures = [
	{
		"doctype": "Custom Field",
		"filters": {
			"name": (
				"in",
				(
					"Sales Order Item-associated_item",
				)
			)
		}
	},
		{
		"doctype": "Print Format",
		"filters": {
			"name": (
				"in",
				(
					"POS Print",
					"GET POS Invoice"
				)
			)
		}
	},
]
# include js, css files in header of desk.html
# app_include_css = "/assets/nbpos/css/nbpos.css"
app_include_js = "/assets/nbpos/js/nbpos.js"

# include js, css files in header of web template
# web_include_css = "/assets/nbpos/css/nbpos.css"
# web_include_js = "/assets/nbpos/js/nbpos.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "nbpos/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_js = {
	"Sales Order" : "public/js/doctype_js/sales_order.js",
	"Warehouse": "public/js/doctype_js/warehouse.js",
	"Account": "public/js/doctype_js/account.js",
	"Customer": "public/js/doctype_js/customer.js",
	"Item": "public/js/doctype_js/item.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------
home_page = "getpos"


# application home page (will override Website Settings)
# home_page = "/app/point-of-sale"

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

# before_install = "nbpos.install.before_install"
# after_install = "nbpos.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "nbpos.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
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
		"validate": "nbpos.nbpos.hooks.warehouse.validate_hub_manager"
	},
	"Customer" : {
		"validate" : "nbpos.nbpos.hooks.customer.validate"
	},
	"Sales Order":{
		"on_submit": "nbpos.nbpos.hooks.sales_order.on_submit",
		"validate": "nbpos.nbpos.hooks.sales_order.validate"
	},
	"Sales Invoice":{
		"on_submit": "nbpos.nbpos.hooks.sales_invoice.on_submit"

	},
	"Item Price":{
		"validate": "nbpos.nbpos.hooks.item_price.validate_item_price"
	}
	
}
# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"nbpos.tasks.all"
# 	],
# 	"daily": [
# 		"nbpos.tasks.daily"
# 	],
# 	"hourly": [
# 		"nbpos.tasks.hourly"
# 	],
# 	"weekly": [
# 		"nbpos.tasks.weekly"
# 	]
# 	"monthly": [
# 		"nbpos.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "nbpos.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "nbpos.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "nbpos.task.get_dashboard_data"
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
# 	"nbpos.auth.validate"
# ]

