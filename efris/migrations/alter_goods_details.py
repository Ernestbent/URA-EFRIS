import frappe

def alter_goods_details_schema():
    try:
        # Alter the 'name' column in the 'Goods Details' table
        frappe.db.sql("""
            ALTER TABLE `tabGoods Details` 
            MODIFY COLUMN `name` VARCHAR(500);
        """)
        
        # Alter the 'deleted_name' column in the 'Deleted Document' table
        frappe.db.sql("""
            ALTER TABLE `tabDeleted Document` 
            MODIFY COLUMN `deleted_name` VARCHAR(500);
        """)
        
        # Commit the changes
        frappe.db.commit()
        
    except Exception as e:
        # Log any errors encountered during the schema alteration
        frappe.log_error(message=str(e), title="Schema Alteration Error")

