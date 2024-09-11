import frappe

def create_or_update_accounts():
    # Define the base tax types and their properties
    base_tax_types = [
        {
            'name': 'VAT',
            'account_type': 'Tax',
            'root_type': 'Liability',
            'report_type': 'Balance Sheet',
            'tax_rate': 0.16
        },
        # Add more base tax types if needed
    ]
    
    # Fetch all companies
    companies = frappe.get_all('Company', fields=['name', 'abbr'])
    
    for company in companies:
        for base_tax_type in base_tax_types:
            # Create or update the Account for the tax type
            account_name = f"{base_tax_type['name']}-{company['abbr'].upper()}"
            existing_account = frappe.get_all('Account', filters={'name': account_name})
            
            if not existing_account:
                # Create a new Account for the tax type
                new_account = frappe.get_doc({
                    'doctype': 'Account',
                    'name': account_name,
                    'account_type': base_tax_type['account_type'],
                    'company': company['name'],
                    'root_type': base_tax_type['root_type'],
                    'report_type': base_tax_type['report_type'],
                    'tax_rate': base_tax_type['tax_rate'],
                    'account_currency': 'USD',  # Set default currency or as needed
                    'parent_account': None,     # Set parent account if required
                    'freeze_account': 0        # 0 means not frozen
                })
                new_account.insert()
                frappe.db.commit()

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
            # Retrieve the Account record for the tax type
            account_name = f"{template['taxes'][0]['tax_type']}-{company['abbr'].upper()}"
            account = frappe.get_all('Account', filters={'name': account_name})
            
            if not account:
                # Skip if the account doesn't exist
                continue

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
                            'tax_type': account_name,
                            'tax_rate': template['taxes'][0]['tax_rate']
                        }
                    ]
                })
                tax_template.insert()
                frappe.db.commit()
            else:
                # Update existing template with the new tax type
                for existing_template in existing_templates:
                    tax_template = frappe.get_doc('Item Tax Template', existing_template['name'])
                    tax_template.taxes = [
                        {
                            'tax_type': account_name,
                            'tax_rate': template['taxes'][0]['tax_rate']
                        }
                    ]
                    tax_template.save()
                    frappe.db.commit()

# Call the functions to create or update accounts and templates
create_or_update_accounts()
create_and_update_item_tax_templates()
