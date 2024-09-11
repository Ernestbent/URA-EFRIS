import frappe

def create_tax_types():
    tax_types = [
        {"name": "Standard", "tax_type": "Standard", "tax_rate": 0.18},
        {"name": "Zero", "tax_type": "Zero", "tax_rate": 0.00},
        {"name": "Exempt", "tax_type": "Exempt", "tax_rate": None},
        {"name": "Deemed", "tax_type": "Deemed", "tax_rate": 0.18}
    ]

    for tax in tax_types:
        if not frappe.db.exists("Tax", {"name": tax["name"]}):
            tax_doc = frappe.get_doc({
                "doctype": "Tax",
                "title": tax["name"],
                "tax_type": tax["tax_type"],
                "tax_rate": tax["tax_rate"]
            })
            tax_doc.insert(ignore_if_duplicate=True)
            
def create_item_tax_templates_and_accounts():
    create_tax_types()  # Ensure tax types exist before creating tax templates
    
    # Define your tax templates and companies
    tax_templates = [
        {"title": "Standard", "tax_type": "Standard", "tax_rate": 0.18},
        {"title": "Zero", "tax_type": "Zero", "tax_rate": 0.00},
        {"title": "Exempt", "tax_type": "Exempt", "tax_rate": None},
        {"title": "Deemed", "tax_type": "Deemed", "tax_rate": 0.18}
    ]
    
    companies = frappe.get_all("Company", fields=["name"])
    
    for company in companies:
        for template in tax_templates:
            item_tax_template = frappe.get_doc({
                "doctype": "Item Tax Template",
                "title": f"{template['title']} Tax Template",
                "company": company["name"],
                "disabled": 0,
                "taxes": [
                    {
                        "tax_type": template["tax_type"],
                        "tax_rate": template["tax_rate"]
                    }
                ]
            })
            item_tax_template.insert(ignore_if_duplicate=True)

# Call this function in your migration script
def after_install():
    create_item_tax_templates_and_accounts()
