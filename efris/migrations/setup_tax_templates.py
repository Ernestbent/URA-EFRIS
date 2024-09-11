import frappe

def create_and_update_item_tax_templates():
    # Define the generic tax templates
    tax_templates = [
        {
            'title': 'Standard Tax Template',
            'taxes': [
                {
                    'tax_type': 'VAT',  # Base tax type
                    'tax_rate': 0.16
                }
            ]
        },
        # Add more templates as needed
    ]
    
    # Fetch all companies
    companies = frappe.get_all('Company', fields=['name', 'abbr'])

    for company in companies:
        for template in tax_templates:
            # Check if the generic template already exists for this company
            existing_templates = frappe.get_all('Item Tax Template', filters={'title': template['title'], 'company': company['name']})
            
            if not existing_templates:
                # Create a new Item Tax Template
                tax_template = frappe.get_doc({
                    'doctype': 'Item Tax Template',
                    'title': template['title'],
                    'company': company['name'],
                    'taxes': [
                        {
                            'tax_type': f"{template['taxes'][0]['tax_type']}-{company['abbr'].upper()}",
                            'tax_rate': template['taxes'][0]['tax_rate']
                        }
                    ]
                })
                tax_template.insert()
                frappe.db.commit()
            else:
                # Update existing template with company-specific tax type
                for existing_template in existing_templates:
                    tax_template = frappe.get_doc('Item Tax Template', existing_template['name'])
                    tax_template.taxes = [
                        {
                            'tax_type': f"{template['taxes'][0]['tax_type']}-{company['abbr'].upper()}",
                            'tax_rate': template['taxes'][0]['tax_rate']
                        }
                    ]
                    tax_template.save()
                    frappe.db.commit()

# Call the function to create or update templates
create_and_update_item_tax_templates()
