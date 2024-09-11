import frappe

def create_item_tax_template_for_all_companies():
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

def after_install():
    create_item_tax_template_for_all_companies()
