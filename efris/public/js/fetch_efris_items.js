frappe.ui.form.on('Item', {
    custom_add_product: function(frm) {
        if (frm.doc.custom_add_product) {
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Goods Details",
                    fieldname: "commodity_name",  // Fetch the commodity_name field
                    filters: { "name": frm.doc.custom_add_product }  // Use the custom_add_product value to fetch the document
                },
                callback: function(r) {
                    if (r.message) {
                        // Set the commodity_name in the item_name field
                        frm.set_value('item_name', r.message.commodity_name);
                    }
                }
            });
        }
    }
});
