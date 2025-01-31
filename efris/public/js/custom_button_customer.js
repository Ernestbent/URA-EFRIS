frappe.ui.form.on('Customer', {
    refresh: function(frm) {
        // Add a custom button to fetch taxpayer information
        frm.add_custom_button(__('Get Taxpayer Information'), function() {
            // Call the server-side method for retrieving taxpayer info
            get_taxpayer_information(frm);
        }, __("EFRIS Actions"));
    }
});

// Function to call the server-side method for retrieving taxpayer info
function get_taxpayer_information(frm) {
    frappe.call({
        method: "efris.efris.custom_scripts.validate_tax_payer.make_api_call",  // Replace with the correct path to your Python method
        args: {
            doc: frm.doc.name  // Pass the document name to the server-side method
        },
        callback: function(response) {
            if (response.message.status === "success") {
                frappe.msgprint(__('Taxpayer information retrieved successfully.'));
            } else {
                frappe.msgprint(__('Failed to retrieve taxpayer information: ') + response.message.message);
            }
        }
    });
}
