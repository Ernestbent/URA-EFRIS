import frappe

def alter_goods_details_schema():
    # Alter the 'name' column to VARCHAR(500)
    try:
        frappe.db.sql("""
            ALTER TABLE `tabGoods Details` 
            MODIFY COLUMN `name` VARCHAR(500);
        """)
        frappe.db.commit()  # Commit the changes
    except Exception as e:
        frappe.log_error(message=str(e), title="Schema Alteration Error")
