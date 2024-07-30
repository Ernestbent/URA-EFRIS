frappe.ui.form.on('Item', {
    refresh: function(frm) {
        // Only add the custom buttons if the document is not new
        if (!frm.is_new()) {
            // Add a custom button for querying stock
            frm.add_custom_button(__('Query Stock'), function() {
                frappe.call({
                    method: "efris.efris.custom_scripts.item_add.query_stock",
                    args: {
                        item_code: frm.doc.item_code  // Pass item code to backend function
                    },
                    callback: function(response) {
                        if (response.message.status === "success") {
                            frappe.msgprint(`Stock Quantity for ${frm.doc.item_code}: ${response.message.quantity}`);
                        } else {
                            frappe.msgprint(`Failed to query stock: ${response.message.error}`);
                        }
                    }
                });
            }, __("Configure Product")); // Add this button to the "Configure Product" group
        }
    }
});
