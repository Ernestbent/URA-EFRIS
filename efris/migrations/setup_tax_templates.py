import frappe

def create_item_tax_templates_and_accounts():
    # Fetch all companies
    companies = frappe.get_all("Company", fields=["name"])

    # Define tax types and rates
    tax_types = {
        "Standard": 0.18,
        "Zero": 0.0,
        "Exempt": None,  # None indicates exempt or no tax rate
        "Deemed": 0.18
    }

    # Iterate through the list of companies
    for company in companies:
        # Create Item Tax Templates
        for tax_type, tax_rate in tax_types.items():
            item_tax_template = frappe.get_doc({
                "doctype": "Item Tax Template",
                "title": f"{tax_type} Tax Template",
                "company": company["name"],
                "disabled": 0,
                "taxes": [
                    {
                        "tax_type": tax_type,
                        "tax_rate": tax_rate if tax_rate is not None else 0.0  # Handle exempt case
                    }
                ]
            })
            item_tax_template.insert(ignore_if_duplicate=True)
        
            # Create Accounting Accounts
            frappe.get_doc({
                "doctype": "Account",
                "name": tax_type,
                "company": company["name"],
                "is_group": 0,
                "root_type": "Liability",
                "report_type": "Balance Sheet",
                "account_currency": company.get("default_currency", "UGX"),
                "parent_account": "",
                "account_type": "Tax",
                "tax_rate": tax_rate if tax_rate is not None else 0.0,
                "freeze_account": 0
            }).insert(ignore_if_duplicate=True)

def after_install():
    # Run this function after installing the app
    create_item_tax_templates_and_accounts()
