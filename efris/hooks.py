app_name = "efris"
app_title = "Efris"
app_publisher = "Ernest Benedict Othieno"
app_description = "Efris Customizations"
app_email = "benedict@tgs-osillo.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/efris/css/efris.css"
app_include_js = "/assets/efris/js/custom_button.js"
app_include_js = "/assets/efris/js/integration_request_widget.js"

# include js, css files in header of web template
# web_include_css = "/assets/efris/css/efris.css"
# web_include_js = "/assets/efris/js/efris.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "efris/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Item":"public/js/fetch_efris_items.js", 
    "Purchase Invoice":"public/js/filter_items_pi.js",
    "Sales Invoice":"public/js/filter_items_si.js",
    "Item":"public/js/toggle_excise_duty.js",
    "Stock Entry":"public/js/filter_items_stock.js",
    "Item":"public/js/toggle_excise_duty.js",
    "Sales Invoice":"public/js/credit_reason.js",
    "Item": "public/js/item_custom_button.js",  # JavaScript file for the Item doctype
    "Sales Order": "public/js/sales_order_custom_button.js",  # Example for another doctype
    # Add more as needed for other doctypes
}
# doctype_js = {"doctype" : "public/js/custom_button.js"}
# doctype_js = {"doctype" : "public/js/item_custom_button.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "efris/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {                                                                                                                                 
# 	"methods": "efris.utils.jinja_methods",
# 	"filters": "efris.utils.jinja_filters"
# }

# Installation
# ------------

after_install = "efris.migrations.alter_goods_details.alter_goods_details_schema"
# after_install = [
#     "efris.migrations.setup_tax_templates.create_or_update_accounts",
#     "efris.migrations.setup_tax_templates.create_and_update_item_tax_templates"
# ]
# after_install ="efris.migrations.setup_tax_templates"
# after_install = "efris.migrations.setup_tax_templates.create_item_tax_templates_and_accounts"

# Uninstallation
# ------------

# before_uninstall = "efris.uninstall.before_uninstall"
# after_uninstall = "efris.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "efris.utils.before_app_install"
# after_app_install = "efris.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "efris.utils.before_app_uninstall"
# after_app_uninstall = "efris.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "efris.notifications.get_notification_config"

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
	"TaxPayer Information":{
        "on_submit":"efris.efris.custom_scripts.taxquery.query_tax_payer"
    },
    "Customer":{
        "on_update":"efris.efris.custom_scripts.taxquery.query_tax_payer"
    },
    "Item":{
        "validate":"efris.efris.custom_scripts.item_add.on_save"
    },
    "Purchase Invoice":{
        "on_submit":"efris.efris.custom_scripts.stock_in.on_stock"
    },
    "Sales Invoice":{
        "on_submit":["efris.efris.custom_scripts.sales_invoice.on_send"],
        "on_cancel":["efris.efris.custom_scripts.credit_note_cancel.on_cancel"]
    },
    "Query Invoice Details":{
        "validate":"efris.efris.doctype.query_invoice_details.query_invoice.query_invoice_information"
    },
    "Stock Entry":{
        "on_submit":"efris.efris.custom_scripts.stock_adjustment.stock_adjust"
    },
    "Tax Payer Status":{
        "validate":"efris.efris.custom_scripts.check_vat_status.taxpayer_status"
    },
    
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#     "cron": {
#         "*/10 * * * *": [
#             "efris.exchange_rates.get_exchange_rates"
#         ]
#     }
# }


# Testing
# -------

# before_tests = "efris.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "efris.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "efris.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["efris.utils.before_request"]
# after_request = ["efris.utils.after_request"]

# Job Events
# ----------
# before_job = ["efris.utils.before_job"]
# after_job = ["efris.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"efris.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# 
  